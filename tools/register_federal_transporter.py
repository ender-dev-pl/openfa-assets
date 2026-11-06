"""Register the independently verified IS0C model without replacing PS05."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = 'openfa:federal-transporter'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    newline = '\r\n' if path.exists() and b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data, indent=2)+'\n').replace('\n', newline).encode())


def main():
    folder = ROOT/'sources/objects/shared/federal-transporter/refined'
    meta = json.loads((folder/'model.json').read_text())
    proof = json.loads((folder/'runtime-verification.json').read_text())
    for suffix in ['blend', 'glb']:
        assert sha(folder/('model.'+suffix)) == meta[suffix+'_sha256'] == proof[suffix+'_sha256']
    assert proof['source_unchanged'] and proof['maximum_bidirectional_world_position_error'] < 5e-6
    assert proof['generator_sha256'] == sha(ROOT/'sources/tools/blender/build_federal_transporter.py')
    assert proof['verifier_sha256'] == sha(ROOT/'sources/tools/blender/verify_federal_transporter.py')
    inventory_path = ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    assert len({r['id'] for r in inventory['records']}) == len(inventory['records'])
    record = dict(id=ID, name='Federal Transporter (IS0C)', category='ships', culture='shared',
                  workstream_issue=215,
                  legacy_identity=dict(kind='Special scheduled federal visit; not a player SHIPS type', source='_S/IS0C.256'),
                  references=[dict(directory='_S', entry='IS0C.256', kind='sprite-sheet', present=True,
                                   frame_count=1, palette_status='embedded', sha256='b41dffea9e3bd39583ba2c10939bfb7540750196d574f66d6c894c9a2ae98a23')],
                  available_studies=[dict(stage='detailed-refined', blend='objects/shared/federal-transporter/refined/model.blend',
                                          present=True, sha256=meta['blend_sha256'],
                                          final_visual_acceptance='Source renders reviewed; client integration pending')],
                  gameplay_identity='Dedicated new binding required; never alias over openfa:transporter',
                  technical_evidence='objects/shared/federal-transporter/refined/runtime-verification.json')
    old = next((r for r in inventory['records'] if r['id'] == ID), None)
    if old is not None:
        inventory['records'][inventory['records'].index(old)] = record
    else:
        inventory['records'].append(record)
    inventory['definition_count'] = len(inventory['records'])
    counts = collections.defaultdict(collections.Counter)
    for row in inventory['records']:
        counts[row['category']][row['culture']] += 1
    inventory['counts_by_category_culture'] = {k: dict(v) for k, v in counts.items()}
    write(inventory_path, inventory)
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_bytes())
    existing = {r['destination'] for r in layout['files']}
    files = list(folder.glob('*'))
    files += list((ROOT/'sources/materials/shared/federal-transporter').glob('*.png'))
    files += list((ROOT/'gallery/media/objects/shared/federal-transporter/refined').glob('*'))
    files += [ROOT/'sources/tools/blender'/name for name in ['build_federal_transporter.py', 'verify_federal_transporter.py']]
    for path in sorted(files):
        if not path.is_file():
            continue
        destination = path.relative_to(ROOT).as_posix()
        if destination in existing:
            continue
        media = destination.startswith('gallery/media/')
        original = destination.removeprefix('gallery/media/' if media else 'sources/')
        assert not any(r['original'] == original for r in layout['files']), original
        role = 'media' if media else 'material-texture' if original.startswith('materials/') else 'source'
        layout['files'].append(dict(original=original, destination=destination, role=role, ownership='authored'))
    write(layout_path, layout)
    print('FEDERAL_TRANSPORTER_REGISTERED', inventory['definition_count'])


if __name__ == '__main__':
    main()
