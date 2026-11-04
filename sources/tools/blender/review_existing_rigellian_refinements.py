"""Run unchanged source-specific assertions on isolated copies for the refining review."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
KEYS = [2, 7, 9, 10, 11, 12, 13, 15, 16, 19, 21, 22]
EARLY = {2: 'filtration', 7: 'science', 9: 'construction', 10: 'ground_deck'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key', type=int, choices=KEYS, required=True)
    key = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).key
    inventory = json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text())
    record = next(r for r in inventory['records'] if r['id'] == f'openfa:building/legacy/{39+key:03}')
    study = [s for s in record['available_studies'] if s['present']][-1]
    source = ROOT/'sources'/study['blend']
    assert sha(source) == study['sha256']
    original_report = json.loads(source.with_name('technical-review.json').read_text())
    if key in EARLY:
        name = 'verify_rigellian_'+EARLY[key]
    else:
        matches = [p.stem for p in SCRIPTS.glob('verify_*.py') if sha(p) == original_report['verifier_sha256']]
        assert len(matches) == 1, 'Source-specific verifier identity is not uniquely available'
        name = matches[0]
    module = importlib.import_module(name)
    assert module.ROOT.resolve() == source.parent.resolve(), 'Verifier targets a different study'
    output = ROOT/'artifacts/issue-185/retention-runtime'/f'ri{key:02}'
    target = output/'working'
    assert not target.exists(), 'Keep prior runtime evidence; use an explicitly new output directory'
    target.mkdir(parents=True)
    layout = json.loads((ROOT/'project/layout.json').read_text())
    prefix = source.parent.relative_to(ROOT/'sources').as_posix()+'/'
    inputs = {}
    for entry in layout['files']:
        if not entry['original'].startswith(prefix) or entry['role'] == 'media':
            continue
        canonical = ROOT/entry['destination']
        relative = entry['original'][len(prefix):]
        destination = target/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(canonical, destination)
        inputs[entry['destination']] = sha(canonical)
    assert (target/'model.blend').is_file() and (target/'model.glb').is_file()
    # A pass must produce a fresh report and fresh images, not retain the old ones.
    prior_report = target/'technical-review.json'
    if prior_report.exists():
        prior_report.unlink()
    redirected = []
    for loaded in list(sys.modules.values()):
        if loaded is None:
            continue
        value = getattr(loaded, 'ROOT', None)
        if isinstance(value, Path) and value.resolve() == source.parent.resolve():
            redirected.append((loaded, value))
            loaded.ROOT = target
    try:
        module.main()
    finally:
        for loaded, value in redirected:
            loaded.ROOT = value
        assert all(sha(ROOT/path) == value for path, value in inputs.items()), 'Canonical input changed'
    assert prior_report.is_file(), 'Source-specific verifier did not publish a fresh runtime report'
    imported = target/'imported-glb-front-quarter.png'
    assert imported.is_file(), 'Actual independent GLB overview missing'
    bpy.ops.wm.open_mainfile(filepath=str(target/'model.blend'))
    scene = bpy.context.scene
    assert scene.camera is not None
    scene.frame_set(1)
    native = target/'native-current-front-quarter.png'
    scene.render.filepath = str(native)
    bpy.ops.render.render(write_still=True)
    report = dict(issue=185, key=f'RI{key:02}', id=record['id'], name=record['name'],
                  study=source.relative_to(ROOT).as_posix(), blend_sha256=sha(source),
                  glb_sha256=sha(source.with_suffix('.glb')), verifier=name+'.py',
                  verifier_sha256=sha(SCRIPTS/(name+'.py')), runner_sha256=sha(Path(__file__)),
                  original_assertions_unchanged=True, canonical_inputs_unchanged=True,
                  canonical_inputs=inputs, actual_runtime_report_sha256=sha(prior_report),
                  native_overview_sha256=sha(native), imported_overview_sha256=sha(imported),
                  working_copy=target.relative_to(ROOT).as_posix(), blender=bpy.app.version_string,
                  passed=True, visual_decision='Pending focused source/render review; technical pass alone is insufficient')
    (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RIGELLIAN_REFINING_RETAINED_RUNTIME_OK', key, record['name'], flush=True)


if __name__ == '__main__':
    main()
