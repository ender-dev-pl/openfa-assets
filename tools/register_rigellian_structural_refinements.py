"""Register source-bound visible structural refinements without replacing prior studies."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = {
    'ri20': ('refine_rigellian_extractor.py', 'verify_refined_rigellian_extractor.py'),
    'ri03': ('refine_rigellian_nourishment.py', 'verify_refined_rigellian_nourishment.py'),
    'observatory': ('refine_rigellian_observatory.py', 'verify_refined_rigellian_observatory.py'),
    'transportation': ('refine_rigellian_transport.py', 'verify_refined_rigellian_transport.py'),
    'lazzaro-research': ('refine_lazzaro_visible_forms.py', 'verify_refined_lazzaro_forms.py'),
}
MISSILES = ['detonator', 'multi-det', 'flamejell', 'maxi-det', 'flare', 'viral-repair', 'temporal-stasis']
SCRIPTS.update({key: ('refine_rigellian_missiles.py', 'verify_refined_rigellian_missiles.py') for key in MISSILES})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    newline = '\r\n' if b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data, indent=2)+'\n').replace('\n', newline).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=SCRIPTS, required=True)
    args = parser.parse_args()
    rel = Path('docs/assets/reconstruction/rigellian-refined')
    if args.model in MISSILES:
        rel /= 'missiles'
    rel /= args.model
    source, media = ROOT/'sources'/rel, ROOT/'gallery/media'/rel
    meta = json.loads((source/'model.json').read_text())
    report = json.loads((media/'validation.json').read_text())
    generator, verifier = SCRIPTS[args.model]
    assert meta['generator_sha256'] == report['generator_sha256'] == sha(ROOT/'sources/tools/blender'/generator)
    assert report['verifier_sha256'] == sha(ROOT/'sources/tools/blender'/verifier)
    assert meta['source_blend_sha256'] == report['source_blend_sha256'] == sha(ROOT/meta['source_study'])
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == report[kind+'_sha256'] == sha(source/('model.'+kind))
    assert report['maximum_native_imported_position_error'] < .0001
    assert report['native_structure']['positive_closed_meshes'] == report['native_mesh_count']
    assert report['imported_structure']['positive_closed_meshes'] == report['imported_mesh_count']
    for view, result in report['renders'].items():
        assert result['native_sha256'] == sha(media/(view+'.png'))
        assert result['imported_sha256'] == sha(media/('imported-'+view+'.png'))
    inventory_path = ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(inventory_path.read_bytes())
    record = next(row for row in inventory['records'] if row['id'] == meta['id'])
    study = dict(stage=meta['stage'], blend=(rel/'model.blend').as_posix(), present=True,
                 sha256=meta['blend_sha256'], final_visual_acceptance='not-established')
    prior = [s for s in record['available_studies'] if s['blend'] == study['blend']]
    if prior and prior != [study]:
        tracked = subprocess.run(['git', 'cat-file', '-e', 'HEAD:sources/'+study['blend']],
                                 cwd=ROOT, capture_output=True, check=False).returncode == 0
        assert not tracked, 'Preserve committed studies; use a new study path for further changes'
        record['available_studies'].remove(prior[0])
        prior = []
    if not prior:
        record['available_studies'].append(study)
    paths = list(source.iterdir())+list(media.iterdir())
    paths += list((ROOT/'sources/materials/reconstruction/rigellian-refined'/args.model).glob('*.png'))
    paths += [ROOT/'sources/tools/blender'/name for name in [generator, verifier]]
    paths += [ROOT/'sources/docs/reconstruction/models'/name for name in
              ['rigellian-lore-evidence.json', 'rigellian-structural-refinement.md']]
    if args.model in MISSILES:
        paths.append(ROOT/'sources/docs/reconstruction/models/rigellian-missile-refinement.md')
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_bytes())
    destinations = {entry['destination'] for entry in layout['files']}
    for path in sorted(paths):
        assert path.is_file(), path
        destination = path.relative_to(ROOT).as_posix()
        if destination in destinations:
            continue
        if destination.startswith('gallery/media/'):
            original, role = destination.removeprefix('gallery/media/'), 'media'
        else:
            original = destination.removeprefix('sources/')
            role = 'material-texture' if original.startswith('materials/') else 'source'
        assert not any(entry['original'] == original for entry in layout['files']), original
        layout['files'].append(dict(original=original, destination=destination, role=role, ownership='authored'))
    save(inventory_path, inventory)
    save(layout_path, layout)
    print('STRUCTURAL_REFINEMENT_REGISTERED', args.model)


if __name__ == '__main__':
    main()
