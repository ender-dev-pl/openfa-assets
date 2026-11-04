#!/usr/bin/env python3
"""Create a deterministic HQ 2x sequence directly from decoded RGBA sprites."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from render_directional_sprite import (
    artifacts,
    checkerboard,
    linear_to_srgb,
    load_json,
    load_logical_frames,
    make_atlas,
    make_contact_sheet,
    png_chunks,
    png_ihdr,
    save_rgba_png,
    sha256,
    srgb_to_linear,
)
from rrdbnet_x2 import RrdbNetX2


FORMAT_NAME = "openfa-hq-raster-upscale-sequence"
FORMAT_VERSION = 1
GENERATOR_VERSION = 2


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--frame-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contact-columns", type=int, default=10)
    parser.add_argument("--bilateral-colour-sigma", type=float, default=0.025)
    parser.add_argument("--bilateral-space-sigma", type=float, default=0.9)
    parser.add_argument("--sharpen-amount", type=float, default=0.9)
    parser.add_argument("--sharpen-radius", type=float, default=0.7)
    parser.add_argument("--detail-limit", type=float, default=0.12)
    parser.add_argument("--alpha-contour-sigma", type=float, default=0.35)
    parser.add_argument("--alpha-softness", type=float, default=0.55)
    parser.add_argument("--realesrgan-model", type=Path)
    parser.add_argument("--realesrgan-blend", type=float, default=0.55)
    return parser.parse_args()


def reconstruct_edge_colours(rgba: np.ndarray) -> np.ndarray:
    from scipy import ndimage

    opaque = rgba[..., 3] > 0
    if not np.any(opaque):
        raise ValueError("source sprite contains no opaque pixels")
    nearest = ndimage.distance_transform_edt(
        ~opaque,
        return_distances=False,
        return_indices=True,
    )
    rgb = rgba[..., :3].copy()
    rgb[~opaque] = rgb[nearest[0][~opaque], nearest[1][~opaque]]
    return rgb


def edge_preserving_smooth(
    linear_rgb: np.ndarray,
    colour_sigma: float,
    space_sigma: float,
) -> np.ndarray:
    import cv2

    if colour_sigma < 0 or space_sigma <= 0:
        raise ValueError("bilateral filter parameters must be non-negative")
    if colour_sigma == 0:
        return linear_rgb.copy()
    return cv2.bilateralFilter(
        linear_rgb.astype(np.float32),
        d=5,
        sigmaColor=colour_sigma,
        sigmaSpace=space_sigma,
        borderType=cv2.BORDER_REFLECT_101,
    )


def limited_unsharp_mask(
    image: np.ndarray,
    amount: float,
    radius: float,
    detail_limit: float,
) -> np.ndarray:
    import cv2

    if amount < 0 or radius <= 0 or detail_limit < 0:
        raise ValueError("sharpening parameters must be non-negative")
    if amount == 0 or detail_limit == 0:
        return image.copy()
    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=radius,
        sigmaY=radius,
        borderType=cv2.BORDER_REFLECT_101,
    )
    detail = np.clip(image - blurred, -detail_limit, detail_limit)
    sharpened = image + amount * detail
    local_minimum = cv2.erode(image, np.ones((3, 3), dtype=np.uint8))
    local_maximum = cv2.dilate(image, np.ones((3, 3), dtype=np.uint8))
    return np.clip(sharpened, local_minimum, local_maximum)


def smooth_signed_distance_alpha(
    source_alpha: np.ndarray,
    size: tuple[int, int],
    contour_sigma: float,
    softness: float,
) -> np.ndarray:
    import cv2
    from scipy import ndimage

    if contour_sigma < 0 or softness <= 0:
        raise ValueError("alpha smoothing parameters must be non-negative")
    opaque = source_alpha >= 0.5
    if not np.any(opaque):
        raise ValueError("source sprite contains no opaque pixels")
    signed_distance = ndimage.distance_transform_edt(opaque) - ndimage.distance_transform_edt(
        ~opaque
    )
    upscaled = cv2.resize(
        signed_distance.astype(np.float32),
        size,
        interpolation=cv2.INTER_CUBIC,
    )
    if contour_sigma > 0:
        upscaled = cv2.GaussianBlur(
            upscaled,
            (0, 0),
            sigmaX=contour_sigma,
            sigmaY=contour_sigma,
            borderType=cv2.BORDER_REFLECT_101,
        )
    coverage = np.clip(0.5 + upscaled / (2.0 * softness), 0.0, 1.0)
    return coverage * coverage * (3.0 - 2.0 * coverage)


class RealEsrganX2Upscaler:
    def __init__(self, model_path: Path) -> None:
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("RealESRGAN_x2plus authoring requires an NVIDIA CUDA device")
        self.model_path = model_path.resolve(strict=True)
        checkpoint = torch.load(self.model_path, map_location="cpu", weights_only=True)
        parameters = checkpoint.get("params_ema")
        if not isinstance(parameters, dict):
            raise ValueError("RealESRGAN checkpoint does not contain params_ema")
        self.model = RrdbNetX2().cuda().eval()
        self.model.load_state_dict(parameters, strict=True)

    def upscale(self, rgb: np.ndarray) -> np.ndarray:
        import torch

        height, width = rgb.shape[:2]
        pad_bottom = height % 2
        pad_right = width % 2
        padded = np.pad(
            rgb,
            ((0, pad_bottom), (0, pad_right), (0, 0)),
            mode="reflect",
        )
        tensor = torch.from_numpy(padded.transpose(2, 0, 1)).float().cuda()[None]
        with torch.inference_mode():
            output = self.model(tensor)
        array = output[0].clamp(0.0, 1.0).permute(1, 2, 0).cpu().numpy()
        return array[: height * 2, : width * 2]


def upscale_crop(
    crop: Image.Image,
    colour_sigma: float,
    space_sigma: float,
    sharpen_amount: float,
    sharpen_radius: float,
    detail_limit: float,
    alpha_contour_sigma: float,
    alpha_softness: float,
    neural_upscaler: RealEsrganX2Upscaler | None = None,
    neural_blend: float = 0.75,
) -> Image.Image:
    import cv2

    padding = 3
    padded = Image.new(
        "RGBA",
        (crop.width + padding * 2, crop.height + padding * 2),
        (0, 0, 0, 0),
    )
    padded.alpha_composite(crop.convert("RGBA"), (padding, padding))
    rgba = np.asarray(padded, dtype=np.uint8)
    filled_rgb = reconstruct_edge_colours(rgba).astype(np.float32) / 255.0
    linear_rgb = srgb_to_linear(filled_rgb)
    smoothed = edge_preserving_smooth(linear_rgb, colour_sigma, space_sigma)
    size = (padded.width * 2, padded.height * 2)
    upscaled_rgb = cv2.resize(smoothed, size, interpolation=cv2.INTER_LANCZOS4)
    upscaled_rgb = limited_unsharp_mask(
        np.clip(upscaled_rgb, 0.0, 1.0),
        sharpen_amount,
        sharpen_radius,
        detail_limit,
    )
    if neural_upscaler is not None:
        if not 0.0 <= neural_blend <= 1.0:
            raise ValueError("Real-ESRGAN blend must be between zero and one")
        neural_rgb = srgb_to_linear(neural_upscaler.upscale(filled_rgb))
        upscaled_rgb = (
            neural_rgb * neural_blend + upscaled_rgb * (1.0 - neural_blend)
        )
    alpha = smooth_signed_distance_alpha(
        rgba[..., 3].astype(np.float32) / 255.0,
        size,
        alpha_contour_sigma,
        alpha_softness,
    )
    alpha[alpha < 1.0 / 255.0] = 0.0
    alpha[alpha > 254.0 / 255.0] = 1.0
    encoded_rgb = np.clip(linear_to_srgb(upscaled_rgb) * 255.0 + 0.5, 0, 255).astype(
        np.uint8
    )
    encoded_alpha = np.clip(alpha * 255.0 + 0.5, 0, 255).astype(np.uint8)
    encoded_rgb[encoded_alpha == 0] = 0
    result = Image.fromarray(
        np.dstack((encoded_rgb, encoded_alpha)),
        mode="RGBA",
    )
    inset = padding * 2
    return result.crop((inset, inset, inset + crop.width * 2, inset + crop.height * 2))


def place_upscaled_crop(
    source: Image.Image,
    frame: Any,
    arguments: argparse.Namespace,
    neural_upscaler: RealEsrganX2Upscaler | None,
) -> Image.Image:
    crop = source.crop((frame.x, frame.y, frame.x + frame.width, frame.y + frame.height))
    upscaled = upscale_crop(
        crop,
        arguments.bilateral_colour_sigma,
        arguments.bilateral_space_sigma,
        arguments.sharpen_amount,
        arguments.sharpen_radius,
        arguments.detail_limit,
        arguments.alpha_contour_sigma,
        arguments.alpha_softness,
        neural_upscaler,
        arguments.realesrgan_blend,
    )
    canvas = Image.new(
        "RGBA",
        (frame.canvas_width * 2, frame.canvas_height * 2),
        (0, 0, 0, 0),
    )
    canvas.alpha_composite(upscaled, (frame.x * 2, frame.y * 2))
    return canvas


def make_comparison_sheet(
    sources: list[Image.Image],
    hq_images: list[Image.Image],
    columns: int = 4,
) -> Image.Image:
    selected_indices = list(range(0, len(sources), max(1, len(sources) // 12)))[:12]
    tile = (320, 240)
    rows_per_variant = math.ceil(len(selected_indices) / columns)
    sheet = Image.new(
        "RGB",
        (tile[0] * columns, tile[1] * rows_per_variant * 2),
        (30, 31, 35),
    )
    draw = ImageDraw.Draw(sheet)
    for variant, images in (("source nearest 2x", sources), ("raster HQ 2x", hq_images)):
        row_offset = 0 if variant.startswith("source") else rows_per_variant
        for position, index in enumerate(selected_indices):
            image = images[index]
            if variant.startswith("source"):
                image = image.resize(
                    (image.width * 2, image.height * 2),
                    Image.Resampling.NEAREST,
                )
            preview = image.copy()
            preview.thumbnail((tile[0] - 24, tile[1] - 36), Image.Resampling.LANCZOS)
            background = checkerboard(tile)
            background.paste(
                preview,
                ((tile[0] - preview.width) // 2, (tile[1] - preview.height) // 2 + 8),
                preview,
            )
            column = position % columns
            row = position // columns + row_offset
            x = column * tile[0]
            y = row * tile[1]
            sheet.paste(background, (x, y))
            draw.text((x + 8, y + 8), f"frame {index:02d} | {variant}", fill="white")
    return sheet


def frame_roundtrip_metrics(source: Image.Image, hq: Image.Image) -> dict[str, float]:
    logical = hq.resize(source.size, Image.Resampling.BOX)
    source_rgba = np.asarray(source.convert("RGBA"), dtype=np.float32) / 255.0
    logical_rgba = np.asarray(logical.convert("RGBA"), dtype=np.float32) / 255.0
    source_mask = source_rgba[..., 3] > 0
    logical_mask = logical_rgba[..., 3] >= 0.5
    intersection = np.logical_and(source_mask, logical_mask).sum()
    union = np.logical_or(source_mask, logical_mask).sum()
    colour_mask = np.logical_and(source_mask, logical_mask)
    if np.any(colour_mask):
        difference = source_rgba[..., :3][colour_mask] - logical_rgba[..., :3][colour_mask]
        colour_mae = float(np.mean(np.abs(difference)))
    else:
        colour_mae = 1.0
    return {
        "alpha_iou": 1.0 if union == 0 else float(intersection / union),
        "rgb_mae": colour_mae,
    }


def temporal_roundtrip_mae(
    sources: list[Image.Image],
    hq_images: list[Image.Image],
) -> float:
    source_arrays = [
        np.asarray(image.convert("RGBA"), dtype=np.float32) / 255.0 for image in sources
    ]
    logical_arrays = [
        np.asarray(image.resize(sources[0].size, Image.Resampling.BOX), dtype=np.float32)
        / 255.0
        for image in hq_images
    ]
    errors = []
    for index in range(len(sources)):
        following = (index + 1) % len(sources)
        source_delta = source_arrays[following] - source_arrays[index]
        logical_delta = logical_arrays[following] - logical_arrays[index]
        errors.append(float(np.mean(np.abs(source_delta - logical_delta))))
    return sum(errors) / len(errors)


def validate_outputs(
    sources: list[Image.Image],
    images: list[Image.Image],
    frames: list[Any],
    frame_paths: list[Path],
) -> dict[str, Any]:
    metrics = [frame_roundtrip_metrics(source, hq) for source, hq in zip(sources, images)]
    partial_alpha = 0
    unique_colours: set[tuple[int, int, int]] = set()
    exact_bounds = True
    transparent_rgb_zero = True
    for frame, image in zip(frames, images):
        rgba = np.asarray(image.convert("RGBA"))
        expected = (
            frame.x * 2,
            frame.y * 2,
            (frame.x + frame.width) * 2,
            (frame.y + frame.height) * 2,
        )
        exact_bounds &= image.getbbox() == expected
        transparent_rgb_zero &= not np.any(rgba[rgba[..., 3] == 0, :3])
        partial_alpha += int(np.logical_and(rgba[..., 3] > 0, rgba[..., 3] < 255).sum())
        unique_colours.update(
            map(tuple, np.unique(rgba[rgba[..., 3] > 0, :3], axis=0).tolist())
        )
    return {
        "first_frame_ihdr": png_ihdr(frame_paths[0]),
        "all_frames_rgba8": all(
            png_ihdr(path)["bit_depth"] == 8 and png_ihdr(path)["color_type"] == 6
            for path in frame_paths
        ),
        "all_frames_tagged_srgb": all("sRGB" in png_chunks(path) for path in frame_paths),
        "all_frames_exact_2x_reference_bounds": exact_bounds,
        "transparent_pixels_have_zero_rgb": transparent_rgb_zero,
        "partial_alpha_pixel_count": partial_alpha,
        "unique_opaque_rgb_count": len(unique_colours),
        "roundtrip": {
            "alpha_iou_mean": round(
                sum(metric["alpha_iou"] for metric in metrics) / len(metrics), 6
            ),
            "alpha_iou_minimum": round(min(metric["alpha_iou"] for metric in metrics), 6),
            "rgb_mae_mean": round(
                sum(metric["rgb_mae"] for metric in metrics) / len(metrics), 6
            ),
            "temporal_rgba_delta_mae": round(
                temporal_roundtrip_mae(sources, images),
                6,
            ),
        },
    }


def run(arguments: argparse.Namespace) -> Path:
    manifest_path = arguments.frame_manifest.resolve(strict=True)
    source_root = manifest_path.parent
    output_root = arguments.output.resolve()
    frame_root = output_root / "frames"
    output_root.mkdir(parents=True, exist_ok=True)
    frame_root.mkdir(parents=True, exist_ok=True)
    source_manifest = load_json(manifest_path)
    neural_upscaler = (
        None
        if arguments.realesrgan_model is None
        else RealEsrganX2Upscaler(arguments.realesrgan_model)
    )
    frames = load_logical_frames(source_manifest)
    raw_frames = sorted(source_manifest["frames"], key=lambda item: int(item["index"]))
    sources = []
    hq_images = []
    for frame, raw_frame in zip(frames, raw_frames):
        source_path = (source_root / raw_frame["png"]).resolve(strict=True)
        with Image.open(source_path) as opened:
            source = opened.convert("RGBA")
        if source.size != (frame.canvas_width, frame.canvas_height):
            raise ValueError(f"frame {frame.index} does not match its logical canvas")
        sources.append(source)
        hq_images.append(place_upscaled_crop(source, frame, arguments, neural_upscaler))

    frame_paths = []
    for frame, image in zip(frames, hq_images):
        output_path = frame_root / f"{frame.index:03d}.png"
        save_rgba_png(image, output_path)
        frame_paths.append(output_path)
    atlas, rectangles = make_atlas(hq_images, arguments.contact_columns)
    atlas_path = output_root / "atlas.png"
    save_rgba_png(atlas, atlas_path)
    contact_path = output_root / "contact-sheet.png"
    save_rgba_png(
        make_contact_sheet(hq_images, min(4, arguments.contact_columns)).convert("RGBA"),
        contact_path,
    )
    comparison_path = output_root / "comparison-sheet.png"
    save_rgba_png(
        make_comparison_sheet(sources, hq_images).convert("RGBA"),
        comparison_path,
    )

    logical_size = [frames[0].canvas_width, frames[0].canvas_height]
    pipeline = [
        "nearest-opaque edge-colour reconstruction",
        "sRGB to linear-light conversion",
        "edge-preserving bilateral smoothing",
        "2x Lanczos colour resampling",
    ]
    if neural_upscaler is not None:
        pipeline.append("RealESRGAN_x2plus RGB restoration blend")
    pipeline.extend(
        (
            "signed-distance contour smoothing",
            "bounded linear-light unsharp mask",
            "straight-alpha RGBA8 sRGB encoding",
        )
    )
    manifest = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "asset": {
            "id": arguments.asset_id,
            "display_name": arguments.display_name,
            "density": 2,
            "frame_count": len(frames),
            "logical_frame_size": logical_size,
            "physical_frame_size": [value * 2 for value in logical_size],
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
            "generator": "tools/hq-sprite-authoring/upscale_raster_sprite.py",
            "generator_version": GENERATOR_VERSION,
            "input": "decoded RGBA raster frames",
            "three_dimensional_reconstruction_used": False,
            "pipeline": pipeline,
            "parameters": {
                "bilateral_colour_sigma": arguments.bilateral_colour_sigma,
                "bilateral_space_sigma": arguments.bilateral_space_sigma,
                "sharpen_amount": arguments.sharpen_amount,
                "sharpen_radius": arguments.sharpen_radius,
                "detail_limit": arguments.detail_limit,
                "alpha_contour_sigma": arguments.alpha_contour_sigma,
                "alpha_softness": arguments.alpha_softness,
                "realesrgan_blend": (
                    None if neural_upscaler is None else arguments.realesrgan_blend
                ),
            },
        },
        "provenance": {
            "private_frame_manifest_sha256": sha256(manifest_path),
            "derived_from_original_raster": True,
            "source_frames_included_verbatim": False,
            "comparison_sheet_contains_source_pixels": True,
            "redistribution_status": "pending-rights-review",
            "realesrgan_x2plus_model_sha256": (
                None if neural_upscaler is None else sha256(neural_upscaler.model_path)
            ),
        },
        "validation": validate_outputs(sources, hq_images, frames, frame_paths),
        "artifacts": artifacts(
            [*frame_paths, atlas_path, contact_path, comparison_path],
            output_root,
        ),
    }
    output_manifest = output_root / "manifest.json"
    output_manifest.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return output_manifest


def main() -> int:
    print(run(parse_arguments()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
