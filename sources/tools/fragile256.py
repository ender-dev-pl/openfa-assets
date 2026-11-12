"""Convert Fragile Allegiance PICTURE .256 assets to and from PNG."""

from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image


FILE_MAGIC = b"GRAPHICS"
PICTURE_MAGIC = b"PICTURE "
PALETTE_MAGIC = b"PALETTE "
GLOBAL_HEADER_SIZE = 32
PICTURE_HEADER_SIZE = 16
PALETTE_HEADER_SIZE = 32
PALETTE_SIZE = 256 * 3
SPRITES_MAGIC = b"SPRITES "


class FormatError(ValueError):
    """Raised when a file is not a supported Fragile Allegiance image."""


@dataclass(frozen=True)
class SpriteFrame:
    index: int
    canvas_width: int
    canvas_height: int
    x: int
    y: int
    width: int
    height: int
    stream_offset: int
    stream_length: int


@dataclass(frozen=True)
class ArchiveEntry:
    """One sequential payload stored in an extensionless Fragile archive."""

    index: int
    name: str
    offset: int
    length: int


def read_picture(path: Path) -> tuple[bytearray, int, int, int, int]:
    data = bytearray(path.read_bytes())
    if len(data) < GLOBAL_HEADER_SIZE + PICTURE_HEADER_SIZE + PALETTE_HEADER_SIZE:
        raise FormatError("file is too small")
    if data[:8] != FILE_MAGIC:
        raise FormatError("missing GRAPHICS signature")
    if data[GLOBAL_HEADER_SIZE : GLOBAL_HEADER_SIZE + 8] != PICTURE_MAGIC:
        raise FormatError(
            "only PICTURE assets are supported; SPRITES assets require a separate decoder"
        )

    width, height = struct.unpack_from("<HH", data, GLOBAL_HEADER_SIZE + 12)
    if not width or not height:
        raise FormatError("invalid image dimensions")

    pixels_offset = GLOBAL_HEADER_SIZE + PICTURE_HEADER_SIZE
    pixels_size = width * height
    palette_offset = pixels_offset + pixels_size
    expected_size = palette_offset + PALETTE_HEADER_SIZE + PALETTE_SIZE
    if len(data) != expected_size:
        raise FormatError(
            f"unexpected file size: expected {expected_size} bytes for {width}x{height}, "
            f"got {len(data)}"
        )
    if data[palette_offset : palette_offset + 8] != PALETTE_MAGIC:
        raise FormatError("missing PALETTE block")

    return data, width, height, pixels_offset, palette_offset


