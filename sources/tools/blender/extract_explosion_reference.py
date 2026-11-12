"""Extract palette-correct legacy explosion frames and quantitative envelopes."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fragile256 import read_sprites, decode_sprite, palette_to_png, GLOBAL_HEADER_SIZE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('installation', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--name', default='XB02', choices=['XB00', 'XB01', 'XB02', 'XS00', 'XS01', 'XS02'])
    parser.add_argument('--frame-ms', type=int, help='Optional animated 300px review at an evidenced cadence')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = args.installation / f'_P/{args.name}.256'
    data, frames, palette, palette_source = read_sprites(source)
    sheet = Image.new('RGB', (5 * 240, ((len(frames) + 4) // 5) * 260), '#11151d')
    draw = ImageDraw.Draw(sheet)
    if palette_source != source.name:
        raise ValueError('Reference requires an embedded, unambiguous palette')
    rgb = palette_to_png(palette)
    union = (min(f.x for f in frames), min(f.y for f in frames),
             max(f.x + f.width for f in frames), max(f.y + f.height for f in frames))
    records = []
    preview = []
    for frame in frames:
        start = GLOBAL_HEADER_SIZE + frame.stream_offset
        pixels = decode_sprite(data[start:start + frame.stream_length], frame.width, frame.height)
        image = Image.new('P', (frame.canvas_width, frame.canvas_height))
        image.putpalette(rgb)
        crop = Image.frombytes('P', (frame.width, frame.height), pixels)
        image.paste(crop, (frame.x, frame.y))
        image.info['transparency'] = 0
        image.save(args.output / f'legacy-{frame.index:02}.png')
        rgba = image.convert('RGBA')
        if args.frame_ms:
            review = Image.new('RGB', (300, 300), '#11151d')
            effect = rgba.crop(union)
            effect.thumbnail((280, 280), Image.Resampling.NEAREST)
            review.paste(effect, ((300 - effect.width) // 2, (300 - effect.height) // 2), effect)
            preview.append(review)
        bounds = rgba.getbbox()
        counts = image.histogram()
        total = sum(counts[1:])
        mean = [sum(counts[i] * rgb[i * 3 + c] for i in range(1, 256)) / max(1, total) for c in range(3)]
        records.append(dict(frame=frame.index, bounds=bounds, pixels=total, mean_rgb=mean))
        x, y = (frame.index % 5) * 240, (frame.index // 5) * 260
        cropped = rgba.crop(union)
        scale = min(232 / cropped.width, 220 / cropped.height)
        enlarged = cropped.resize((round(cropped.width * scale), round(cropped.height * scale)), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (x + (240 - enlarged.width) // 2, y + (235 - enlarged.height) // 2), enlarged)
        draw.text((x + 8, y + 242), f'{args.name} / {frame.index:02}', fill='white')
    sheet.save(args.output / 'legacy-contact.png')
    if preview:
        preview.append(Image.new('RGB', (300, 300), '#11151d'))
        preview[0].save(args.output / 'legacy-preview.gif', save_all=True,
                        append_images=preview[1:], duration=[args.frame_ms] * len(frames) + [350], loop=0, disposal=2)
    manifest = dict(source=f'_P/{args.name}.256', source_sha256=hashlib.sha256(data).hexdigest(),
                    palette_source=palette_source, palette_rgb_sha256=hashlib.sha256(rgb).hexdigest(),
                    canvas=[frames[0].canvas_width, frames[0].canvas_height], frames=records)
    (args.output / 'reference.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
