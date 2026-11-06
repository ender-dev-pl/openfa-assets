"""Verify 300px RGBA airburst frames and package native-size review media."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from package_pyro_explosions import background, encode


def portable_font(size):
    """Resolve installed fonts without a machine-specific filesystem path."""
    for name in ('arial.ttf', 'segoeui.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/effects/pyro/airborne'
REFERENCE = ROOT.parent / 'reference/xs01'


def composed(frame, checker=False):
    image = Image.open(ROOT / f'frames/{frame:03}.png').convert('RGBA')
    result = background((300, 300), checker); result.paste(image, (0, 0), image)
    return result


def legacy(frame):
    index = min(25, int(((frame - 1) / 30) / .05))
    image = Image.open(REFERENCE / f'legacy-{index:02}.png').convert('RGBA')
    image = image.crop((85, 24, 230, 156))
    result = background((300, 300))
    image.thumbnail((280, 280), Image.Resampling.NEAREST)
    result.paste(image, ((300 - image.width) // 2, (300 - image.height) // 2), image)
    return result


def review_frames():
    font = portable_font( 19)
    for _ in range(3):
        for frame in range(1, 41):
            image = background((900, 380)); draw = ImageDraw.Draw(image)
            for index, (title, picture) in enumerate([('XS01 / legacy', legacy(frame)),
                ('3D / airborne', composed(frame)), ('3D / alpha check', composed(frame, True))]):
                draw.text((index * 300 + 15, 12), title, font=font, fill='#ffca86')
                image.paste(picture, (index * 300, 45))
            draw.text((15, 350), f'{(frame - 1) / 30:.2f} s / character reference; independent framing', font=font, fill='#aab1bc')
            yield image


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--ffmpeg', required=True)
    args = parser.parse_args()
    paths = sorted((ROOT / 'frames').glob('*.png')); assert len(paths) == 40
    coverage = []; edge_max = 0; partial_max = 0
    for path in paths:
        image = Image.open(path); assert image.size == (300, 300) and image.mode == 'RGBA'
        alpha = np.asarray(image)[:, :, 3]
        coverage.append(int(alpha.sum())); partial_max = max(partial_max, int(((alpha > 0) & (alpha < 255)).sum()))
        edge_max = max(edge_max, int(alpha[0].max()), int(alpha[-1].max()), int(alpha[:, 0].max()), int(alpha[:, -1].max()))
    assert coverage[0] == 0 and coverage[-1] == 0 and edge_max == 0
    assert partial_max > 1000 and coverage[36] < coverage[22]
    encode(args.ffmpeg, ROOT / 'explosion.mp4', (composed(f) for f in range(1, 41)), fps=30)
    encode(args.ffmpeg, ROOT / 'comparison.mp4', review_frames(), (900, 380), fps=30)
    gif = [composed(frame, True) for frame in range(1, 41)]
    gif[0].save(ROOT / 'preview.gif', save_all=True, append_images=gif[1:],
                duration=[30, 30, 40] * 13 + [380], loop=0, disposal=2)
    contact = background((1500, 340)); draw = ImageDraw.Draw(contact)
    font = portable_font( 20)
    for index, frame in enumerate([4, 12, 20, 28, 36]):
        contact.paste(composed(frame, True), (index * 300, 0))
        draw.text((index * 300 + 15, 308), f'{(frame - 1) / 30:.2f} s', font=font, fill='white')
    contact.save(ROOT / 'contact.png')
    result = dict(frames=40, fps=30, resolution=[300, 300], rgba=True, fractional_alpha=True,
                  transparent_endpoints=True, transparent_edges=True, alpha_coverage=coverage,
                  sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in ['explosion.blend', 'explosion.mp4', 'comparison.mp4']})
    (ROOT / 'render-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print('AIRBURST_PACKAGE_OK')


if __name__ == '__main__': main()
