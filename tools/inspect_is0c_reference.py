"""Decode the actual IS0C archive member; original pixels remain private."""
import hashlib
import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-root', required=True, type=Path)
    args = parser.parse_args()
    legacy = args.legacy_root.resolve()
    sys.path.insert(0, str(legacy / 'tools'))
    import fragile256 as codec
    out = ROOT / 'artifacts/issue-215/reference'
    out.mkdir(parents=True, exist_ok=True)
    _, archive, entries = codec.read_archive(legacy / '_S/_S')
    entry = next(e for e in entries if e.name == 'IS0C.256')
    payload = archive[entry.offset:entry.offset + entry.length]
    source = out / entry.name
    source.write_bytes(payload)
    raw, frames, palette, palette_source = codec.read_sprites(source)
    assert len(frames) == 1
    records = []
    for frame in frames:
        offset = codec.GLOBAL_HEADER_SIZE + frame.stream_offset
        indices = codec.decode_sprite(raw[offset:offset + frame.stream_length], frame.width, frame.height)
        image = Image.frombytes('P', (frame.width, frame.height), indices)
        image.putpalette(codec.palette_to_png(palette))
        image.info['transparency'] = 0
        image = image.convert('RGBA')
        image.save(out / 'decoded.png')
        image.resize((1608, 320), Image.Resampling.NEAREST).save(out / 'detail.png')
        records.append(dict(canvas=[frame.canvas_width, frame.canvas_height],
                            bounds=[frame.x, frame.y, frame.width, frame.height],
                            indexed_sha256=hashlib.sha256(indices).hexdigest()))
    report = dict(source='_S/IS0C.256', source_sha256=hashlib.sha256(payload).hexdigest(),
                  palette_source=palette_source, palette_rgb_sha256=hashlib.sha256(codec.palette_to_png(palette)).hexdigest(),
                  frames=records, original_pixels='Private artifacts only; no legacy texture imported into model')
    (out / 'reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
