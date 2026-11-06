"""Decode both PS7C descriptors with the actual embedded palette; keep pixels private."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-root', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.legacy_root/'tools'))
    import fragile256 as codec
    out = ROOT/'artifacts/issue-216/reference'
    out.mkdir(parents=True, exist_ok=True)
    _, archive, entries = codec.read_archive(args.legacy_root/'_S/_S')
    entry = next(e for e in entries if e.name == 'PS7C.256')
    payload = archive[entry.offset:entry.offset+entry.length]
    source = out/entry.name
    source.write_bytes(payload)
    raw, frames, palette, palette_source = codec.read_sprites(source)
    assert len(frames) == 2
    rows = []
    for index, frame in enumerate(frames):
        offset = codec.GLOBAL_HEADER_SIZE+frame.stream_offset
        indices = codec.decode_sprite(raw[offset:offset+frame.stream_length], frame.width, frame.height)
        image = Image.frombytes('P', (frame.width, frame.height), indices)
        image.putpalette(codec.palette_to_png(palette))
        image.info['transparency'] = 0
        image = image.convert('RGBA')
        image.save(out/f'{index:03}.png')
        image.resize((frame.width*6, frame.height*6), Image.Resampling.NEAREST).save(out/f'detail-{index}.png')
        rows.append(dict(index=index, size=list(image.size), canvas=[frame.canvas_width, frame.canvas_height],
                         offset=[frame.x, frame.y], indexed_sha256=hashlib.sha256(indices).hexdigest()))
    assert [r['size'] for r in rows] == [[113, 178], [117, 162]]
    report = dict(issue=216, source='_S/PS7C.256', source_sha256=hashlib.sha256(payload).hexdigest(),
                  palette_source=palette_source, palette_rgb_sha256=hashlib.sha256(codec.palette_to_png(palette)).hexdigest(),
                  frames=rows, semantics=['finished', 'construction (user-confirmed)'],
                  view_limit='Two states, one original viewpoint; not a recovered turntable',
                  function_evidence='Existing source-bound Space Dock function/CDB audit in space-dock-refining-evidence.json')
    (out/'reference.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PS7C_REFERENCE_DECODED', json.dumps(report))


if __name__ == '__main__':
    main()
