"""Decode private legacy evidence and pair it with existing Rigellian studies.

Outputs contain original pixels and must remain in ignored artifacts/. This is
an evidence preparation tool, not a model generator or visual acceptance gate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT.parent / 'legacy'
OUT = ROOT / 'artifacts/issue-185/references'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tile(path, size=(380, 320), nearest=False):
    with Image.open(path) as source:
        image = source.convert('RGBA')
    bounds = image.getchannel('A').getbbox()
    if bounds:
        image = image.crop(bounds)
    image = ImageOps.contain(image, (size[0]-24, size[1]-24),
                            Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS)
    result = Image.new('RGBA', size, (22, 27, 34, 255))
    result.alpha_composite(image, ((size[0]-image.width)//2, (size[1]-image.height)//2))
    return result.convert('RGB')


def main():
    global LEGACY
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root', type=Path, default=LEGACY)
    LEGACY = parser.parse_args().legacy_root.resolve()
    sys.path.insert(0, str(LEGACY/'tools'))
    import fragile256 as codec
    import fragile_vid as video
    OUT.mkdir(parents=True, exist_ok=True)
    archive_cache = {}

    def sprites(directory, entry, expected_sha, external_palette=None):
        if directory not in archive_cache:
            _, payload, entries = codec.read_archive(LEGACY/directory/directory)
            archive_cache[directory] = {
                item.name: payload[item.offset:item.offset+item.length] for item in entries}
        payload = archive_cache[directory][entry]
        assert sha(payload) == expected_sha, entry
        folder = OUT/Path(entry).stem
        folder.mkdir(exist_ok=True)
        source = folder/entry
        source.write_bytes(payload)
        data, frames, palette, _ = codec.read_sprites(source)
        colours = external_palette if external_palette is not None else codec.palette_to_png(palette)
        paths = []
        for frame in frames:
            if not frame.width or not frame.height:
                paths.append(None)
                continue
            start = codec.GLOBAL_HEADER_SIZE+frame.stream_offset
            indices = codec.decode_sprite(data[start:start+frame.stream_length], frame.width, frame.height)
            image = Image.frombytes('P', (frame.width, frame.height), indices)
            image.putpalette(colours)
            rgba = image.convert('RGBA')
            rgba.putalpha(Image.frombytes('L', rgba.size, bytes(255 if value else 0 for value in indices)))
            path = folder/f'{frame.index:03}.png'
            rgba.save(path)
            paths.append(path)
        return paths

    records = json.loads((ROOT/'gallery/catalogue.json').read_text())
    rows = {row['id']: row for row in records if row['culture'] == 'rigellian'}
    refs = json.loads((ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json').read_text())
    manifest = []
    for item in refs['buildings']:
        key = item['key']
        paths = sprites('_B', key+'.256', item['surface']['source_sha256'])
        vid = LEGACY/'_ZOOM'/(key+'.VID')
        target = OUT/key/'hologram'
        if not (target/'metadata.json').is_file():
            video.export_png(vid, target, LEGACY/'FRAGILE.EXE')
        frames = sorted((target/'frames').glob('*.png'))
        assert len(frames) == 41, key
        row = rows[item['id']]
        study = row['studies'][-1]
        image = ROOT/study['image']
        sheet = Image.new('RGB', (1520, 360), (22, 27, 34))
        draw = ImageDraw.Draw(sheet)
        sources = [(paths[1] or paths[2], 'Surface body; separate layers may apply', True),
                   (frames[20], 'Catalogue phase 20; fixed presentation', True),
                   (image, 'Latest authored front quarter', False),
                   (image.with_name('side.png'), 'Latest authored side', False)]
        for n, (path, label, nearest) in enumerate(sources):
            if not path.is_file():
                path = image
            sheet.paste(tile(path, nearest=nearest), (n*380, 40))
            draw.text((n*380+8, 8), key+' '+label, fill='white')
        sheet.save(OUT/key/'comparison.png')
        manifest.append(dict(id=item['id'], key=key, blend=study['blend'],
                             blend_sha256=sha((ROOT/study['blend']).read_bytes()),
                             surface_sha256=item['surface']['source_sha256'],
                             video_sha256=sha(vid.read_bytes()), video_frames=len(frames)))
    ship_index = json.loads((ROOT/'sources/docs/reconstruction/models/ship-reference-index.json').read_text())
    missile_index = json.loads((ROOT/'sources/docs/reconstruction/models/missile-reference-index.json').read_text())
    _, _, palette, _ = codec.read_sprites(LEGACY/'_MS/BUTTONS.256')
    for category, items in [('ships', ship_index['ships']), ('missiles', missile_index['missiles'])]:
        for item in items:
            if item['culture'] != 'rigellian':
                continue
            source = item if category == 'ships' else item['surface']
            entry = source['source_entry']
            paths = sprites('_S' if category == 'ships' else '_M', entry, source['source_sha256'],
                            codec.palette_to_png(palette) if category == 'missiles' else None)
            selected = [0, 8, 16, 24] if len(paths) == 32 else list(range(min(7, len(paths))))
            sheet = Image.new('RGB', (1520, 720), (22, 27, 34))
            draw = ImageDraw.Draw(sheet)
            for n, index in enumerate(selected):
                if paths[index]:
                    sheet.paste(tile(paths[index], (380, 270), True), (n%4*380, n//4*320+40))
                    draw.text((n%4*380+8, n//4*320+8), entry+f' frame {index}', fill='white')
            study = rows[item['id']]['studies'][-1]
            sheet.paste(tile(ROOT/study['image'], (380, 320)), (1140, 360))
            sheet.save(OUT/Path(entry).stem/'comparison.png')
            manifest.append(dict(id=item['id'], key=Path(entry).stem, blend=study['blend'],
                                 blend_sha256=sha((ROOT/study['blend']).read_bytes()),
                                 surface_sha256=source['source_sha256'], frames=len(paths)))
    assert len(manifest) == len(rows) == 35
    text_index = json.loads((ROOT/'sources/docs/reconstruction/models/functional-text-index.json').read_text())
    payload = (LEGACY/'_TEXT/ENGLISH.TXT').read_bytes()
    narrative = []
    for item in text_index['records']:
        if item.get('culture') != 'rigellian':
            continue
        narrative += [item['id']+' '+item['name']]
        for desc in item['descriptions']:
            raw = payload[desc['offset']:desc['offset']+desc['byte_length']]
            assert sha(raw) == desc['sha256']
            narrative.append(raw.decode('cp1252'))
    (OUT/'functions.txt').write_text('\n\n'.join(narrative), encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    for start in range(0, 23, 6):
        subset = manifest[:23][start:start+6]
        sheet = Image.new('RGB', (1520, 360*len(subset)))
        for n, item in enumerate(subset):
            with Image.open(OUT/item['key']/'comparison.png') as image:
                sheet.paste(image, (0, 360*n))
        sheet.save(OUT/f'buildings-{start+1:02}.png')
    print('RIGELLIAN_PRIVATE_REFERENCES_READY', len(manifest), 'definitions; 943 catalogue frames', flush=True)


if __name__ == '__main__':
    main()