def palette_to_png(palette: bytes) -> bytes:
    """Expand the 6-bit VGA DAC values stored in a Fragile palette."""
    return bytes(((value & 0x3F) * 255 + 31) // 63 for value in palette)


def palette_from_png(palette: bytes, original_palette: bytes) -> bytes:
    """Reduce PNG channels to VGA DAC values while preserving palette flags."""
    return bytes(
        (original & 0xC0) | ((value * 63 + 127) // 255)
        for value, original in zip(palette, original_palette)
    )


def find_palette(data: bytes, start: int) -> tuple[int | None, bytes | None]:
    palette_offset = data.find(PALETTE_MAGIC, start)
    if palette_offset < 0:
        return None, None
    palette_start = palette_offset + PALETTE_HEADER_SIZE
    if palette_start + PALETTE_SIZE != len(data):
        return None, None
    return palette_offset, data[palette_start : palette_start + PALETTE_SIZE]


def fallback_palette(path: Path) -> tuple[bytes, str]:
    for candidate in sorted(path.parent.glob("*.256")):
        if candidate == path:
            continue
        data = candidate.read_bytes()
        _, palette = find_palette(data, GLOBAL_HEADER_SIZE)
        if palette is not None:
            return palette, candidate.name
    return bytes(value for value in range(256) for _ in range(3)), "grayscale"


def read_sprites(path: Path) -> tuple[bytes, list[SpriteFrame], bytes, str]:
    data = path.read_bytes()
    if len(data) < 48 or data[:8] != FILE_MAGIC:
        raise FormatError("missing GRAPHICS signature")
    if data[GLOBAL_HEADER_SIZE : GLOBAL_HEADER_SIZE + 8] != SPRITES_MAGIC:
        raise FormatError("missing SPRITES signature")

    frame_count = struct.unpack_from("<H", data, 40)[0]
    table_end = 48 + frame_count * 16
    if table_end > len(data):
        raise FormatError("truncated sprite table")

    palette_offset, palette = find_palette(data, table_end)

    offsets: list[int] = []
    entries: list[tuple[int, int, int, int, int, int]] = []
    for index in range(frame_count):
        entry_offset = 48 + index * 16
        canvas_width, canvas_height, x, y, width, height, offset = struct.unpack_from(
            "<6HI", data, entry_offset
        )
        empty = width == 0 and height == 0
        if (
            not canvas_width
            or not canvas_height
            or (width == 0) != (height == 0)
            or (not empty and (x + width > canvas_width or y + height > canvas_height))
        ):
            raise FormatError(f"invalid geometry in sprite {index}")
        offsets.append(GLOBAL_HEADER_SIZE + offset)
        entries.append((canvas_width, canvas_height, x, y, width, height))

    if palette_offset is not None:
        data_end = palette_offset
    else:
        data_end = GLOBAL_HEADER_SIZE + struct.unpack_from("<I", data, 12)[0]
    if data_end < table_end or data_end > len(data):
        raise FormatError("invalid sprite data boundary")

    frames: list[SpriteFrame] = []
    for index, (offset, entry) in enumerate(zip(offsets, entries)):
        next_offset = offsets[index + 1] if index + 1 < len(offsets) else data_end
        if offset < table_end or next_offset < offset or next_offset > data_end:
            raise FormatError(f"invalid data offsets in sprite {index}")
        frames.append(SpriteFrame(index, *entry, offset - GLOBAL_HEADER_SIZE, next_offset - offset))

    if palette is None:
        palette, palette_source = fallback_palette(path)
    else:
        palette_source = path.name
    return data, frames, palette, palette_source


def decode_sprite(stream: bytes, width: int, height: int) -> bytes:
    pixels = bytearray(width * height)
    cursor = 0
    for y in range(height):
        x = 0
        while True:
            if cursor + 2 > len(stream):
                raise FormatError(f"truncated RLE data in row {y}")
            skip, count = stream[cursor], stream[cursor + 1]
            cursor += 2
            if skip == 0 and count == 0:
                break
            x += skip
            if x + count > width or cursor + count > len(stream):
                raise FormatError(f"invalid RLE span in row {y}")
            row_start = y * width + x
            pixels[row_start : row_start + count] = stream[cursor : cursor + count]
            cursor += count
            x += count
    return bytes(pixels)


def export_sprites(source: Path, destination: Path) -> None:
    data, frames, palette, palette_source = read_sprites(source)
    output_directory = destination / source.stem
    output_directory.mkdir(parents=True, exist_ok=True)
    png_palette = palette_to_png(palette)
    frame_metadata = []

    for frame in frames:
        stream_start = GLOBAL_HEADER_SIZE + frame.stream_offset
        stream = data[stream_start : stream_start + frame.stream_length]
        cropped = (
            decode_sprite(stream, frame.width, frame.height)
            if frame.width and frame.height
            else b""
        )
        canvas = bytearray(frame.canvas_width * frame.canvas_height)
        for row in range(frame.height):
            source_start = row * frame.width
            target_start = (frame.y + row) * frame.canvas_width + frame.x
            canvas[target_start : target_start + frame.width] = cropped[
                source_start : source_start + frame.width
            ]

        image = Image.frombytes("P", (frame.canvas_width, frame.canvas_height), bytes(canvas))
        image.putpalette(png_palette, rawmode="RGB")
        png_name = f"{frame.index:03}.png"
        image.save(output_directory / png_name, format="PNG", bits=8, transparency=0)
        metadata = asdict(frame)
        metadata["png"] = f"{source.stem}/{png_name}"
        frame_metadata.append(metadata)

    metadata = {
        "format": "fragile-allegiance-sprites",
        "version": 1,
        "source": source.name,
        "palette": {
            "embedded": palette_source == source.name,
            "preview_source": palette_source,
            "encoding": "6-bit VGA DAC values with preserved flag bits",
        },
        "frames": frame_metadata,
    }
    manifest = destination / f"{source.stem}.json"
    manifest.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def export_png(source: Path, destination: Path) -> None:
    data, width, height, pixels_offset, palette_offset = read_picture(source)
    pixels = bytes(data[pixels_offset:palette_offset])
    palette_start = palette_offset + PALETTE_HEADER_SIZE
    palette = palette_to_png(bytes(data[palette_start : palette_start + PALETTE_SIZE]))

    image = Image.frombytes("P", (width, height), pixels)
    image.putpalette(palette, rawmode="RGB")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG", bits=8, optimize=False)


def read_archive(path: Path) -> tuple[str, bytes, list[ArchiveEntry]]:
    """Read the table of an extensionless graphics archive without extracting it."""
    data = path.read_bytes()
    header_size = 24
    entry_size = 24
    entry_name_size = 16
    if len(data) < header_size:
        raise FormatError("archive is shorter than its header")

    archive_name = data[:20].split(b"\0", 1)[0].decode("ascii")
    if not archive_name:
        raise FormatError("archive has no name")
    table_end = struct.unpack_from("<I", data, 20)[0]
    if table_end < header_size or table_end > len(data) or (table_end - header_size) % entry_size:
        raise FormatError("archive has an invalid entry table")

    entries: list[ArchiveEntry] = []
    expected_offset = table_end
    names: set[str] = set()
    output_stems: set[str] = set()
    for index, table_offset in enumerate(range(header_size, table_end, entry_size)):
        name = data[table_offset : table_offset + entry_name_size].split(b"\0", 1)[0].decode("ascii")
        offset, length = struct.unpack_from("<II", data, table_offset + entry_name_size)
        if (
            not name
            or name in {".", ".."}
            or "/" in name
            or "\\" in name
            or ":" in name
            or Path(name).is_absolute()
            or Path(name).is_reserved()
            or name.rstrip(" .") != name
            or any(ord(character) < 32 or ord(character) == 127 for character in name)
        ):
            raise FormatError(f"archive entry {index} has an unsafe name")
        stem = Path(name).stem.casefold()
        if name.casefold() in names or stem in output_stems or stem == "archive":
            raise FormatError(f"archive entry {index} has an invalid name")
        if offset != expected_offset or offset > len(data) or length > len(data) - offset:
            raise FormatError(f"archive entry '{name}' has an invalid payload range")
        entries.append(ArchiveEntry(index, name, offset, length))
        names.add(name.casefold())
        output_stems.add(stem)
        expected_offset = offset + length
    if expected_offset != len(data):
        raise FormatError("archive payloads do not cover the complete file")
    return archive_name, data, entries


def export_archive(source: Path, destination: Path) -> None:
    """Export all PICTURE/SPRITES entries from a Fragile graphics archive."""
    archive_name, data, entries = read_archive(source)
    destination_root = destination.resolve()
    for entry in entries:
        output_stem = Path(entry.name).stem
        for relative_output in (f"{output_stem}.png", f"{output_stem}.json", output_stem):
            if (destination / relative_output).resolve().parent != destination_root:
                raise FormatError(f"archive entry '{entry.name}' escapes the output directory")
    destination.mkdir(parents=True, exist_ok=True)
    exported_entries = []

    # Sprite files can intentionally omit a palette.  Keep every archive entry
    # together while exporting so fallback_palette can locate a matching one.
    with tempfile.TemporaryDirectory(prefix="fragile256-") as temporary:
        staging = Path(temporary)
        staging_root = staging.resolve()
        for entry in entries:
            staged_path = (staging / entry.name).resolve()
            if staged_path.parent != staging_root:
                raise FormatError(f"archive entry '{entry.name}' escapes the staging directory")
            staged_path.write_bytes(data[entry.offset : entry.offset + entry.length])

        for entry in entries:
            staged_source = (staging / entry.name).resolve()
            try:
                read_picture(staged_source)
                export_png(staged_source, destination / f"{staged_source.stem}.png")
                kind = "picture"
            except FormatError:
                export_sprites(staged_source, destination)
                kind = "sprites"
            exported_entries.append(
                {
                    "index": entry.index,
                    "source": entry.name,
                    "length": entry.length,
                    "kind": kind,
                    "output": (
                        f"{staged_source.stem}.png"
                        if kind == "picture"
                        else f"{staged_source.stem}.json"
                    ),
                }
            )

    manifest = {
        "format": "fragile-allegiance-graphics-archive",
        "version": 1,
        "source": source.name,
        "archive": archive_name,
        "entries": exported_entries,
    }
    (destination / "archive.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def normalized_palette(image: Image.Image, fallback: bytes) -> bytes:
    palette = image.getpalette(rawmode="RGB") or []
    palette_bytes = bytes(palette[:PALETTE_SIZE])
    palette_bytes += palette_to_png(fallback)[len(palette_bytes) :]
    return palette_from_png(palette_bytes, fallback)


def import_png(source: Path, template: Path, destination: Path) -> None:
    data, width, height, pixels_offset, palette_offset = read_picture(template)
    original_palette_start = palette_offset + PALETTE_HEADER_SIZE
    original_palette = bytes(
        data[original_palette_start : original_palette_start + PALETTE_SIZE]
    )

    with Image.open(source) as loaded:
        loaded.load()
        if loaded.size != (width, height):
            raise FormatError(
                f"PNG dimensions must be {width}x{height}, got {loaded.width}x{loaded.height}"
            )

        if loaded.mode == "P":
            image = loaded.copy()
            palette = normalized_palette(image, original_palette)
        else:
            reference = Image.new("P", (1, 1))
            reference.putpalette(palette_to_png(original_palette), rawmode="RGB")
            image = loaded.convert("RGB").quantize(
                palette=reference, dither=Image.Dither.NONE
            )
            palette = original_palette
            print(
                "warning: non-indexed PNG mapped to the template palette; "
                "use an indexed PNG to edit the palette intentionally",
                file=sys.stderr,
            )

        pixels = image.tobytes()

    data[pixels_offset:palette_offset] = pixels
    data[original_palette_start : original_palette_start + PALETTE_SIZE] = palette
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)


def print_info(path: Path) -> None:
    _, width, height, _, _ = read_picture(path)
    print(f"{path}: PICTURE, {width}x{height}, 8-bit indexed palette")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    export = commands.add_parser("export", help="convert a .256 PICTURE asset to PNG")
    export.add_argument("source", type=Path)
    export.add_argument("destination", type=Path)

    sprites = commands.add_parser(
        "export-sprites", help="convert a .256 SPRITES asset to PNG frames and JSON"
    )
    sprites.add_argument("source", type=Path)
    sprites.add_argument("destination", type=Path, help="parent png directory")

    archive = commands.add_parser(
        "export-archive", help="extract every PICTURE/SPRITES entry from a graphics archive"
    )
    archive.add_argument("source", type=Path)
    archive.add_argument("destination", type=Path, help="output png directory")

    imported = commands.add_parser(
        "import", help="write an edited PNG into a copy of a .256 PICTURE asset"
    )
    imported.add_argument("source", type=Path, help="edited PNG")
    imported.add_argument("template", type=Path, help="original .256 asset")
    imported.add_argument("destination", type=Path, help="output .256 asset")

    info = commands.add_parser("info", help="show supported .256 image details")
    info.add_argument("source", type=Path)

    arguments = parser.parse_args()
    try:
        if arguments.command == "export":
            export_png(arguments.source, arguments.destination)
        elif arguments.command == "export-sprites":
            export_sprites(arguments.source, arguments.destination)
        elif arguments.command == "export-archive":
            export_archive(arguments.source, arguments.destination)
        elif arguments.command == "import":
            import_png(arguments.source, arguments.template, arguments.destination)
        else:
            print_info(arguments.source)
    except (FormatError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
