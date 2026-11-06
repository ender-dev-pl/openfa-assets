"""Check the delivered label contract and independently repeat the Python render."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources/ui/legacy-menu-labels'
MEDIA = ROOT / 'gallery/media/ui/legacy-menu-labels'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(folder):
    catalog = json.loads((folder / 'catalog.json').read_text())
    assert catalog['generator_sha256'] == sha(SOURCE / 'build_labels.py')
    assert catalog['font_sha256'] == sha(SOURCE / 'font/NotoSerif-Bold.ttf')
    assert catalog['license_sha256'] == sha(SOURCE / 'font/OFL.txt') == sha(folder / 'OFL.txt')
    assert catalog['reference_evidence_sha256'] == sha(SOURCE / 'legacy-evidence.json') == sha(folder / 'evidence.json')
    assert catalog['composition']['socket_center'] == [450, 50]
    assert catalog['composition']['text_center_x'] == 554
    for name, digest in catalog['files'].items():
        assert sha(folder / name) == digest, name
    for state in ['idle', 'hover', 'selected', 'pressed', 'off']:
        with Image.open(folder / f'label-shade-{state}.png') as shade:
            assert shade.size == (184, 46) and all(lo == hi for lo, hi in shade.getextrema())
            if state == 'idle':
                # Compositing must preserve the substrate, approximating legacy shade row 13.
                for value in [0, 64, 128, 200, 255]:
                    base = Image.new('RGBA', (184, 46), (value,) * 3 + (255,))
                    base.alpha_composite(shade)
                    assert abs(base.getpixel((90, 20))[0] - value * 208 / 256) <= 1
        rows = [folder / 'rows' / f'row-{theme}-{state}.png' for theme in ['amber', 'green', 'blue', 'cyan']]
        assert len({sha(p) for p in rows}) == 1, 'Unexpected theme-colored neon in label'
        with Image.open(rows[0]) as image:
            assert image.size == (211, 48)
            for x in range(44, 211):
                assert image.getpixel((x, 0))[3] == image.getpixel((x, 47))[3] == 0
                assert image.getpixel((x, 23))[:3] == (0, 0, 0), 'Frame/rail returned'
        for locale in ['en', 'pl']:
            for path in (folder / locale).glob(f'*-{state}.png'):
                with Image.open(path) as ink:
                    bounds = ink.getbbox()
                    assert ink.size == (184, 46) and bounds
                    assert bounds[0] >= 6 and bounds[2] <= 178 and bounds[1] >= 2 and bounds[3] <= 44
    glyphs = json.loads((folder / 'font.json').read_text())['glyphs']
    assert len(glyphs) == len({g['codepoint'] for g in glyphs}) == 319
    assert all(ord(c) in {g['codepoint'] for g in glyphs} for c in 'ĄĆĘŁŃÓŚŹŻąćęłńóśźż')
    with Image.open(folder / 'font-atlas.png') as image:
        for glyph in glyphs:
            if glyph['codepoint'] not in [32, 160]:
                x, y, w, h = glyph['rect']
                assert image.crop((x, y, x + w, y + h)).getbbox(), glyph
    return catalog


def main():
    current = verify(MEDIA)
    spec = importlib.util.spec_from_file_location('menu_labels', SOURCE / 'build_labels.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(dir=ROOT / 'artifacts') as directory:
        module.generate(Path(directory))
        repeated = verify(Path(directory))
        assert repeated == current, 'Non-deterministic output/provenance'
    print('MENU_LABELS_VERIFIED', len(current['files']), 'files; 319 glyphs; EN/PL; shade/anchors; repeat render identical')


if __name__ == '__main__':
    main()
