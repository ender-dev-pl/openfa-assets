"""Validate canonical building evidence without conflating it with client acceptance."""
import hashlib
import json
from pathlib import Path


def digest(path):
    raw = path.read_bytes()
    if path.suffix in {'.json', '.py'}:
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()


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
    for helper, expected in report['helpers'].items():
        assert helper in files
        assert hashlib.sha256(path(helper).read_bytes()).hexdigest() == expected
    for image, expected in report['renders'].items():
        relative = proof['render_directory'] + '/' + image
        assert relative in files and files[relative] == expected
    return dict(id=record['id'], files=len(files), views=len(report['renders']),
                scope=proof['scope'], game_client_integration=False)
