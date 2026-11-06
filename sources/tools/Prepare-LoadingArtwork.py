"""Prepare the user-supplied wordmark and spinning emblem for the bootstrap UI.

Usage: python tools/Prepare-LoadingArtwork.py wordmark.png emblem.gif
Requires Pillow. Outputs belong to the standalone bootstrap package.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

output = Path(__file__).resolve().parents[1] / "content/loadscreen/images"
output.mkdir(parents=True, exist_ok=True)
wordmark = Image.open(sys.argv[1]).convert("RGB")
if wordmark.size != (1672, 941):
    raise ValueError("Expected the supplied 1672 x 941 wordmark")
# Remove only the static oval emblem, preserving the adjacent lettering.
ImageDraw.Draw(wordmark).rectangle((1060, 150, 1295, 508), fill="black")
wordmark = wordmark.crop((300, 50, 1325, 910)).resize((400, 336), Image.Resampling.LANCZOS)
background = Image.new("RGB", (640, 350))
background.paste(wordmark, (120, 0))
background.save(output / "wordmark.png", optimize=True)

animation = Image.open(sys.argv[2])
if animation.n_frames != 60:
    raise ValueError("Expected the supplied 60-frame animation")
sheet = Image.new("RGBA", (90 * 10, 140 * 6))
for index in range(60):
    animation.seek(index)
    if animation.info.get("duration") != 60:
        raise ValueError("Expected 60 ms per frame")
    frame = animation.convert("RGB").crop((80, 0, 560, 620))
    frame = frame.resize((90, 140), Image.Resampling.LANCZOS)
    frame.putalpha(frame.convert("L").point(lambda value: 255 if value > 4 else 0))
    sheet.paste(frame, ((index % 10) * 90, (index // 10) * 140))
sheet.save(output / "emblem-frames.png", optimize=True)
