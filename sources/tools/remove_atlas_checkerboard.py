"""Remove border-connected neutral checkerboard pixels from a generated atlas.

Project authoring utility; requires Pillow and NumPy. It preserves foreground
RGB and existing alpha. Inspect the resulting atlas before publishing it.
"""
import argparse
from collections import deque

import numpy as np
from PIL import Image


def clean(source, destination):
    pixels = np.array(Image.open(source).convert("RGBA"))
    rgb = pixels[:, :, :3].astype(np.int16)
    candidate = ((rgb.max(axis=2) - rgb.min(axis=2) <= 14)
                 & (rgb.min(axis=2) >= 65) & (rgb.max(axis=2) <= 240))
    height, width = candidate.shape
    removed = np.zeros((height, width), dtype=bool)
    queue = deque()

    def seed(x, y):
        if candidate[y, x] and not removed[y, x]:
            removed[y, x] = True
            queue.append((x, y))

    for x in range(width):
        seed(x, 0)
        seed(x, height - 1)
    for y in range(height):
        seed(0, y)
        seed(width - 1, y)
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                seed(nx, ny)
    pixels[removed] = 0
    Image.fromarray(pixels).save(destination)
    print(f"{width}x{height}: removed {removed.sum()} background pixels; "
          f"retained {np.count_nonzero(pixels[:, :, 3])} foreground pixels")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    clean(args.source, args.destination)
