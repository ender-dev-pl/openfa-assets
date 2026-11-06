"""Register verified orbital-station state pairs without replacing finished studies."""
import hashlib
import json
from pathlib import Path

from gallery_animation_assets import animation_previews

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    newline = '\r\n' if path.exists() and b'\r\n' in path.read_bytes() else '\n'
    path.write_bytes((json.dumps(data, indent=2)+'\n').replace('\n', newline).encode())


def main():
    inventory_path = ROOT/'sources/docs/reconstruction/models/inventory.json'
    inventory = json.loads(inventory_path.read_text())
    pair_path = ROOT/'sources/docs/reconstruction/models/orbital-station-variants.json'
    pairs = json.loads(pair_path.read_text())
    registered = []
    for pair in pairs['records']:
        if pair['status'] != 'runtime-verified':
            continue
        row = next(r for r in inventory['records'] if r['id'] == pair['id'])
        for variant in ['finished', 'construction']:
            state = pair[variant]
            source = ROOT/state['blend']
            meta = json.loads(source.with_suffix('.json').read_text())
            report_path = ROOT/state['validation']
            report = json.loads(report_path.read_text())
            assert meta['id'] == pair['id']
            assert report.get('id', meta['id']) == pair['id']
            for kind in ['blend', 'glb']:
                assert state[kind+'_sha256'] == meta[kind+'_sha256'] == report[kind+'_sha256'] == sha(source.with_suffix('.'+kind))
            assert report['maximum_native_imported_position_error'] < .0001
            if variant == 'finished':
                previous = [s for s in row['available_studies'] if s['blend'] == state['blend'].removeprefix('sources/')]
                if not previous:
                    assert report['retained_geometry_uv_normals_preserved'] and report['finished_helpers_preserved']
                    assert report['verifier_sha256'] == sha(ROOT/pair['verifier'])
                    assert report['generator_sha256'] == meta['generator_sha256'] == sha(ROOT/pair['generator'])
                    for name, digest in report['verifier_dependencies_sha256'].items():
                        assert sha(ROOT/'sources/tools/blender'/name) == digest
                    for name, digest in meta['dependency_sha256'].items():
                        assert sha(ROOT/'sources/tools/blender'/name) == digest
                    for name, digest in meta['texture_sha256'].items():
                        assert sha(ROOT/name) == digest
                    for side in ['native', 'imported']:
                        assert report[side+'_structure']['positive_closed_meshes'] == report[side+'_mesh_count']
                    for view, result in report['renders'].items():
                        assert result['native_sha256'] == sha(report_path.parent/(view+'.png'))
                        assert result['imported_sha256'] == sha(report_path.parent/('imported-'+view+'.png'))
                    assert not animation_previews(state['blend'], state['glb'], report_path.parent)
                    row['available_studies'].append(dict(stage=meta['stage'], blend=state['blend'].removeprefix('sources/'), present=True,
                                                        sha256=meta['blend_sha256'], final_visual_acceptance='not-established'))
                else:
                    assert len(previous)==1 and previous[0]['sha256']==state['blend_sha256']
                continue
            assert report['finished_body_geometry_uv_normals_preserved'] and report['finished_helpers_preserved']
            for side in ['native', 'imported']:
                assert report[side+'_structure']['positive_closed_meshes'] == report[side+'_mesh_count']
            for name, digest in report['verifier_dependencies_sha256'].items():
                assert sha(ROOT/'sources/tools/blender'/name) == digest
            verifier = ROOT/pair['verifier']
            assert report['verifier_sha256'] == sha(verifier)
            assert report['generator_sha256'] == meta['generator_sha256'] == sha(ROOT/pair['generator'])
            for name, digest in meta['texture_sha256'].items():
                assert sha(ROOT/name) == digest
            for name, digest in meta['dependency_sha256'].items():
                assert sha(verifier.with_name(name)) == digest
            media = report_path.parent
            for view, result in report['renders'].items():
                assert result['native_sha256'] == sha(media/(view+'.png'))
                assert result['imported_sha256'] == sha(media/('imported-'+view+'.png'))
            clips = animation_previews(state['blend'], state['glb'], media)
            assert len(clips) == 1 and clips[0]['name'] == 'ConstructionActivity'
            assert clips[0]['duration'] == 6 and clips[0]['frames'] == 144
            study = dict(stage=meta['stage'], blend=state['blend'].removeprefix('sources/'), present=True,
                         sha256=meta['blend_sha256'], final_visual_acceptance='not-established')
            previous = [s for s in row['available_studies'] if s['blend'] == study['blend']]
            assert not previous or previous == [study], 'Preserve accepted studies'
            if not previous:
                row['available_studies'].append(study)
            registered.append(pair['key'])
    layout_path = ROOT/'project/layout.json'
    layout = json.loads(layout_path.read_text())
    destinations = {r['destination'] for r in layout['files']}
    paths = [pair_path, ROOT/'sources/docs/reconstruction/models/orbital-station-construction.md']
    for pair in pairs['records']:
        if pair['status'] != 'runtime-verified':
            continue
        paths += [ROOT/pair['generator'], ROOT/pair['verifier']]
        if pair.get('evidence'):
            paths.append(ROOT/pair['evidence'])
        for variant in ['finished','construction']:
            paths += list((ROOT/pair[variant]['blend']).parent.iterdir())
            paths += list((ROOT/pair[variant]['validation']).parent.rglob('*'))
            meta = json.loads((ROOT/pair[variant]['blend']).with_suffix('.json').read_text())
            paths += [ROOT/p for p in meta.get('texture_sha256',{})]
    for path in sorted(set(paths)):
        if not path.is_file():
            continue
        assert path.suffix != '.blend1'
        destination = path.relative_to(ROOT).as_posix()
        if destination in destinations:
            continue
        media = destination.startswith('gallery/media/')
        original = destination.removeprefix('gallery/media/' if media else 'sources/')
        assert not any(r['original'] == original for r in layout['files'])
        role = 'media' if media else 'material-texture' if original.startswith('materials/') else 'source'
        layout['files'].append(dict(original=original, destination=destination, role=role, ownership='authored'))
        destinations.add(destination)
    save(inventory_path, inventory)
    save(layout_path, layout)
    print('ORBITAL_STATION_PAIRS_REGISTERED', ','.join(registered))


if __name__ == '__main__':
    main()
