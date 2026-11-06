"""Convert an animated transparent GIF to fixed-size menu frames (Pillow required)."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageSequence, ImageChops, ImageDraw, ImageOps


def create(source, output):
    with Image.open(source) as image:
        frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(image)]
        durations = []
        for index in range(image.n_frames):
            image.seek(index)
            durations.append(max(10, image.info.get("duration", 100)))
    for frame in frames:
        r, g, b, alpha = frame.split()
        maximum = ImageChops.lighter(ImageChops.lighter(r, g), b)
        mask = maximum.point(lambda value: 255 if value <= 20 else 0)
        padded = ImageOps.expand(mask, border=1, fill=255)
        ImageDraw.floodfill(padded, (0, 0), 128)
        mask = padded.crop((1, 1, frame.width + 1, frame.height + 1))
        frame.putalpha(ImageChops.multiply(alpha, mask.point(lambda value: 0 if value == 128 else 255)))
    bounds = [frame.getchannel("A").getbbox() for frame in frames]
    if any(bound is None for bound in bounds):
        raise ValueError("Every frame must contain a visible object")
    crop = (min(b[0] for b in bounds), min(b[1] for b in bounds),
            max(b[2] for b in bounds), max(b[3] for b in bounds))
    size = (41, 138)
    scale = min(size[0] / (crop[2] - crop[0]), size[1] / (crop[3] - crop[1]))
    fitted = (round((crop[2] - crop[0]) * scale), round((crop[3] - crop[1]) * scale))
    sheet = Image.new("RGBA", (size[0] * 16, size[1] * ((len(frames) + 15) // 16)))
    metadata, sequence, previews = [], [], []
    for index, (frame, duration) in enumerate(zip(frames, durations)):
        canvas = Image.new("RGBA", size)
        canvas.alpha_composite(frame.crop(crop).resize(fitted, Image.Resampling.LANCZOS),
                               ((size[0] - fitted[0]) // 2, (size[1] - fitted[1]) // 2))
        x, y = index % 16 * size[0], index // 16 * size[1]
        sheet.alpha_composite(canvas, (x, y))
        metadata.append(dict(index=index, x=x, y=y, width=41, height=138, canvasWidth=41, canvasHeight=138))
        sequence.extend([index] * (duration // 10))
        previews.append(canvas)
    output.mkdir(parents=True, exist_ok=True)
    sheet.save(output / "menu-preview.png")
    (output / "menu-animation.json").write_text(json.dumps(dict(frames=metadata, sequence=sequence), indent=2))
    previews[0].save(output / "menu-review.gif", save_all=True, append_images=previews[1:],
                     duration=durations, loop=0, disposal=2)
    print(f"{len(frames)} frames; shared crop {crop}; fitted size {fitted}; duration {sum(durations)} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    create(args.source, args.output)
