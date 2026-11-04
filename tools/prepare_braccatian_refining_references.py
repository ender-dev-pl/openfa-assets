"""Decode private Braccatian legacy references and bind all 38 current studies."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT/'artifacts/issue-190/references'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tile(path, size=(360, 300), original=False):
    image = Image.open(path).convert('RGBA')
    bounds = image.getchannel('A').getbbox()
    if bounds:
        image = image.crop(bounds)
    image = ImageOps.contain(image, (size[0]-20, size[1]-30), Image.Resampling.NEAREST if original else Image.Resampling.LANCZOS)
    result = Image.new('RGBA', size, (22, 27, 34, 255))
    result.alpha_composite(image, ((size[0]-image.width)//2, (size[1]-image.height)//2))
    return result.convert('RGB')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root', type=Path, required=True)
    legacy = parser.parse_args().legacy_root.resolve()
    sys.path.insert(0, str(legacy/'tools'))
    import fragile256 as codec
    import fragile_vid as video
    OUTPUT.mkdir(parents=True, exist_ok=True)
    archives, archive_hashes = {}, {}

    def sprites(directory, entry, expected=None, palette_override=None):
        if directory not in archives:
            path = legacy/directory/directory
            _, payload, entries = codec.read_archive(path)
            archives[directory] = {item.name: payload[item.offset:item.offset+item.length] for item in entries}
            archive_hashes[directory] = sha(path.read_bytes())
        payload = archives[directory][entry]
        if expected:
            assert sha(payload) == expected, entry
        folder = OUTPUT/Path(entry).stem
        folder.mkdir(exist_ok=True)
        path = folder/entry
        path.write_bytes(payload)
        data, frames, palette, _ = codec.read_sprites(path)
        colours = palette_override if palette_override is not None else codec.palette_to_png(palette)
        records = []
        for frame in frames:
            record = dict(index=frame.index, size=[frame.width, frame.height], offset=[frame.x, frame.y])
            if frame.width and frame.height:
                start = codec.GLOBAL_HEADER_SIZE+frame.stream_offset
                indices = codec.decode_sprite(data[start:start+frame.stream_length], frame.width, frame.height)
                image = Image.frombytes('P', (frame.width, frame.height), indices)
                image.putpalette(colours)
                rgba = image.convert('RGBA')
                rgba.putalpha(Image.frombytes('L', rgba.size, bytes(255 if v else 0 for v in indices)))
                target = folder/f'{frame.index:03}.png'
                rgba.save(target)
                record.update(png=target.relative_to(ROOT).as_posix(), png_sha256=sha(target.read_bytes()), indexed_sha256=sha(indices))
            records.append(record)
        return dict(source_directory=directory, source_entry=entry, source_sha256=sha(payload),
                    palette_rgb_sha256=sha(bytes(colours)), layers=records)

    rows = [r for r in json.loads((ROOT/'gallery/catalogue.json').read_text()) if r['culture'] == 'braccatian']
    assert len(rows) == 38
    ships = {r['id']: r for r in json.loads((ROOT/'sources/docs/reconstruction/models/ship-reference-index.json').read_text())['ships']}
    missiles = {r['id']: r for r in json.loads((ROOT/'sources/docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']}
    _, _, palette, _ = codec.read_sprites(legacy/'_MS/BUTTONS.256')
    colours = codec.palette_to_png(palette)
    manifest = []
    for row in rows:
        study = row['studies'][-1]
        blend = ROOT/study['blend']
        assert sha(blend.read_bytes()) == study['sha256']
        record = dict(id=row['id'], name=row['name'], category=row['category'],
                      baseline_study=study['blend'], blend_sha256=study['sha256'],
                      glb_sha256=sha((ROOT/study['glb']).read_bytes()), authored_clips=study['animations'])
        if row['category'] == 'buildings':
            key = f"BR{int(row['id'].split('/')[-1])-62:02}"
            surface = sprites('_B', key+'.256')
            source = legacy/'_ZOOM'/(key+'.VID')
            target = OUTPUT/key/'catalogue'
            if not (target/'metadata.json').is_file():
                video.export_png(source, target, legacy/'FRAGILE.EXE')
            phases = sorted((target/'frames').glob('*.png'))
            record.update(key=key, surface=surface, catalogue_source_sha256=sha(source.read_bytes()), catalogue_phases=len(phases))
            samples = [ROOT/surface['layers'][1]['png'], phases[len(phases)//2]]
        else:
            source = ships[row['id']] if row['category'] == 'ships' else missiles[row['id']]['surface']
            directory = '_S' if row['category'] == 'ships' else '_M'
            surface = sprites(directory, source['source_entry'], source['source_sha256'], colours if directory == '_M' else None)
            key = Path(source['source_entry']).stem
            record.update(key=key, surface=surface)
            filled = [r for r in surface['layers'] if 'png' in r]
            samples = [ROOT/filled[0]['png'], ROOT/filled[len(filled)//2]['png']]
        folder = OUTPUT/key
        sheet = Image.new('RGB', (1440, 335), (22, 27, 34))
        draw = ImageDraw.Draw(sheet)
        current = ROOT/study['image']
        alternate = current.with_name('rear-quarter.png')
        if not alternate.is_file():
            alternate = current.with_name('side.png')
        if not alternate.is_file():
            alternate = current
        for i, (path, label) in enumerate(zip(samples+[current, alternate], ['Original surface / state', 'Original phase / heading', 'Current authored quarter', 'Current authored alternate'])):
            sheet.paste(tile(path, original=i<2), (i*360, 30))
            draw.text((i*360+8, 8), key+' '+label, fill='white')
        sheet.save(folder/'comparison.png')
        layers = [r for r in surface['layers'] if 'png' in r]
        sheet = Image.new('RGB', (1200, ((len(layers)+5)//6)*190), (22, 27, 34))
        draw = ImageDraw.Draw(sheet)
        for i, item in enumerate(layers):
            x, y = i%6*200, i//6*190
            sheet.paste(tile(ROOT/item['png'], (200, 165), True), (x, y+20))
            draw.text((x+5, y+2), str(item['index'])+' '+str(item['size']), fill='white')
        sheet.save(folder/'all-surface-parts.png')
        manifest.append(record)
        print('BRACCATIAN_REFERENCE_READY', key, row['name'], flush=True)
    text_index = json.loads((ROOT/'sources/docs/reconstruction/models/functional-text-index.json').read_text())
    text = (legacy/'_TEXT/ENGLISH.TXT').read_bytes()
    functional, prose = [], []
    for row in text_index['records']:
        if row.get('culture') != 'braccatian':
            continue
        prose.append(row['name'])
        for item in [row['name_reference']]+row['descriptions']:
            raw = text[item['offset']:item['offset']+item['byte_length']]
            assert sha(raw) == item['sha256']
            prose.append(raw.decode('cp1252'))
        functional.append(row)
    assert len(functional) == 38
    (OUTPUT/'functions.txt').write_text('\n\n'.join(prose), encoding='utf-8')
    result = dict(issue=190, culture='braccatian', baseline='cf2843c751be17d697d65e6b9e43136f9261354a',
                  codec_sha256=sha((legacy/'tools/fragile256.py').read_bytes()),
                  video_codec_sha256=sha((legacy/'tools/fragile_vid.py').read_bytes()),
                  executable_sha256=sha((legacy/'FRAGILE.EXE').read_bytes()), archives=archive_hashes,
                  tool_sha256=sha(Path(__file__).read_bytes()), records=manifest)
    (OUTPUT/'manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    for category in ['buildings', 'ships', 'missiles']:
        selected = [r for r in manifest if r['category'] == category]
        for start in range(0, len(selected), 5):
            group = selected[start:start+5]
            sheet = Image.new('RGB', (1440, 335*len(group)))
            for j, row in enumerate(group):
                sheet.paste(Image.open(OUTPUT/row['key']/'comparison.png'), (0, j*335))
            sheet.save(OUTPUT/f'{category}-{start:02}.png')
    print('BRACCATIAN_FULL_SCOPE_REFERENCES_READY', len(manifest), flush=True)


if __name__ == '__main__':
    main()
