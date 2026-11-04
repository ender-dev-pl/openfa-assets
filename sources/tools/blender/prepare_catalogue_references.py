"""Decode reference-only previews outside tracked model outputs; preserve mappings and hashes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('artifacts/issue-943-catalogue/references'))
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    data = json.loads((repo / 'content/standard/catalogues/legacy-buildings.json').read_text(encoding='utf-8'))
    presentation = json.loads((repo / 'content/standard/presentation/legacy-domain.json').read_text(encoding='utf-8'))
    profiles = {item['buildingId']: item for item in presentation['buildings']}
    assets = {item['id']: item for item in presentation['assets']}
    animations = {item['id']: item for item in presentation['animations']}
    spec = importlib.util.spec_from_file_location('legacy_vid_decoder', args.legacy_root / 'tools/fragile_vid.py')
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    records = []
    for building in data['buildings']:
        profile = profiles[building['id']]
        animation = animations[profile['catalogue']['previewAnimationId']]
        source = assets[animation['assetId']]['source']
        video = args.legacy_root / source['directoryName'] / source['fileName']
        key = source['fileName'].removesuffix('.VID')
        output = args.output / key
        if not (output / 'metadata.json').is_file():
            decoder.export_png(video, output, args.legacy_root / 'FRAGILE.EXE')
        metadata = json.loads((output / 'metadata.json').read_text())
        count = metadata['head']['frame_count']
        selected = sorted(set([0, count // 4, count // 2, count * 3 // 4, count - 1]))
        surface_root = args.legacy_root / '_B/png'
        surface_manifest = json.loads((surface_root / (key + '.json')).read_text())
        body = surface_manifest['frames'][1]
        layered = building['legacy']['definitionClass'] in [3, 17, 18, 27, 40] and len(surface_manifest['frames']) >= 18
        body_frames = [1, 2] if layered else [1]
        records.append({'global_type': building['legacy']['globalType'], 'building_id': building['id'],
            'name': building['legacy']['name'], 'culture': building['factionId'].split('/')[-1],
            'definition_class': building['legacy']['definitionClass'],
            'footprint': [building['footprintWidth'], building['footprintHeight']],
            'preview': key, 'source_directory': source['directoryName'],
            'source_sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
            'frame_count': count, 'selected_frames_zero_based': selected,
            'surface_entry': key + '.256', 'surface_body_frame': 1,
            'surface_composition_frames': body_frames,
            'surface_layer_sha256': {str(index): hashlib.sha256((surface_root / surface_manifest['frames'][index]['png']).read_bytes()).hexdigest()
                                     for index in body_frames},
            'surface_body_sha256': hashlib.sha256((surface_root / body['png']).read_bytes()).hexdigest(),
            'reference_mode': 'preview rotation' if building['factionId'].endswith('/terran') else 'surface body plus hologram final frame',
            'selected_frame_sha256': {str(index): hashlib.sha256((output / 'frames' / f'{index:03}.png').read_bytes()).hexdigest()
                                      for index in selected}})
        print('REFERENCE_READY', building['legacy']['globalType'], key, flush=True)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'index.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    for culture in sorted({record['culture'] for record in records}):
        group = [record for record in records if record['culture'] == culture]
        for start in range(0, len(group), 20):
            subset = group[start:start + 20]
            sheet = Image.new('RGB', (1600, 1280), (15, 20, 27))
            draw = ImageDraw.Draw(sheet)
            for slot, item in enumerate(subset):
                if culture == 'terran':
                    image = Image.open(args.output / item['preview'] / 'frames/000.png').convert('RGB')
                else:
                    source = args.legacy_root / '_B/png'
                    frames = json.loads((source / (item['preview'] + '.json')).read_text())['frames']
                    image = Image.new('RGB', (320, 200), (255, 0, 255))
                    for frame_index in item['surface_composition_frames']:
                        layer = Image.open(source / frames[frame_index]['png']).convert('RGB')
                        mask = ImageChops.difference(layer, Image.new('RGB', layer.size, layer.getpixel((0, 0)))).convert('L').point(lambda value: 255 if value else 0)
                        image.paste(layer, (0, 0), mask)
                bounds = ImageChops.difference(image, Image.new('RGB', image.size, image.getpixel((0, 0)))).getbbox()
                image = image.crop(bounds)
                factor = min(280 / image.width, 245 / image.height)
                image = image.resize((round(image.width * factor), round(image.height * factor)), Image.Resampling.NEAREST)
                x, y = slot % 5 * 320, slot // 5 * 320
                sheet.paste(image, (x + (320 - image.width) // 2, y + (260 - image.height) // 2))
                draw.text((x + 8, y + 271), f'{item["global_type"]:03} {item["preview"]} {item["name"]}', fill='white')
            sheet.save(args.output / f'{culture}-{start:02}.png')


if __name__ == '__main__':
    main()
