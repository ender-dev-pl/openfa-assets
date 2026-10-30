"""Inspect PNG alpha and create portable review videos for the pyro assets."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/effects/pyro'
VARIANTS = ['compact', 'rising', 'asymmetric']


def background(size, checker=False):
    image = Image.new('RGB', size, '#0b0e14')
    if checker:
        draw = ImageDraw.Draw(image)
        for y in range(0, size[1], 48):
            for x in range(0, size[0], 48):
                draw.rectangle((x, y, x + 47, y + 47), fill='#292f3a' if (x // 48 + y // 48) % 2 else '#414957')
    return image


def frame_image(variant, frame, size, checker=False):
    image = Image.open(ROOT / variant / f'frames/{frame:03}.png').convert('RGBA')
    image = image.resize(size, Image.Resampling.LANCZOS)
    result = background(size, checker)
    result.paste(image, (0, 0), image)
    return result


def encode(ffmpeg, output, images, size=(300, 300), fps=24):
    command = [ffmpeg, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{size[0]}x{size[1]}', '-r', str(fps), '-i', '-', '-an', '-c:v', 'libx264',
               '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for image in images:
            process.stdin.write(image.tobytes())
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError('FFmpeg failed')


def comparison_frames():
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
    for repeat in range(2):
        for frame in range(1, 97):
            result = background((960, 820)); draw = ImageDraw.Draw(result)
            draw.text((20, 16), '3D EXPLOSIONS / 300 x 300 / FIRE, SMOKE, ALPHA', font=font, fill='#ffb45d')
            for index, variant in enumerate(VARIANTS):
                x = index * 320 + 10
                draw.text((x + 10, 65), variant.upper(), font=font, fill='white')
                result.paste(frame_image(variant, frame, (300, 300)), (x, 110))
                result.paste(frame_image(variant, frame, (300, 300), True), (x, 450))
            draw.text((20, 775), f'{(frame - 1) / 24:.2f} s / lower row: alpha over checkerboard', font=font, fill='#aeb6c4')
            yield result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--ffmpeg', required=True)
    args = parser.parse_args()
    verification = {}
    contact = background((1500, 1120)); draw = ImageDraw.Draw(contact)
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 26)
    for row, variant in enumerate(VARIANTS):
        directory = ROOT / variant
        files = sorted((directory / 'frames').glob('*.png'))
        assert len(files) == 96, (variant, len(files))
        coverage = []
        edge_max = 0
        for path in files:
            image = Image.open(path)
            assert image.size == (300, 300) and image.mode == 'RGBA'
            alpha = np.asarray(image)[:, :, 3]
            edge_max = max(edge_max, int(alpha[0].max()), int(alpha[-1].max()),
                           int(alpha[:, 0].max()), int(alpha[:, -1].max()))
            coverage.append(dict(sum=int(alpha.sum()), partial=int(((alpha > 0) & (alpha < 255)).sum())))
        assert coverage[0]['sum'] == 0 and coverage[-1]['sum'] == 0, (variant, coverage[0], coverage[-1])
        assert max(item['partial'] for item in coverage) > 1000
        # Expansion can increase total coverage while local density falls.
        # The late dissipation phase must reduce coverage before the blank end.
        assert coverage[89]['sum'] < coverage[47]['sum']
        assert coverage[94]['sum'] < coverage[89]['sum']
        assert edge_max == 0, (variant, 'Clipped animation', edge_max)
        verification[variant] = dict(frames=96, resolution=[300, 300], rgba=True,
            first_last_transparent=True, fractional_alpha=True, transparent_frame_edges=True, coverage=coverage)
        encode(args.ffmpeg, directory / 'explosion.mp4',
               (frame_image(variant, frame, (300, 300)) for frame in range(1, 97)))
        draw.text((20, row * 370 + 8), variant.upper(), font=font, fill='#ffb45d')
        for col, frame in enumerate([8, 16, 30, 48, 80]):
            contact.paste(frame_image(variant, frame, (300, 300), True), (col * 300, row * 370 + 40))
            draw.text((col * 300 + 20, row * 370 + 340), f'{(frame - 1) / 24:.2f} s', font=font, fill='white')
    contact.save(ROOT / 'contact.png')
    encode(args.ffmpeg, ROOT / 'variants.mp4', comparison_frames(), (960, 820))
    previews = [image for i, image in enumerate(comparison_frames()) if i < 96 and i % 2 == 0]
    previews[0].save(ROOT / 'preview.gif', save_all=True, append_images=previews[1:], duration=[80, 80, 90] * 16, loop=0, disposal=2)
    (ROOT / 'rgba-verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    manifests = {}
    for variant in VARIANTS:
        paths = [ROOT / variant / 'explosion.blend', ROOT / variant / 'explosion.mp4']
        manifests[variant] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    peak_hashes = [hashlib.sha256((ROOT / variant / 'frames/016.png').read_bytes()).hexdigest() for variant in VARIANTS]
    assert len(set(peak_hashes)) == 3, 'Variant renders must be distinct'
    generator = Path(__file__).with_name('build_pyro_explosions.py')
    (ROOT / 'manifest.json').write_text(json.dumps(dict(issue=1035, files=manifests,
        final_generator_sha256=hashlib.sha256(generator.read_bytes()).hexdigest(), distinct_variant_renders=True), indent=2) + '\n')
    print('PYRO_PACKAGE_OK')


if __name__ == '__main__':
    main()
