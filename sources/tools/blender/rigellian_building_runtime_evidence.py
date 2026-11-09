"""Validate canonical building evidence without conflating it with client acceptance."""
import hashlib
import json
import struct
from pathlib import Path


def digest(path):
    raw = path.read_bytes()
    if path.suffix in {'.json', '.py'}:
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()


def verify_animation_contract(metadata, report, document):
    animation = metadata['animation']
    expected = {animation['cycle_clip'], animation['descriptor_clip']}
    assert set(report['clips']) == expected
    clips = {clip['name']: clip for clip in document['animations']}
    assert set(clips) == expected and len(document['meshes']) == report['meshes']
    for name, clip in clips.items():
        assert len(clip['channels']) == 6
        assert {document['nodes'][c['target']['node']]['name'] for c in clip['channels']} == set(animation['target_nodes'])
        assert all(c['target']['path'] == 'translation' for c in clip['channels'])
        if name == animation['descriptor_clip']:
            assert all(s['interpolation'] == 'STEP' for s in clip['samplers'])
    assert [s['descriptor'] for s in metadata['states']] == report['descriptor_domain'] == list(range(2,18))
    assert all(s['clip'] == animation['descriptor_clip'] and s['frame'] == s['descriptor'] for s in metadata['states'])
    assert all(abs(s['time_seconds'] - s['frame']/animation['fps']) < 1e-9 for s in metadata['states'])
    validation = report['animation_validation']
    assert validation['cycle_integer_frames'] == 61 and validation['descriptor_poses'] == 16
    assert validation['channels_per_clip'] == 6
    assert validation['translation_only'] is True and validation['descriptor_step'] is True
    assert validation['duplicate_state_meshes'] is False
    assert validation['continuous_sweep_proven'] is False and validation['descriptor17_composition_verified'] is False
    assert report['maximum_animation_matrix_error'] < .00003
    for key in ['native', 'imported']:
        assert report[key]['sweep']['sampled_frames'] == list(range(1,62))
        assert not report[key]['sweep']['surface_intersections']


def verify(root, record):
    root = Path(root).resolve()
    project = root.parent if root.name == 'sources' else root
    assert (project / 'project/layout.json').is_file(), 'Canonical project context required'
    reviewed = record['reviewed_model']
    proof = reviewed['runtime_evidence']
    assert proof['format'] == 'rigellian-building-remaster-v1'
    assert proof['scope'] == 'blender-native-and-imported-glb'
    assert proof['game_client_integration'] is False
    files = proof['files']

    def path(relative):
        result = (project / relative).resolve()
        assert result.is_relative_to(project) and result.is_file(), relative
        return result

    for relative, expected in files.items():
        assert digest(path(relative)) == expected, 'Changed evidence: ' + relative
    study, = record['available_studies']
    blend = 'sources/' + study['blend']
    folder = Path(blend).parent
    assert reviewed['blend'] == study['blend']
    assert files[blend] == study['sha256'] == reviewed['sha256']
    metadata_path = (folder / 'model.json').as_posix()
    report_path = (folder / 'runtime-review.json').as_posix()
    metadata = json.loads(path(metadata_path).read_bytes())
    report = json.loads(path(report_path).read_bytes())
    assert metadata['id'] == report['id'] == record['id']
    assert metadata['binaries'] == report['binaries']
    for kind, expected in metadata['binaries'].items():
        assert files[(folder / ('model.' + kind)).as_posix()] == expected
    assert hashlib.sha256(path(metadata_path).read_bytes()).hexdigest() == report['metadata_sha256']
    assert report['native']['positive_closed_meshes'] == report['imported']['positive_closed_meshes'] == report['meshes']
    assert report['maximum_bidirectional_surface_error'] < 1e-5
    assert report['final_artistic_acceptance'] is False and report['game_client_integration'] is False
    if metadata.get('recipe'):
        recipe_path = metadata['recipe']
        assert recipe_path in files
        assert hashlib.sha256(path(recipe_path).read_bytes()).hexdigest() == metadata['recipe_sha256']
        recipe = json.loads(path(recipe_path).read_bytes())
        if recipe.get('state_evidence'):
            state_evidence = recipe['state_evidence']
            assert state_evidence in files
            assert hashlib.sha256(path(state_evidence).read_bytes()).hexdigest() == recipe['state_evidence_sha256']
    if metadata.get('animation'):
        mechanism = metadata['mechanism_evidence']
        assert mechanism in files and hashlib.sha256(path(mechanism).read_bytes()).hexdigest() == metadata['mechanism_sha256']
        raw = path((folder / 'model.glb').as_posix()).read_bytes()
        document = json.loads(raw[20:20+struct.unpack_from('<I', raw, 12)[0]])
        verify_animation_contract(metadata, report, document)
    for helper, expected in report['helpers'].items():
        assert helper in files
        assert hashlib.sha256(path(helper).read_bytes()).hexdigest() == expected
    for image, expected in report['renders'].items():
        relative = proof['render_directory'] + '/' + image
        assert relative in files and files[relative] == expected
    return dict(id=record['id'], files=len(files), views=len(report['renders']),
                scope=proof['scope'], game_client_integration=False)
