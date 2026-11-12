"""Register verified PS7C stages while preserving all earlier studies."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    newline = '\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data, indent=2)+'\n').replace('\n', newline).encode())


def main():
    path = ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(path.read_bytes())
    record = next(r for r in inventory['records'] if r['id'] == 'openfa:space-dock')
    files = []
    for variant in ['refined', 'construction']:
        folder = ROOT/'sources/objects/terran/space-dock'/variant
        media = ROOT/'gallery/media/objects/terran/space-dock'/variant
        meta = json.loads((folder/'model.json').read_text())
        proof = json.loads((folder/'runtime-verification.json').read_text())
        for suffix in ['blend', 'glb']:
            assert sha(folder/('model.'+suffix)) == meta[suffix+'_sha256'] == proof[suffix+'_sha256']
        assert proof['source_unchanged'] and proof['maximum_world_position_error'] < 5e-6
        assert meta['generator_sha256'] == sha(ROOT/'sources/tools/blender/refine_ps7c_details.py')
        assert meta['material_generator_sha256'] == sha(ROOT/'sources/tools/blender/ps7c_materials.py')
        assert proof['verifier_sha256'] == sha(ROOT/'sources/tools/blender/verify_ps7c_details.py')
        blend = (folder/'model.blend').relative_to(ROOT/'sources').as_posix()
        study = dict(stage=meta['stage'], blend=blend, present=True, sha256=meta['blend_sha256'],
                     final_visual_acceptance='Reviewed detailed source; client scale/GPU and mount calibration pending')
        old = next((s for s in record['available_studies'] if s['blend'] == blend), None)
        if old is None:
            record['available_studies'].append(study)
        else:
            record['available_studies'][record['available_studies'].index(old)] = study
        files += [p for p in folder.iterdir() if p.is_file()]
        files += [p for p in media.iterdir() if p.is_file()]
    record['current_shared_model'] = 'objects/terran/space-dock/refined/model.glb'
    record['current_construction_model'] = 'objects/terran/space-dock/construction/model.glb'
    write(path, inventory)
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_bytes())
    files += list((ROOT/'sources/materials/terran/space-dock/refined').glob('*.png'))
    files += [ROOT/'sources/tools/blender'/name for name in ['refine_ps7c_details.py', 'ps7c_materials.py',
                                                          'verify_ps7c_details.py', 'render_ps7c_activity.py']]
    existing = {r['destination'] for r in layout['files']}
    for path in sorted(files):
        destination = path.relative_to(ROOT).as_posix()
        if destination in existing:
            continue
        media = destination.startswith('gallery/media/')
        original = destination.removeprefix('gallery/media/' if media else 'sources/')
        assert not any(r['original'] == original for r in layout['files']), original
        role = 'media' if media else 'material-texture' if original.startswith('materials/') else 'source'
        layout['files'].append(dict(original=original, destination=destination, role=role, ownership='authored'))
    write(layout_path, layout)
    print('PS7C_DETAILS_REGISTERED', len(record['available_studies']), 'preserved and current studies')


if __name__ == '__main__':
    main()
