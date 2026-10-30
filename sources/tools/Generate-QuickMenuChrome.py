"""Build quick-menu chrome from a generated tile quantized to legacy menu greys.

The committed tile was generated with docs/assets/issue-625/test-colony.png as
the style reference, then quantized to greys sampled from its right-hand menu.
"""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "content/standard/images"
TILE = Image.open(OUTPUT / "quick-chrome-metal-tile.png").convert("RGBA")
LIGHT = (170, 170, 170, 255)
SHADE = (105, 105, 105, 255)


def textured(size):
    image = Image.new("RGBA", size)
    for y in range(0, size[1], TILE.height):
        for x in range(0, size[0], TILE.width):
            image.paste(TILE, (x, y))
    return image


def chrome(size, *, horizontal_edges=True, vertical_edges=True):
    width, height = size
    image = textured(size)
    draw = ImageDraw.Draw(image)
    if horizontal_edges:
        draw.line((0, 0, width - 1, 0), fill=LIGHT)
        draw.line((0, height - 1, width - 1, height - 1), fill=SHADE)
    if vertical_edges:
        draw.line((0, 0, 0, height - 1), fill=LIGHT)
        draw.line((width - 1, 0, width - 1, height - 1), fill=SHADE)
    return image


def save(image, name):
    image.save(OUTPUT / name)


rail = chrome((82, 64), horizontal_edges=False)
save(rail, "quick-chrome-rail.png")
save(chrome((56, 64), horizontal_edges=False), "quick-chrome-left-column.png")
Image.new("RGBA", (56, 1), SHADE).save(OUTPUT / "quick-chrome-separator.png")
save(chrome((56, 44)), "quick-chrome-corner.png")
bottom_corner = chrome((56, 44), horizontal_edges=False)
ImageDraw.Draw(bottom_corner).line((0, 43, 55, 43), fill=SHADE)
save(bottom_corner, "quick-chrome-bottom-corner.png")
save(chrome((24, 218)), "quick-chrome-vertical.png")
save(chrome((196, 24)), "quick-chrome-header.png")

screen = Image.new("RGBA", (196, 218))
source = TILE.load()
pixels = screen.load()
for y in range(screen.height):
    for x in range(screen.width):
        grain = (source[x % TILE.width, y % TILE.height][0] - 138) // 4
        pixels[x, y] = (11 + grain, 20 + grain, 34 + grain, 203)
draw = ImageDraw.Draw(screen)
draw.rectangle((0, 0, 195, 217), outline=(133, 139, 146, 230))
draw.rectangle((2, 2, 193, 215), outline=(59, 69, 80, 220))
save(screen, "quick-overlay-screen.png")


def button_icon(source_name, output_name):
    icon = Image.open(OUTPUT / source_name).convert("RGBA")
    canvas = Image.new("RGBA", (47, 38))
    canvas.alpha_composite(icon, ((47 - icon.width) // 2, (38 - icon.height) // 2))
    save(canvas, output_name)


button_icon("quick-asteroid-icon.png", "quick-asteroid-menu-icon-v2.png")
button_icon("quick-visual-menu-icon-v2.png", "quick-visual-menu-icon-v3.png")
