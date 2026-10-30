"""Slice newly generated OpenFA art and register deterministic portable PNG resources.

Inputs are original ImageGen outputs, never original-game artwork. See the
saved generation-prompts.json for the prompts and source roles.
"""
import argparse
import itertools
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance


def build(atlas_path, menu_path):
    root = Path(__file__).resolve().parent.parent
    content = root / "content/standard"
    output = content / "images/bootstrap"
    output.mkdir(parents=True, exist_ok=True)
    resources = []

    def save(image, name, resource_id):
        image.convert("RGBA").save(output / (name + ".png"))
        resources.append(dict(id=resource_id, type="ui-image", path="images/bootstrap/" + name + ".png"))

    atlas = Image.open(atlas_path).convert("RGBA")
    names = ["cpu", "solar", "air", "food", "water", "transporter"]
    widths = [110, 44, 64, 90, 64, 64]
    sprites = []
    for index, (name, width) in enumerate(zip(names, widths)):
        column, row = index % 3, index // 3
        cell = atlas.crop((column * atlas.width // 3, row * atlas.height // 2,
                           (column + 1) * atlas.width // 3, (row + 1) * atlas.height // 2))
        mask = cell.getchannel("A").point(lambda value: 255 if value >= 160 else 0)
        cell = cell.crop(mask.getbbox())
        cell = cell.resize((width, max(1, round(cell.height * width / cell.width))), Image.Resampling.LANCZOS)
        sprites.append(cell)
        save(cell, name, "openfa:asset/bootstrap/" + name)
    construction = ImageEnhance.Color(sprites[0]).enhance(0.1)
    draw = ImageDraw.Draw(construction)
    draw.line((4, construction.height - 8, construction.width - 5, 12), fill="#efb958", width=2)
    draw.line((4, 12, construction.width - 5, construction.height - 8), fill="#efb958", width=2)
    save(construction, "construction", "openfa:asset/bootstrap/construction")

    menu = Image.open(menu_path).convert("RGBA").resize((640, 480), Image.Resampling.LANCZOS)
    save(menu.crop((0, 0, 320, 480)), "menu-left", "openfa:asset/bootstrap/frontend/edge")
    save(menu.crop((320, 0, 640, 480)), "menu-right", "openfa:asset/bootstrap/frontend/menu-base")
    save(Image.new("RGBA", (1, 1)), "menu-dome", "openfa:asset/bootstrap/frontend/dome")
    metal = menu.crop((390, 200, 510, 320))
    panel_source = Image.open(root / "docs/assets/bootstrap/source-panel.png").convert("RGBA")
    save(panel_source.resize((192,144), Image.Resampling.LANCZOS), "panel", "openfa:asset/bootstrap/panel")
    metal = panel_source.crop((panel_source.width // 3, panel_source.height // 3,
                              panel_source.width * 2 // 3, panel_source.height * 2 // 3))

    def panel(width, height, selected=False):
        image = ImageEnhance.Brightness(metal.resize((width, height))).enhance(1.7 if selected else 0.9)
        d = ImageDraw.Draw(image)
        d.rounded_rectangle((0, 0, width - 1, height - 1), radius=4,
                            outline="#ddb16d" if selected else "#67818a", width=2)
        d.line((5, height - 4, width - 5, height - 4), fill="#091119", width=1)
        return image

    ui_atlas = Image.open(root / "docs/assets/bootstrap/source-ui-icons.png").convert("RGBA")
    symbols = []
    for index in range(64):
        x, y = index % 8, index // 8
        cell = ui_atlas.crop((x * ui_atlas.width // 8, y * ui_atlas.height // 8,
                              (x + 1) * ui_atlas.width // 8, (y + 1) * ui_atlas.height // 8))
        box = cell.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
        symbols.append(cell.crop(box) if box else cell)

    def icon(symbol, size):
        image = Image.new("RGBA", size)
        art = symbols[symbol].copy()
        art.thumbnail((size[0] - 8, size[1] - 6), Image.Resampling.LANCZOS)
        image.alpha_composite(art, ((size[0] - art.width) // 2, (size[1] - art.height) // 2))
        return image

    gameplay_symbols = {0:16,1:18,2:30,3:31,4:27,5:26,6:31,7:23,8:62,9:63,
        10:41,11:14,12:55,13:6,14:0,15:3,16:2,17:39,18:5,19:8,20:7,21:4,
        22:25,23:9,24:12,25:13,26:52,27:53,29:2,30:3,34:11,39:11,40:26,
        41:51,42:42,43:53,44:51,45:16,46:14,47:22,48:36,50:52,51:42,
        52:51,53:36,54:32,55:1,56:28,57:51,58:18,59:11,60:14,62:13,
        64:41,65:19,66:20,67:14,68:31,69:21,70:45,72:42,73:18,74:36}
    frontend_symbols = {0:19,1:24,2:59,3:56,4:57,5:22,6:58}
    for area in ["frontend", "gameplay"]:
        button_id = "buttons" if area == "gameplay" else "button"
        size = (48, 40) if area == "gameplay" else (211, 48)
        for state in ["normal", "selected", "pressed", "disabled", "hover"]:
            skin = panel(*size, state in ["selected", "hover"])
            if state == "pressed":
                skin = ImageEnhance.Brightness(skin).enhance(0.65)
            if state == "disabled":
                skin = ImageEnhance.Brightness(ImageEnhance.Color(skin).enhance(0)).enhance(0.55)
            suffix = "" if state == "normal" else "/" + state
            save(skin, area + "-button-" + state, "openfa:asset/bootstrap/" + area + "/" + button_id + suffix)
        mapping = gameplay_symbols if area == "gameplay" else frontend_symbols
        for frame, symbol in mapping.items():
            art = icon(symbol, (47, 38) if area == "gameplay" else (40, 40))
            resource = "openfa:asset/bootstrap/" + area + "/icons/frame-" + str(frame)
            save(art, area + "-icon-" + str(frame), resource)
            disabled = ImageEnhance.Brightness(ImageEnhance.Color(art).enhance(0)).enhance(0.45)
            save(disabled, area + "-icon-" + str(frame) + "-disabled", resource + "/disabled")
    for name, symbol in [("confirm",17),("cancel",18),("enabled",17),("disabled",18)]:
        image = panel(29,30)
        image.alpha_composite(icon(symbol,(29,30)))
        save(image, "control-" + name, "openfa:asset/bootstrap/control/" + name)
    # The research launcher is a complete button sprite, without a separate icon child.
    for frame in [2,3]:
        research = panel(48,40,frame == 3)
        research.alpha_composite(icon(10,(48,40)))
        resource = "openfa:asset/bootstrap/gameplay/buttons/frame-" + str(frame)
        save(research, "gameplay-research-" + str(frame), resource)
        save(research, "gameplay-research-" + str(frame) + "-pressed", resource + "/pressed")
    for asset, mapping in {
        "gameplay/control-icons": {0:62,1:62,2:62,3:63,4:63,5:63},
        "frontend/scroll-icons": {0:62,1:62,2:62,3:63,4:63,5:63},
        "gameplay/scroll": {7:62,8:62,9:62,10:63,11:63,12:63,19:30,20:30,21:30,
                             22:31,23:31,24:31},
    }.items():
        for frame, symbol in mapping.items():
            art = panel(30,30)
            art.alpha_composite(icon(symbol,(30,30)))
            resource = "openfa:asset/bootstrap/" + asset + "/frame-" + str(frame)
            name = asset.replace("/", "-") + "-" + str(frame)
            save(art, name, resource)
            save(ImageEnhance.Brightness(ImageEnhance.Color(art).enhance(0)).enhance(0.45),
                 name + "-disabled", resource + "/disabled")
    for frame in range(8):
        edge = Image.new("RGBA", (531, 60))
        if frame == 0:
            edge.alpha_composite(panel(531, 37), (0, 0))
        save(edge, "gameplay-edge-" + str(frame), "openfa:asset/bootstrap/gameplay/edge/frame-" + str(frame))
    for name, size in [("menu-edge", (109,200)), ("menu-base", (558,480)), ("catalogue-tile", (96,96))]:
        save(panel(*size), "gameplay-" + name, "openfa:asset/bootstrap/gameplay/" + name)

    # Preserve the existing management UI indices; all other colours are new.
    reserved = {0:(2,3,7),8:(5,8,18),48:(28,30,34),75:(13,28,55),100:(18,44,62),
                120:(19,52,31),180:(55,14,14),200:(56,40,10),220:(52,57,63),225:(36,39,43),
                226:(32,32,32),227:(19,19,19),228:(17,35,18),229:(41,33,21),230:(51,54,57),
                235:(7,8,23),240:(11,18,50),245:(52,8,10)}
    values = [(0,0,0)] * 256
    available = iter(index for index in range(256) if index not in reserved and not 128 <= index < 160)
    for colour in itertools.product([0,16,32,47,63], repeat=3):
        values[next(available)] = colour
    for index, colour in reserved.items():
        values[index] = colour
    for index in range(128,160):
        shade = index - 128
        values[index] = (12 + shade, 10 + shade, 8 + shade)
    palette = Image.new("RGBA", (256, 1))
    palette.putdata([tuple((v * 255 + 31) // 63 for v in colour) + (255,) for colour in values])
    save(palette, "palette", "openfa:asset/bootstrap/palette")
    (root / "docs/assets/bootstrap/terrain.pal").write_bytes(bytes(v for colour in values for v in colour))

    manifest_path = content / "manifest.json"
    # Preserve all unrelated formatting and localized characters.
    original = manifest_path.read_text(encoding="utf-8")
    start = original.index("[", original.index('"resources"')) + 1
    cursor = start
    preserved = []
    obsolete = []
    decoder = json.JSONDecoder()
    while True:
        while original[cursor].isspace() or original[cursor] == ",":
            cursor += 1
        if original[cursor] == "]":
            break
        entry, end = decoder.raw_decode(original, cursor)
        if not entry.get("path", "").startswith("images/bootstrap/"):
            preserved.append("    " + original[cursor:end])
        elif entry["path"] not in {resource["path"] for resource in resources}:
            obsolete.append(content / entry["path"])
        cursor = end
    additions = ["\n".join("    " + line for line in json.dumps(entry, indent=2).splitlines()) for entry in resources]
    manifest_path.write_text(original[:start] + "\n" + ",\n".join(preserved + additions) +
                             "\n  " + original[cursor:], encoding="utf-8")
    for path in obsolete:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sprite_atlas", type=Path)
    parser.add_argument("menu_artwork", type=Path)
    args = parser.parse_args()
    build(args.sprite_atlas, args.menu_artwork)
