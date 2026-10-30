"""Export the chunk structure of Fragile Allegiance .VID files."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

from PIL import Image


ROOT_TAG = b"Vide"
HEADER_TAG = b"Head"
INTER_TAG = b"Inte"
FRAME_TAG = b"Fram"
IMAGE_DECODER = 0xF7061
INTER_DECODER = 0xF7514
RETURN_ADDRESS = 0x1FFF00
JUMP_TABLE = 0x75424
TEMP_BUFFER_GLOBAL = 0x1382D0
WIDTH_GLOBAL = 0x13830C
HEIGHT_GLOBAL = 0x1382D8
PALETTE_OFFSET_GLOBAL = 0x138304
FRAME_BUFFER_SIZE = 0x100000
PALETTE_SIZE = 256 * 3


class FormatError(ValueError):
    """Raised when a file is not a supported .VID container."""


def validate_dimensions(width: int, height: int) -> None:
    if not width or not height or width * height + PALETTE_SIZE > FRAME_BUFFER_SIZE:
        raise FormatError("video dimensions exceed the emulator frame buffer")


def read_chunks(data: bytes) -> list[tuple[bytes, int, int]]:
    """Validate the entire chunk table before producing output or invoking the codec."""
    chunks = []
    offset = 8
    while offset < len(data):
        if offset + 8 > len(data):
            raise FormatError(f"truncated chunk header at 0x{offset:X}")
        tag = data[offset : offset + 4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        if size < 8 or offset + size > len(data):
            raise FormatError(f"invalid chunk size at 0x{offset:X}")
        chunks.append((tag, offset, size))
        offset += size
    return chunks


class VideoDecoder:
    """Runs Fragile Allegiance's own video codec in an isolated x86 emulator."""

    def __init__(self, executable: Path, width: int, height: int) -> None:
        validate_dimensions(width, height)
        try:
            from unicorn import UC_ARCH_X86, UC_MODE_32, Uc, UcError
            from unicorn.x86_const import (
                UC_X86_REG_EAX,
                UC_X86_REG_EBX,
                UC_X86_REG_EDX,
                UC_X86_REG_ESP,
            )
        except ImportError as error:
            raise FormatError("video decoding requires the unicorn Python package") from error
        self.uc_error = UcError
        self.registers = (UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_EDX, UC_X86_REG_ESP)
        executable_bytes = executable.read_bytes()
        self.emulator = Uc(UC_ARCH_X86, UC_MODE_32)
        self.emulator.mem_map(0, 0x200000)
        self.emulator.mem_write(0, executable_bytes)

        handlers = [
            0xF7214,
            0xF7228,
            0xF7243,
            0xF725E,
            0xF727A,
            0xF7295,
            0xF72B4,
            0xF72D0,
            0xF72F0,
            0xF7305,
            0xF7321,
            0xF733D,
            0xF735A,
            0xF7370,
            0xF738D,
            0xF73AA,
        ]
        jump_table = [0xF7210] + [handlers[(index - 1) & 15] for index in range(1, 256)]
        self.emulator.mem_write(
            JUMP_TABLE, b"".join(struct.pack("<I", address) for address in jump_table)
        )

        self.current = 0x200000
        self.other = 0x300000
        self.payload = 0x400000
        self.temporary = 0x800000
        self.stack = 0xC00000
        for address, size in [
            (self.current, 0x100000),
            (self.other, 0x100000),
            (self.payload, 0x400000),
            (self.temporary, 0x400000),
            (self.stack, 0x100000),
        ]:
            self.emulator.mem_map(address, size)

        for address, value in [
            (TEMP_BUFFER_GLOBAL, self.temporary),
            (WIDTH_GLOBAL, width),
            (HEIGHT_GLOBAL, height),
            (PALETTE_OFFSET_GLOBAL, 0),
        ]:
            self.emulator.mem_write(address, struct.pack("<I", value))
        self.width = width
        self.height = height

    def _run(self, entrypoint: int, destination: int, source: int, payload: bytes) -> None:
        if len(payload) > 0x400000:
            raise FormatError("chunk exceeds the emulator input buffer")
        self.emulator.mem_write(self.payload, payload)
        eax, ebx, edx, esp = self.registers
        self.emulator.reg_write(eax, destination)
        self.emulator.reg_write(edx, source)
        self.emulator.reg_write(ebx, self.payload)
        stack_pointer = self.stack + 0xFFF00
        self.emulator.reg_write(esp, stack_pointer)
        self.emulator.mem_write(stack_pointer, struct.pack("<I", RETURN_ADDRESS))
        try:
            self.emulator.emu_start(entrypoint, RETURN_ADDRESS, count=80_000_000)
        except self.uc_error as error:
            raise FormatError(f"video decoder failed at 0x{entrypoint:X}: {error}") from error

    def apply_inter(self, payload: bytes) -> None:
        self._run(INTER_DECODER, self.current, self.payload, payload)

    def apply_frame(self, payload: bytes) -> tuple[bytes, bytes]:
        self._run(IMAGE_DECODER, self.other, self.current, payload)
        self.current, self.other = self.other, self.current
        size = PALETTE_SIZE + self.width * self.height
        decoded = bytes(self.emulator.mem_read(self.current, size))
        return decoded[: 256 * 3], decoded[256 * 3 :]


