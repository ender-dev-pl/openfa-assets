"""Create legacy-layout missile assets from an upright, nose-up image (requires Pillow)."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps


def prepare(source_path, output, review_output, exhaust_directory, background, threshold):
    source = ImageOps.exif_transpose(Image.open(source_path)).convert("RGBA")
    alpha = source.getchannel("A")
    if background == "black" or (background == "auto" and alpha.getextrema() == (255, 255)):
        red, green, blue, _ = source.split()
        maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
        mask = maximum.point(lambda value: 255 if value <= threshold else 0)
        # Padding joins all background regions touching any border, preserving dark interiors.
        padded = ImageOps.expand(mask, border=1, fill=255)
        ImageDraw.floodfill(padded, (0, 0), 128)
        mask = padded.crop((1, 1, source.width + 1, source.height + 1))
        alpha = ImageChops.multiply(alpha, mask.point(lambda value: 0 if value == 128 else 255))
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("The input contains no visible rocket after background removal.")
    cutout = source.copy()
    cutout.putalpha(alpha)
    cutout = cutout.crop(bounds)
    output.mkdir(parents=True, exist_ok=True)
    review_output.mkdir(parents=True, exist_ok=True)
    cutout.save(review_output / "cutout.png")
    variants = {"preview": (41, 138), "inventory": (16, 32), "launch": (10, 32)}
    for name, size in variants.items():
        fitted = cutout.copy()
        fitted.thumbnail(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", size)
        canvas.alpha_composite(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
        canvas.save(output / f"{name}.png")

    # Review at nearest-neighbour enlargement; the checkerboard is not baked into assets.
    review = Image.new("RGB", (600, 480), "#18202c")
    draw = ImageDraw.Draw(review)
    for index, (name, size) in enumerate(variants.items()):
        x = index * 200
        draw.text((x + 12, 16), f"{name}  {size[0]} x {size[1]}", fill="white")
        for y in range(48, 448, 12):
            for xx in range(x + 12, x + 188, 12):
                color = "#454c57" if ((xx - x) // 12 + y // 12) % 2 else "#737b87"
                draw.rectangle((xx, y, min(xx + 11, x + 187), min(y + 11, 447)), fill=color)
        variant = Image.open(output / f"{name}.png")
        scale = min(4, 380 // variant.height, 168 // variant.width)
        enlarged = variant.resize((variant.width * scale, variant.height * scale), Image.Resampling.NEAREST)
        review.paste(enlarged, (x + (200 - enlarged.width) // 2, 58), enlarged)
    review.save(review_output / "asset-review.png")

    # Preserve the measured legacy frame order, dimensions, and emergence/exhaust phases.
    dimensions = [(15, 10), (13, 13), (10, 17), (5, 18), (10, 17), (13, 13), (15, 10)]
    angles = [-60, -40, -20, 0, 20, 40, 60]
    frames = []
    for size, angle in zip(dimensions, angles):
        tilted = cutout.rotate(-angle, Image.Resampling.BICUBIC, expand=True)
        tilted = tilted.crop(tilted.getbbox())
        tilted.thumbnail(size, Image.Resampling.LANCZOS)
        frame = Image.new("RGBA", size)
        frame.alpha_composite(tilted, ((size[0] - tilted.width) // 2, (size[1] - tilted.height) // 2))
        frames.append(frame)
    fitted_body = cutout.copy()
    fitted_body.thumbnail((5, 18), Image.Resampling.LANCZOS)
    body = Image.new("RGBA", (5, 18))
    body.alpha_composite(fitted_body, ((5 - fitted_body.width) // 2, 18 - fitted_body.height))
    frames.extend([body.crop((0, 0, 5, 6)), body.crop((0, 0, 5, 12)), body])
    for index in range(10, 14):
        exhaust = Image.open(exhaust_directory / f"exhaust-{index}.png").convert("RGBA")
        if exhaust.size != (5, [11, 12, 13, 12][index - 10]):
            raise ValueError(f"Unexpected exhaust dimensions: {exhaust.size}")
        frame = Image.new("RGBA", (5, 18 + exhaust.height))
        frame.alpha_composite(body)
        frame.alpha_composite(exhaust, (0, 18))
        frames.append(frame)
    atlas = Image.new("RGBA", (7 * 20, 2 * 36))
    frame_data = []
    frame_review = Image.new("RGB", (840, 440), "#252b35")
    labels = ImageDraw.Draw(frame_review)
    for index, frame in enumerate(frames):
        frame.save(output / f"flight-{index:02}.png")
        x, y = (index % 7) * 20, (index // 7) * 36
        atlas.alpha_composite(frame, (x, y))
        frame_data.append(dict(index=index, x=x, y=y, width=frame.width, height=frame.height,
                               clockwiseTiltDegrees=angles[index] if index < 7 else 0))
        rx, ry = (index % 7) * 120, (index // 7) * 220
        labels.text((rx + 8, ry + 8), f"{index}: {frame.width}x{frame.height}", fill="white")
        enlarged = frame.resize((frame.width * 5, frame.height * 5), Image.Resampling.NEAREST)
        frame_review.paste(enlarged, (rx + (120 - enlarged.width) // 2, ry + 40), enlarged)
    atlas.save(output / "flight-atlas.png")
    (review_output / "flight-frames.json").write_text(json.dumps(frame_data, indent=2) + "\n")
    frame_review.save(review_output / "flight-review.png")
    assert len(frames) == 14
    assert len({frame.tobytes() for frame in frames[:7]}) == 7
    print(f"Source: {source.size}; cutout: {cutout.size}; {len(variants)} UI/base resources and {len(frames)} flight frames.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Upright rocket image, nose pointing up")
    parser.add_argument("--output", type=Path, required=True, help="Generated PNG directory")
    parser.add_argument("--review-output", type=Path, help="Cutout, metadata and reviews (default: output)")
    parser.add_argument("--background", choices=("auto", "black", "keep"), default="auto",
                        help="auto preserves existing alpha, otherwise removes border-connected black")
    parser.add_argument("--black-threshold", type=int, default=20, help="Maximum black RGB channel (0..255)")
    parser.add_argument("--exhaust-directory", type=Path,
                        default=Path(__file__).resolve().parent / "assets/legacy-missile-exhaust",
                        help="Directory containing exhaust-10.png through exhaust-13.png")
    args = parser.parse_args()
    if not 0 <= args.black_threshold <= 255:
        parser.error("--black-threshold must be between 0 and 255")
    review_output = args.review_output or args.output
    # Never allow generated files to replace the supplied image.
    generated = {"preview.png", "inventory.png", "launch.png", "flight-atlas.png"}
    generated.update(f"flight-{index:02}.png" for index in range(14))
    destinations = {args.output.resolve() / name for name in generated}
    destinations.update(review_output.resolve() / name for name in
                        ("cutout.png", "asset-review.png", "flight-review.png", "flight-frames.json"))
    if args.input.resolve() in destinations:
        parser.error("Input would be overwritten by a generated file; choose another output directory")
    try:
        for index, height in zip(range(10, 14), (11, 12, 13, 12)):
            with Image.open(args.exhaust_directory / f"exhaust-{index}.png") as exhaust:
                if exhaust.size != (5, height):
                    raise ValueError(f"exhaust-{index}.png must be 5 x {height}")
        prepare(args.input, args.output, review_output, args.exhaust_directory,
                args.background, args.black_threshold)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
