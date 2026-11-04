"""Register only source-bound, independently verified Rigellian crown studies."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['ri01', 'ri04', 'ri05', 'ri06', 'ri17']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    # Source inventory deliberately preserves its pre-existing line endings.
    newline = '\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data, indent=2)+'\n').replace('\n', newline).encode())


def main():
    inventory_path = ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_bytes())
    added = []
    for key in KEYS:
        rel = Path('docs/assets/reconstruction/rigellian-refined')/key
        source = ROOT/'sources'/rel
        media = ROOT/'gallery/media'/rel
        meta = json.loads((source/'model.json').read_text())
        report = json.loads((media/'validation.json').read_text())
        for kind in ['blend', 'glb']:
            assert meta[kind+'_sha256'] == report[kind+'_sha256'] == sha(source/('model.'+kind))
        generator = sha(ROOT/'sources/tools/blender/refine_rigellian_crowns.py')
        assert meta['generator_sha256'] == report['generator_sha256'] == generator
        assert report['verifier_sha256'] == sha(ROOT/'sources/tools/blender/verify_rigellian_crowns.py')
        assert report['preserved_body_position_error'] < 1e-6
        assert report['maximum_native_imported_position_error'] < 1e-4
        for view, result in report['renders'].items():
            assert result['native_sha256'] == sha(media/(view+'.png'))
            assert result['imported_sha256'] == sha(media/('imported-'+view+'.png'))
        record = next(row for row in inventory['records'] if row['id'] == meta['id'])
        path = (rel/'model.blend').as_posix()
        study = dict(stage='crown-refinement-study', blend=path, present=True,
                     sha256=meta['blend_sha256'], final_visual_acceptance='not-established')
        previous = [s for s in record['available_studies'] if s['blend'] == path]
        assert not previous or previous == [study], 'Refusing to rewrite a different existing study'
        if not previous:
            record['available_studies'].append(study)
        added += [p for p in source.iterdir() if p.is_file()]
        added += [p for p in media.iterdir() if p.is_file()]
    added += list((ROOT/'sources/materials/reconstruction/rigellian-refined/crowns').glob('*.png'))
    added += [ROOT/'sources/tools/blender'/name for name in
              ['refine_rigellian_crowns.py', 'verify_rigellian_crowns.py']]
    added += [ROOT/'sources/docs/reconstruction/models/rigellian-crown-refinement.md']
    destinations = {entry['destination'] for entry in layout['files']}
    for path in sorted(added):
        destination = path.relative_to(ROOT).as_posix()
        if destination in destinations:
            continue
        if destination.startswith('gallery/media/'):
            original, role = destination.removeprefix('gallery/media/'), 'media'
        else:
            original = destination.removeprefix('sources/')
            role = 'material-texture' if original.startswith('materials/') else 'source'
        assert not any(entry['original'] == original for entry in layout['files']), original
        layout['files'].append(dict(original=original, destination=destination,
                                    role=role, ownership='authored'))
    write_json(inventory_path, inventory)
    write_json(layout_path, layout)
    print('RIGELLIAN_CROWNS_REGISTERED', len(KEYS), 'new studies; previous studies preserved')


if __name__ == '__main__':
    main()