def export_structure(source: Path, destination: Path) -> None:
    data = source.read_bytes()
    if len(data) < 8 or data[:4] != ROOT_TAG:
        raise FormatError("missing Vide signature")
    declared_size = struct.unpack_from("<I", data, 4)[0]
    if declared_size != len(data):
        raise FormatError(f"container declares {declared_size} bytes, got {len(data)}")

    parsed_chunks = read_chunks(data)
    destination.mkdir(parents=True, exist_ok=True)
    frames_directory = destination / "frames"
    inter_directory = destination / "inter"
    frames_directory.mkdir(exist_ok=True)
    inter_directory.mkdir(exist_ok=True)

    chunks = []
    frame_index = 0
    inter_index = 0
    header = None

    for tag, offset, size in parsed_chunks:
        payload = data[offset + 8 : offset + size]
        item = {
            "tag": tag.decode("ascii", "replace"),
            "offset": offset,
            "size": size,
            "payload_size": len(payload),
        }
        if tag == HEADER_TAG:
            if len(payload) != 12:
                raise FormatError("unexpected Head payload length")
            header = {"raw_u16": list(struct.unpack("<6H", payload))}
        elif tag == INTER_TAG:
            filename = f"{inter_index:03}.bin"
            (inter_directory / filename).write_bytes(payload)
            item["index"] = inter_index
            item["file"] = f"inter/{filename}"
            inter_index += 1
        elif tag == FRAME_TAG:
            filename = f"{frame_index:03}.bin"
            (frames_directory / filename).write_bytes(payload)
            item["index"] = frame_index
            item["file"] = f"frames/{filename}"
            frame_index += 1
        chunks.append(item)

    manifest = {
        "format": "fragile-allegiance-vid",
        "version": 1,
        "source": source.name,
        "container_size": len(data),
        "head": header,
        "chunks": chunks,
        "notes": [
            "Fram blocks are compressed delta frames and are not yet decoded to PNG.",
            "Inte blocks preserve palette/reference-state updates required for decoding.",
        ],
    }
    (destination / "metadata.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def export_png(source: Path, destination: Path, executable: Path) -> None:
    data = source.read_bytes()
    if len(data) < 28 or data[:4] != ROOT_TAG:
        raise FormatError("missing Vide signature")
    if struct.unpack_from("<I", data, 4)[0] != len(data):
        raise FormatError("container size does not match the file")

    parsed_chunks = read_chunks(data)
    if not parsed_chunks or parsed_chunks[0][0] != HEADER_TAG:
        raise FormatError("Head must be the first chunk")
    _, header_offset, header_size = parsed_chunks[0]
    if header_size != 20:
        raise FormatError("unexpected Head chunk size")
    head = struct.unpack_from("<6H", data, header_offset + 8)
    bit_depth, width, height, declared_frames, _, _ = head
    if bit_depth != 8 or not width or not height:
        raise FormatError("unsupported video dimensions or bit depth")
    validate_dimensions(width, height)

    decoder = VideoDecoder(executable, width, height)
    frames_directory = destination / "frames"
    frames_directory.mkdir(parents=True, exist_ok=True)
    manifest_chunks = []
    frame_index = 0
    inter_index = 0
    for tag, offset, size in parsed_chunks[1:]:
        payload = data[offset + 8 : offset + size]
        chunk = {"tag": tag.decode("ascii", "replace"), "offset": offset, "size": size}
        if tag == INTER_TAG:
            decoder.apply_inter(payload)
            chunk["index"] = inter_index
            inter_index += 1
        elif tag == FRAME_TAG:
            palette, pixels = decoder.apply_frame(payload)
            png_name = f"{frame_index:03}.png"
            image = Image.frombytes("P", (width, height), pixels)
            image.putpalette(
                bytes(((value & 0x3F) * 255 + 31) // 63 for value in palette),
                rawmode="RGB",
            )
            image.save(frames_directory / png_name, format="PNG", bits=8, optimize=False)
            chunk["index"] = frame_index
            chunk["png"] = f"frames/{png_name}"
            frame_index += 1
        manifest_chunks.append(chunk)

    if frame_index != declared_frames:
        raise FormatError(f"Head declares {declared_frames} frames, decoded {frame_index}")
    manifest = {
        "format": "fragile-allegiance-vid",
        "version": 1,
        "source": source.name,
        "head": {
            "bit_depth": bit_depth,
            "width": width,
            "height": height,
            "frame_count": frame_index,
            "raw_u16": list(head),
        },
        "chunks": manifest_chunks,
        "decoder": "FRAGILE.EXE video codec, emulated with Unicorn",
    }
    (destination / "metadata.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    structure = commands.add_parser("structure", help="export raw chunks and their metadata")
    structure.add_argument("source", type=Path)
    structure.add_argument("destination", type=Path)
    exported = commands.add_parser("export", help="decode a .VID file to paletted PNG frames")
    exported.add_argument("source", type=Path)
    exported.add_argument("destination", type=Path)
    exported.add_argument("--executable", type=Path, default=Path("FRAGILE.EXE"))
    arguments = parser.parse_args()
    try:
        if arguments.command == "structure":
            export_structure(arguments.source, arguments.destination)
        else:
            export_png(arguments.source, arguments.destination, arguments.executable)
    except (FormatError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
