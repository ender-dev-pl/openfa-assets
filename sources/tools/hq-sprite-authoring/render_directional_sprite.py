#!/usr/bin/env python3
"""Render a directional vertex-colour model as a deterministic 2x RGBA sprite."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


FORMAT_NAME = "openfa-hq-directional-sprite-sequence"
FORMAT_VERSION = 1
GENERATOR_VERSION = 1
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class LogicalFrame:
    index: int
    canvas_width: int
    canvas_height: int
    x: int
    y: int
    width: int
    height: int

    @property
    def physical_bounds(self) -> tuple[int, int, int, int]:
        return self.x * 2, self.y * 2, self.width * 2, self.height * 2


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--frame-manifest", type=Path, required=True)
    parser.add_argument("--appearance-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--render-resolution", type=int, default=1024)
    parser.add_argument("--contact-columns", type=int, default=10)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def load_logical_frames(manifest: dict[str, Any]) -> list[LogicalFrame]:
    raw_frames = manifest.get("frames")
    if not isinstance(raw_frames, list) or not raw_frames:
        raise ValueError("frame manifest must contain a non-empty frames array")
    frames = [
        LogicalFrame(
            index=int(item["index"]),
            canvas_width=int(item["canvas_width"]),
            canvas_height=int(item["canvas_height"]),
            x=int(item["x"]),
            y=int(item["y"]),
            width=int(item["width"]),
            height=int(item["height"]),
        )
        for item in raw_frames
    ]
    frames.sort(key=lambda frame: frame.index)
    if [frame.index for frame in frames] != list(range(len(frames))):
        raise ValueError("frame indices must be contiguous and start at zero")
    canvas_sizes = {(frame.canvas_width, frame.canvas_height) for frame in frames}
    if len(canvas_sizes) != 1:
        raise ValueError("every frame must use the same logical canvas")
    for frame in frames:
        if min(frame.width, frame.height) <= 0:
            raise ValueError(f"frame {frame.index} has an empty reference bound")
        if frame.x < 0 or frame.y < 0:
            raise ValueError(f"frame {frame.index} has a negative reference bound")
        if frame.x + frame.width > frame.canvas_width:
            raise ValueError(f"frame {frame.index} exceeds the logical canvas width")
        if frame.y + frame.height > frame.canvas_height:
            raise ValueError(f"frame {frame.index} exceeds the logical canvas height")
    return frames


def srgb_to_linear(values: Any) -> Any:
    import numpy as np

    values = np.asarray(values, dtype=np.float32)
    return np.where(
        values <= 0.04045,
        values / 12.92,
        ((values + 0.055) / 1.055) ** 2.4,
    )


def linear_to_srgb(values: Any) -> Any:
    import numpy as np

    values = np.clip(np.asarray(values, dtype=np.float32), 0.0, 1.0)
    return np.where(
        values <= 0.0031308,
        values * 12.92,
        1.055 * values ** (1.0 / 2.4) - 0.055,
    )


def unpremultiply_rgba(linear_rgba: Any) -> Any:
    import numpy as np

    rgba = np.clip(np.asarray(linear_rgba, dtype=np.float32), 0.0, 1.0)
    alpha = rgba[..., 3:4]
    rgb = np.divide(
        rgba[..., :3],
        alpha,
        out=np.zeros_like(rgba[..., :3]),
        where=alpha > 1.0 / 65535.0,
    )
    encoded = linear_to_srgb(rgb)
    return np.clip(
        np.concatenate((encoded, alpha), axis=-1) * 255.0 + 0.5,
        0,
        255,
    ).astype(np.uint8)


def resize_straight_alpha(image: Any, size: tuple[int, int]) -> Any:
    import numpy as np
    from PIL import Image

    rgba = np.asarray(image.convert("RGBA"), dtype=np.float32) / 255.0
    alpha = rgba[..., 3:4]
    premultiplied = np.concatenate((srgb_to_linear(rgba[..., :3]) * alpha, alpha), axis=2)
    channels = []
    for channel in range(4):
        source = Image.fromarray(premultiplied[..., channel], mode="F")
        channels.append(
            np.asarray(source.resize(size, Image.Resampling.LANCZOS), dtype=np.float32)
        )
    return Image.fromarray(unpremultiply_rgba(np.stack(channels, axis=2)), mode="RGBA")


def crop_to_alpha(image: Any) -> Any:
    box = image.getbbox()
    if box is None:
        raise ValueError("rendered model produced an empty frame")
    return image.crop(box)


def remove_tiny_components(image: Any, minimum_fraction: float = 0.0005) -> Any:
    import numpy as np
    from PIL import Image
    from scipy import ndimage

    rgba = np.asarray(image.convert("RGBA")).copy()
    labels, count = ndimage.label(rgba[..., 3] > 0)
    if count == 0:
        raise ValueError("rendered model produced an empty frame")
    areas = np.bincount(labels.ravel())
    foreground_area = int(areas[1:].sum())
    threshold = max(16, math.ceil(foreground_area * minimum_fraction))
    retained = np.flatnonzero(areas >= threshold)
    retained = retained[retained != 0]
    keep = np.isin(labels, retained)
    rgba[~keep] = 0
    return Image.fromarray(rgba, mode="RGBA")


def png_metadata() -> Any:
    from PIL.PngImagePlugin import PngInfo

    metadata = PngInfo()
    metadata.add(b"sRGB", b"\x00")
    return metadata


def save_rgba_png(image: Any, path: Path) -> None:
    image.save(path, format="PNG", optimize=False, compress_level=9, pnginfo=png_metadata())


def model_geometry(model_path: Path) -> tuple[Any, Any, Any]:
    import numpy as np
    import trimesh

    scene = trimesh.load(model_path, force="scene", process=False)
    if len(scene.geometry) != 1:
        raise ValueError("the source model must contain exactly one mesh")
    mesh = next(iter(scene.geometry.values()))
    if getattr(mesh.visual, "kind", None) != "vertex":
        raise ValueError("the source model must provide RGBA vertex colours")
    vertices = np.asarray(mesh.vertices, dtype=np.float32)
    # The reconstruction exporter converts TRELLIS Z-up coordinates to glTF Y-up.
    # Undo that storage transform so the proven directional camera mapping remains valid.
    storage_transform = np.asarray(
        [[1, 0, 0], [0, 0, -1], [0, 1, 0]],
        dtype=np.float32,
    )
    vertices = vertices @ storage_transform.T
    faces = np.asarray(mesh.faces, dtype=np.int32)
    colors = np.asarray(mesh.visual.vertex_colors, dtype=np.float32) / 255.0
    return vertices, faces, colors


def render_views(
    vertices: Any,
    faces: Any,
    colors: Any,
    frame_count: int,
    pitch_degrees: float,
    resolution: int,
) -> list[Any]:
    import numpy as np
    import torch
    import utils3d
    from PIL import Image

    if resolution < 256:
        raise ValueError("render resolution must be at least 256 pixels")
    device = torch.device("cuda")
    if not torch.cuda.is_available():
        raise RuntimeError("the current authoring renderer requires an NVIDIA CUDA device")
    vertex_tensor = torch.tensor(vertices, dtype=torch.float32, device=device)[None]
    face_tensor = torch.tensor(faces, dtype=torch.int32, device=device)
    linear_rgb = srgb_to_linear(colors[:, :3])
    attributes = torch.tensor(
        np.concatenate((linear_rgb, colors[:, 3:4]), axis=1),
        dtype=torch.float32,
        device=device,
    )[None]
    context = utils3d.torch.RastContext(backend="cuda")
    pitch = torch.tensor(math.radians(pitch_degrees), dtype=torch.float32, device=device)
    up = torch.tensor([0.0, 0.0, 1.0], device=device)
    target = torch.zeros(3, device=device)
    fov = torch.tensor(math.radians(40.0), dtype=torch.float32, device=device)
    intrinsic = utils3d.torch.intrinsics_from_fov_xy(fov, fov)
    projection = utils3d.torch.intrinsics_to_perspective(intrinsic, 0.1, 10.0)
    images = []
    for position in range(frame_count):
        yaw = torch.tensor(
            2.0 * math.pi * position / frame_count,
            dtype=torch.float32,
            device=device,
        )
        origin = torch.stack(
            (
                torch.sin(yaw) * torch.cos(pitch),
                torch.cos(yaw) * torch.cos(pitch),
                torch.sin(pitch),
            )
        ) * 2.0
        extrinsic = utils3d.torch.extrinsics_look_at(origin, target, up)
        view = utils3d.torch.extrinsics_to_view(extrinsic)
        rasterized = utils3d.torch.rasterize_triangle_faces(
            context,
            vertex_tensor,
            face_tensor,
            resolution,
            resolution,
            attr=attributes,
            view=view,
            projection=projection,
            antialiasing=True,
        )
        rgba = rasterized["image"][0].permute(1, 2, 0).detach().cpu().numpy()
        images.append(Image.fromarray(unpremultiply_rgba(rgba), mode="RGBA"))
    return images


def place_frame(render: Any, frame: LogicalFrame) -> Any:
    from PIL import Image

    x, y, width, height = frame.physical_bounds
    sprite = resize_straight_alpha(
        crop_to_alpha(remove_tiny_components(render)),
        (width, height),
    )
    canvas = Image.new(
        "RGBA",
        (frame.canvas_width * 2, frame.canvas_height * 2),
        (0, 0, 0, 0),
    )
    canvas.alpha_composite(sprite, (x, y))
    return canvas


def make_atlas(images: list[Any], columns: int) -> tuple[Any, list[dict[str, int]]]:
    from PIL import Image

    if columns <= 0:
        raise ValueError("contact columns must be positive")
    width, height = images[0].size
    rows = math.ceil(len(images) / columns)
    atlas = Image.new("RGBA", (width * columns, height * rows), (0, 0, 0, 0))
    rectangles = []
    for index, image in enumerate(images):
        x = (index % columns) * width
        y = (index // columns) * height
        atlas.alpha_composite(image, (x, y))
        rectangles.append({"index": index, "x": x, "y": y, "width": width, "height": height})
    return atlas, rectangles


def checkerboard(size: tuple[int, int], cell: int = 16) -> Any:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", size, (54, 56, 62))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(72, 74, 82))
    return image


def make_contact_sheet(images: list[Any], columns: int) -> Any:
    from PIL import Image, ImageDraw

    selected = [images[index] for index in range(0, len(images), max(1, len(images) // 12))][:12]
    tile = (320, 240)
    rows = math.ceil(len(selected) / columns)
    sheet = Image.new("RGB", (tile[0] * columns, tile[1] * rows), (30, 31, 35))
    draw = ImageDraw.Draw(sheet)
    for position, image in enumerate(selected):
        preview = image.copy()
        preview.thumbnail((tile[0] - 24, tile[1] - 36), Image.Resampling.LANCZOS)
        background = checkerboard(tile)
        background.paste(
            preview,
            ((tile[0] - preview.width) // 2, (tile[1] - preview.height) // 2 + 8),
            preview,
        )
        x = (position % columns) * tile[0]
        y = (position // columns) * tile[1]
        sheet.paste(background, (x, y))
        frame_index = position * max(1, len(images) // 12)
        draw.text((x + 8, y + 8), f"frame {frame_index:02d} | native 2x RGBA", fill="white")
    return sheet


def png_ihdr(path: Path) -> dict[str, int]:
    data = path.read_bytes()[:33]
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG file")
    return {
        "width": int.from_bytes(data[16:20], "big"),
        "height": int.from_bytes(data[20:24], "big"),
        "bit_depth": data[24],
        "color_type": data[25],
    }


def png_chunks(path: Path) -> list[str]:
    data = path.read_bytes()
    if data[:8] != PNG_SIGNATURE:
        raise ValueError(f"{path} is not a PNG file")
    chunks = []
    offset = 8
    while offset + 12 <= len(data):
        length = int.from_bytes(data[offset : offset + 4], "big")
        kind = data[offset + 4 : offset + 8].decode("ascii")
        chunks.append(kind)
        offset += 12 + length
        if kind == "IEND":
            break
    return chunks


def silhouette_iou(reference: Any, hq_frame: Any) -> float:
    import numpy as np
    from PIL import Image

    reference_mask = np.asarray(reference.convert("RGBA"))[..., 3] > 0
    logical_alpha = hq_frame.getchannel("A").resize(
        reference.size,
        Image.Resampling.BOX,
    )
    hq_mask = np.asarray(logical_alpha) >= 128
    intersection = np.logical_and(reference_mask, hq_mask).sum()
    union = np.logical_or(reference_mask, hq_mask).sum()
    return 1.0 if union == 0 else float(intersection / union)


def validate_outputs(
    images: list[Any],
    frames: list[LogicalFrame],
    frame_paths: list[Path],
    raw_frames: list[dict[str, Any]],
    reference_root: Path,
) -> dict[str, Any]:
    import numpy as np
    from PIL import Image

    expected_size = (frames[0].canvas_width * 2, frames[0].canvas_height * 2)
    exact_bounds = True
    transparent_rgb_zero = True
    partial_alpha_pixels = 0
    opaque_colors: set[tuple[int, int, int]] = set()
    for frame, image in zip(frames, images):
        rgba = np.asarray(image.convert("RGBA"))
        x, y, width, height = frame.physical_bounds
        exact_bounds &= image.getbbox() == (x, y, x + width, y + height)
        transparent_rgb_zero &= not np.any(rgba[rgba[..., 3] == 0, :3])
        partial_alpha_pixels += int(
            np.logical_and(rgba[..., 3] > 0, rgba[..., 3] < 255).sum()
        )
        opaque_colors.update(
            map(tuple, np.unique(rgba[rgba[..., 3] > 0, :3], axis=0).tolist())
        )

    reference_ious = []
    for raw_frame, image in zip(raw_frames, images):
        relative_path = raw_frame.get("png")
        if not relative_path:
            reference_ious = []
            break
        reference_path = reference_root / relative_path
        if not reference_path.is_file():
            reference_ious = []
            break
        with Image.open(reference_path) as reference:
            reference_ious.append(silhouette_iou(reference, image))

    validation: dict[str, Any] = {
        "first_frame_ihdr": png_ihdr(frame_paths[0]),
        "all_frames_rgba8": all(
            png_ihdr(path)["bit_depth"] == 8 and png_ihdr(path)["color_type"] == 6
            for path in frame_paths
        ),
        "all_frames_tagged_srgb": all("sRGB" in png_chunks(path) for path in frame_paths),
        "all_frames_expected_size": all(image.size == expected_size for image in images),
        "all_frames_exact_2x_reference_bounds": exact_bounds,
        "transparent_pixels_have_zero_rgb": transparent_rgb_zero,
        "partial_alpha_pixel_count": partial_alpha_pixels,
        "unique_opaque_rgb_count": len(opaque_colors),
    }
    if reference_ious:
        validation["private_reference_silhouette_iou"] = {
            "method": "2x alpha box-downsampled to logical size; threshold 128",
            "mean": round(sum(reference_ious) / len(reference_ious), 6),
            "minimum": round(min(reference_ious), 6),
            "frame_count": len(reference_ious),
        }
    return validation


def artifacts(paths: Iterable[Path], root: Path) -> list[dict[str, Any]]:
    return [
        {
            "file": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in paths
    ]


def run(arguments: argparse.Namespace) -> Path:
    model_path = arguments.model.resolve(strict=True)
    frame_manifest_path = arguments.frame_manifest.resolve(strict=True)
    appearance_manifest_path = arguments.appearance_manifest.resolve(strict=True)
    output_root = arguments.output.resolve()
    frame_root = output_root / "frames"
    output_root.mkdir(parents=True, exist_ok=True)
    frame_root.mkdir(parents=True, exist_ok=True)

    reference_manifest = load_json(frame_manifest_path)
    appearance_manifest = load_json(appearance_manifest_path)
    frames = load_logical_frames(reference_manifest)
    parameters = appearance_manifest["parameters"]
    mapping = appearance_manifest["view_mapping"]
    pitch_degrees = float(parameters["pitch_degrees"])
    yaw_offset = int(mapping["yaw_offset_frames"])
    direction = int(mapping["direction"])
    if direction not in (-1, 1):
        raise ValueError("appearance direction must be -1 or 1")

    vertices, faces, colors = model_geometry(model_path)
    rendered = render_views(
        vertices,
        faces,
        colors,
        len(frames),
        pitch_degrees,
        arguments.render_resolution,
    )
    images = []
    for frame in frames:
        view = (yaw_offset + direction * frame.index) % len(frames)
        images.append(place_frame(rendered[view], frame))

    frame_paths = []
    for frame, image in zip(frames, images):
        path = frame_root / f"{frame.index:03d}.png"
        save_rgba_png(image, path)
        frame_paths.append(path)
    atlas, rectangles = make_atlas(images, arguments.contact_columns)
    atlas_path = output_root / "atlas.png"
    save_rgba_png(atlas, atlas_path)
    contact_path = output_root / "contact-sheet.png"
    make_contact_sheet(images, min(4, arguments.contact_columns)).save(
        contact_path,
        format="PNG",
        optimize=False,
        compress_level=9,
        pnginfo=png_metadata(),
    )

    logical_size = [frames[0].canvas_width, frames[0].canvas_height]
    physical_size = [value * 2 for value in logical_size]
    manifest = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "asset": {
            "id": arguments.asset_id,
            "display_name": arguments.display_name,
            "density": 2,
            "frame_count": len(frames),
            "logical_frame_size": logical_size,
            "physical_frame_size": physical_size,
            "origin": "inherited-from-logical-asset",
            "hotspot": "inherited-from-logical-asset",
            "animation_timing": "inherited-from-logical-asset",
        },
        "pixels": {
            "container": "PNG",
            "format": "RGBA8",
            "png_color_type": 6,
            "bit_depth": 8,
            "color_space": "sRGB",
            "alpha_mode": "straight",
            "sampling": "linear",
        },
        "layout": {
            "atlas": "atlas.png",
            "columns": arguments.contact_columns,
            "frames": rectangles,
        },
        "authoring": {
            "generator": "tools/hq-sprite-authoring/render_directional_sprite.py",
            "generator_version": GENERATOR_VERSION,
            "render_resolution": arguments.render_resolution,
            "projection": {
                "kind": "perspective",
                "vertical_fov_degrees": 40.0,
                "pitch_degrees": pitch_degrees,
                "yaw_offset_frames": yaw_offset,
                "direction": direction,
            },
            "placement": "legacy-reference-bounds-at-2x",
            "resize_filter": "linear-light-premultiplied-lanczos",
        },
        "provenance": {
            "source_model_sha256": sha256(model_path),
            "private_frame_manifest_sha256": sha256(frame_manifest_path),
            "appearance_manifest_sha256": sha256(appearance_manifest_path),
            "original_frames_redistributed": False,
        },
        "validation": validate_outputs(
            images,
            frames,
            frame_paths,
            reference_manifest["frames"],
            frame_manifest_path.parent,
        ),
        "artifacts": artifacts([*frame_paths, atlas_path, contact_path], output_root),
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest_path


def main() -> int:
    manifest_path = run(parse_arguments())
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
