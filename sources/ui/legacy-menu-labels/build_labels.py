"""Author flat shade-only frontend labels; never sample legacy image pixels."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent
MEDIA = ROOT / 'gallery/media/ui/legacy-menu-labels'
STATES = {'idle': (48, 208), 'hover': (40, 224), 'selected': (48, 216),
          'pressed': (64, 170), 'off': (48, 150)}
LABELS = {
    'en': {'intro': 'INTRO', 'tutorials': 'TUTORIALS', 'new-game': 'NEW GAME',
           'saved-game': 'SAVED GAME', 'multiplayer': 'MULTIPLAYER', 'options': 'GAME OPTIONS',
           'quit': 'QUIT', 'resume': 'PLAY COLONY', 'no-network': 'NO NETWORK'},
    'pl': {'intro': 'INTRO', 'tutorials': 'SAMOUCZKI', 'new-game': 'NOWA GRA',
           'saved-game': 'WCZYTAJ GRĘ', 'multiplayer': 'GRA SIECIOWA', 'options': 'OPCJE GRY',
           'quit': 'WYJŚCIE', 'resume': 'GRAJ W KOLONII', 'no-network': 'BRAK SIECI'}}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8', newline='\n')


def font():
    return ImageFont.truetype(str(SOURCE / 'font/NotoSerif-Bold.ttf'), 14)


def outlined(text, luminance=208):
    face = font()
    bounds = face.getbbox(text, stroke_width=1)
    result = Image.new('RGBA', (bounds[2] - bounds[0], bounds[3] - bounds[1]))
    ImageDraw.Draw(result).text((-bounds[0], -bounds[1]), text, font=face,
                               fill=(luminance,) * 3 + (255,), stroke_width=1, stroke_fill=(0, 0, 0, 255))
    return result


def label(text, state='idle', two_lines=None):
    result = Image.new('RGBA', (184, 46))
    lines = [text] if two_lines is None else [text, two_lines]
    for n, line in enumerate(lines):
        ink = outlined(line, STATES[state][1])
        assert ink.width <= 170, ('Label exceeds native well', line, ink.width)
        cy = 23 if len(lines) == 1 else 17 + n * 13
        result.alpha_composite(ink, (98 - ink.width // 2, cy - ink.height // 2))
    return result


def socket(state):
    """Independent circular bezel; shallow wear stays confined to the metal."""
    scale = 4
    image = Image.new('RGBA', (44 * scale, 46 * scale))
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            dx, dy = x / scale - 21, y / scale - 23
            radius = (dx * dx + dy * dy) ** .5
            if radius > 21:
                continue
            light = (-dx - dy) / 42
            value = (58 if radius > 20 else 152 + 70 * light if radius > 17 else 22)
            if 17 < radius < 20 and (x * 47 + y * 29) % 113 == 0:
                value -= 32
            if state == 'pressed':
                value -= 12
            value = max(0, min(255, round(value)))
            pixels[x, y] = (value, value, value, 255)
    return image.resize((44, 46), Image.Resampling.LANCZOS)


def atlas(destination):
    face = font()
    chars = list(range(32, 127)) + list(range(160, 384))
    image = Image.new('RGBA', (384, 24 * ((len(chars) + 15) // 16)))
    draw = ImageDraw.Draw(image)
    glyphs = []
    for i, codepoint in enumerate(chars):
        x, y = i % 16 * 24, i // 16 * 24
        draw.text((x + 3, y + 17), chr(codepoint), font=face, anchor='ls',
                  fill=(208, 208, 208, 255), stroke_width=1, stroke_fill=(0, 0, 0, 255))
        glyphs.append(dict(codepoint=codepoint, rect=[x, y, 24, 24],
                           advance=round(face.getlength(chr(codepoint))), offset=[-3, -17]))
    image.save(destination / 'font-atlas.png')
    save_json(destination / 'font.json', dict(font='Noto Serif Bold', size=14, line_height=16,
              baseline=17, atlas='font-atlas.png', color_embedded=True, glyphs=glyphs,
              license='OFL.txt', note='Separate open-font interpretation, not recovered FONT.256 pixels'))


def preview(destination, panel_path):
    # Only existing authored OpenFA artwork is used as the preview background.
    with Image.open(panel_path) as image:
        panel = image.convert('RGBA')
    assert panel.size == (320, 480)
    output = Image.new('RGBA', (640, 480), (104, 106, 108, 255))
    output.alpha_composite(panel, (320, 0))
    # A small neutral left column keeps this a label study, not a new sphere kit.
    draw = ImageDraw.Draw(output)
    draw.text((22, 20), 'OPENFA / LABEL STUDY', font=font(), fill=(220, 220, 220))
    draw.text((22, 48), 'Native canvas: 640 x 480', font=font(), fill=(210, 210, 210))
    colors = [(205, 127, 18), (17, 21, 143), (0, 85, 12), (182, 39, 17),
              (119, 35, 153), (19, 83, 151), (173, 155, 20)]
    for locale in LABELS:
        page = output.copy()
        for i, key in enumerate(['intro', 'tutorials', 'new-game', 'saved-game', 'multiplayer', 'options', 'quit']):
            row = Image.open(destination / 'rows/row-amber-idle.png').convert('RGBA')
            d = ImageDraw.Draw(row)
            d.ellipse((5, 7, 37, 39), fill=colors[i], outline=(15, 15, 15), width=2)
            page.alpha_composite(row, (429, 27 + i * 64))
            text = label(LABELS[locale][key], two_lines=LABELS[locale]['no-network'] if key == 'multiplayer' else None)
            page.alpha_composite(text, (456, 28 + i * 64))
        page.convert('RGB').save(destination / f'preview-{locale}.png')
    sheet = Image.new('RGB', (640, 240), (105, 107, 109))
    for n, state in enumerate(STATES):
        sheet.paste(Image.open(destination / 'rows' / f'row-amber-{state}.png'), (150, n * 48),
                    Image.open(destination / 'rows' / f'row-amber-{state}.png'))
        text = label('GAME OPTIONS', state)
        sheet.paste(text, (177, n * 48 + 1), text)
        ImageDraw.Draw(sheet).text((15, n * 48 + 17), state, font=font(), fill=(230, 230, 230))
    sheet.save(destination / 'states.png')


def generate(destination):
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'rows').mkdir(exist_ok=True)
    for state, (opacity, _) in STATES.items():
        shade = Image.new('RGBA', (184, 46), (0, 0, 0, opacity))
        shade.save(destination / f'label-shade-{state}.png')
        ring = socket(state)
        ring.save(destination / f'socket-{state}.png')
        row = Image.new('RGBA', (211, 48))
        row.alpha_composite(shade, (27, 1))
        row.alpha_composite(ring, (0, 0))
        for theme in ['amber', 'green', 'blue', 'cyan']:
            row.save(destination / 'rows' / f'row-{theme}-{state}.png')
        for locale, labels in LABELS.items():
            folder = destination / locale
            folder.mkdir(exist_ok=True)
            for key, text in labels.items():
                label(text, state).save(folder / f'{key}-{state}.png')
            label(labels['multiplayer'], state, labels['no-network']).save(folder / f'multiplayer-no-network-{state}.png')
    atlas(destination)
    (destination / 'OFL.txt').write_bytes((SOURCE / 'font/OFL.txt').read_bytes())
    (destination / 'evidence.json').write_bytes((SOURCE / 'legacy-evidence.json').read_bytes())
    panel = ROOT / 'gallery/media/ui/legacy-main-menu-refined/native/layer-menu-base.png'
    preview(destination, panel)
    evidence = dict(issue=206, generator_sha256=sha(Path(__file__)), font_sha256=sha(SOURCE / 'font/NotoSerif-Bold.ttf'),
        pillow=pillow_version, freetype=features.version('freetype2'),
        reference_evidence_sha256=sha(SOURCE / 'legacy-evidence.json'),
        license_sha256=sha(SOURCE / 'font/OFL.txt'), preview_panel_sha256=sha(panel),
        legacy_evidence='game docs/legacy/fe-tag-menu-usage.md: BOX 184x46 at (456,28+64n), style 0xFFFF240D',
        font_interpretation='Noto Serif Bold 14px, greyscale fill and black 1px edge; not exact legacy font',
        composition=dict(canvas=[640,480], row_anchor=[429,27], row_pitch=64, shade_anchor=[456,28],
                         text_center_x=554, text_center_y=51, socket_center=[450,50],
                         cap_bounds=[434,34,32,32], text_safe_bounds=[462,31,172,40]),
        integration=['Use either row PNG or separate shade/socket, not both.',
                     'Remove previous framed row sprite and label-shade rectangle before applying these assets.',
                     'Normal shade alpha 48 approximates 208/256 brightness; original palette quantization is not reproduced.',
                     'No neon hue tint on rows: the four theme aliases are intentionally identical.',
                     'Keep localized live text or use supplied glyph atlas; EN/PL string PNGs are optional.',
                     'States beyond normal are authored interaction feedback, not recovered legacy behavior.'],
        files={p.relative_to(destination).as_posix():sha(p) for p in sorted(destination.rglob('*')) if p.is_file() and p.name!='catalog.json'})
    save_json(destination / 'catalog.json', evidence)
    print('LEGACY_MENU_LABELS_GENERATED', len(evidence['files']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=MEDIA)
    generate(parser.parse_args().output.resolve())
