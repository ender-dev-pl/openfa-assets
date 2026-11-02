"""Decode private Sci-Tek motion references; no original pixels are publishable assets."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_timeline(source, folder, codec, executable):
    data = source.read_bytes()
    assert data[:4] == b'Vide' and struct.unpack_from('<I', data, 4)[0] == len(data)
    assert data[8:12] == b'Head' and struct.unpack_from('<I', data, 12)[0] == 20
    bit_depth, width, height, declared, _, _ = struct.unpack_from('<6H', data, 16)
    assert bit_depth == 8 and width and height
    decoder = codec.VideoDecoder(executable, width, height)
    frames = folder/'frames'
    frames.mkdir(parents=True)
    offset, updates, timeline = 28, 0, 0
    chunks = []
    while offset < len(data):
        tag = data[offset:offset+4]
        size = struct.unpack_from('<I', data, offset+4)[0]
        assert size >= 8 and offset+size <= len(data)
        payload = data[offset+8:offset+size]
        chunk = dict(tag=tag.decode('ascii'), offset=offset, size=size)
        if tag == b'Inte':
            decoder.apply_inter(payload)
        elif tag == b'Fram':
            palette, pixels = decoder.apply_frame(payload)
            image = Image.frombytes('P', (width, height), pixels)
            image.putpalette(bytes(((v & 63)*255+31)//63 for v in palette), rawmode='RGB')
            image.save(frames/f'{updates:03}.png')
            chunk['index'] = updates
            updates += 1
            timeline += 1
        elif tag == b'Same':
            assert updates > 0 and not payload
            timeline += 1
        chunks.append(chunk)
        offset += size
    assert timeline == declared, (source.name, timeline, declared)
    (folder/'metadata.json').write_text(json.dumps(dict(
        head=dict(width=width, height=height, image_updates=updates, timeline_frames=timeline),
        chunks=chunks, decoder='Original FRAGILE.EXE codec; Same chunks retain the prior decoded frame'), indent=2)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root', type=Path, required=True)
    parser.add_argument('--keys', nargs='*', type=int)
    args = parser.parse_args()
    legacy = args.legacy_root.resolve()
    sys.path.insert(0, str(legacy/'tools'))
    import fragile_vid as codec
    catalogue = ROOT/'sources/content/standard/presentation/legacy-domain.json'
    data = json.loads(catalogue.read_text())
    assets = {r['id']: r for r in data['assets']}
    animations = {r['id']: r for r in data['animations']}
    output = ROOT/'artifacts/issue-185/scitek-motion-review'
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for row in data['research']:
        index = int(row['id'].split('/')[-1])
        if args.keys and index not in args.keys:
            continue
        video = assets[animations[row['informationAnimationId']]['assetId']]['source']
        preview = assets[row['catalogue']['normal']['assetId']]['source']
        source = legacy/video['directoryName']/video['fileName']
        folder = output/f'ST{index:02}'
        inputs = dict(source_sha256=sha(source), executable_sha256=sha(legacy/'FRAGILE.EXE'),
                      decoder_sha256=sha(legacy/'tools/fragile_vid.py'), timeline_decoder_sha256=sha(Path(__file__)))
        if (folder/'inputs.json').exists():
            assert json.loads((folder/'inputs.json').read_text()) == inputs, 'Keep prior decoding; input changed'
        else:
            assert not folder.exists(), 'Unrecognized reference output; preserve it separately'
            decode_timeline(source, folder, codec, legacy/'FRAGILE.EXE')
            (folder/'inputs.json').write_text(json.dumps(inputs, indent=2)+'\n')
        meta = json.loads((folder/'metadata.json').read_text())
        timeline, last = [], None
        for chunk in meta['chunks']:
            if chunk['tag'] == 'Fram':
                last = chunk['index']
            if chunk['tag'] in ['Fram', 'Same']:
                assert last is not None
                timeline.append(last)
        frames = sorted((folder/'frames').glob('*.png'))
        selected = sorted({round(i*(len(frames)-1)/17) for i in range(18)})
        sheet = Image.new('RGB', (900, 6*190), (16, 20, 24))
        draw = ImageDraw.Draw(sheet)
        for i, n in enumerate(selected):
            image = Image.open(folder/f'frames/{n:03}.png').convert('RGB')
            image = ImageOps.contain(image, (292, 162), Image.Resampling.NEAREST)
            sheet.paste(image, (i%3*300, i//3*190+24))
            draw.text((i%3*300+5, i//3*190+4), f'ST{index:02} update {n}', fill='white')
        sheet.save(folder/'motion-contact.png')
        record = dict(index=index, subject=row['researchId'], preview_source=preview,
                      information_source=video, **inputs, image_updates=len(frames),
                      timeline_frames=len(timeline), same_frames=len(timeline)-len(frames),
                      sampled_updates=selected, direct_rigellian_preview=preview.get('entryName', '').startswith('RI'),
                      motion_contact_sha256=sha(folder/'motion-contact.png'))
        records.append(record)
        (folder/'review-inputs.json').write_text(json.dumps(record, indent=2)+'\n')
        print('SCITEK_MOTION_REFERENCE_READY', index, row['researchId'], len(frames), len(timeline), flush=True)
    (output/('manifest-'+('-'.join(map(str, args.keys)) if args.keys else 'all')+'.json')).write_text(
        json.dumps(dict(catalogue_sha256=sha(catalogue), records=records), indent=2)+'\n')


if __name__ == '__main__':
    main()
