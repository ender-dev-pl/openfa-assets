"""Exercise the existing RI18 cycle on an isolated exact copy; do not regenerate it."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import verify_launch_facilities as verifier


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    relative = Path('sources/docs/assets/reconstruction/launch-facilities/rigellian/ri18')
    source = ROOT/relative
    meta = json.loads((source/'model.json').read_text())
    for ext in ['blend', 'glb']:
        assert sha(source/('model.'+ext)) == meta[ext+'_sha256']
    # This is a retained model, not a regeneration. Other facilities were added
    # after RI18 was authored, so its recorded generator/recipe may be earlier
    # than the current files. Preserve and disclose both identities; do not
    # rewrite the model's provenance or claim the current generator produced it.
    generation = dict(recorded_generator_sha256=meta['generator_sha256'],
                      current_generator_sha256=sha(SCRIPTS/'build_launch_facilities.py'),
                      recorded_recipe_sha256=meta['recipe_sha256'],
                      current_recipe_sha256=sha(SCRIPTS/'launch_facility_recipes.py'),
                      generator_executed=False)
    assert sha(ROOT/meta['source_study']) == meta['source_blend_sha256']
    inventory = json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text())
    record = next(r for r in inventory['records'] if r['id'] == meta['id'])
    current = [s for s in record['available_studies'] if s['present']][-1]
    assert current['blend'] == (relative/'model.blend').as_posix().removeprefix('sources/')
    assert current['sha256'] == meta['blend_sha256']
    output = ROOT/'artifacts/issue-185/retention-runtime/ri18'
    work = output/'working'
    assert not work.exists(), 'Preserve prior runtime evidence; select a new output directory'
    target = work/relative
    shutil.copytree(source, target)
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in source.iterdir() if p.is_file()}
    media = work/'gallery/media/docs/assets/reconstruction/launch-facilities/rigellian/ri18'
    media.mkdir(parents=True)
    audit = json.loads((ROOT/'sources/docs/reconstruction/models/launch-facility-animation-audit.json').read_text())
    recipe = next(r for r in audit['records'] if r['key'] == 'RI18')
    verifier.ROOT = work
    verifier.verify(recipe)
    for frame, label in [(1, 'closed'), (16, 'half-open')]:
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = str(media/('imported-'+label+'.png'))
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.open_mainfile(filepath=str(target/'model.blend'))
    for frame, label in [(1, 'closed'), (16, 'half-open'), (31, 'open')]:
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = str(media/('native-'+label+'.png'))
        bpy.ops.render.render(write_still=True)
    assert all(sha(ROOT/path) == value for path, value in inputs.items())
    report = dict(issue=185, key='RI18', id=meta['id'], name='Missile Launcher',
                  study=(relative/'model.blend').as_posix(), blend_sha256=meta['blend_sha256'],
                  glb_sha256=meta['glb_sha256'], runner_sha256=sha(Path(__file__)),
                  verifier='verify_launch_facilities.py', verifier_sha256=sha(SCRIPTS/'verify_launch_facilities.py'),
                  original_assertions_unchanged=True, canonical_inputs_unchanged=True,
                  retained_generation_provenance=generation,
                  canonical_inputs=inputs, actual_runtime_report_sha256=sha(media/'validation.json'),
                  working_copy=work.relative_to(ROOT).as_posix(), blender=bpy.app.version_string,
                  state_renders={p.name: sha(p) for p in media.glob('*.png')},
                  passed=True, visual_decision='Pending focused source/render review; technical pass alone is insufficient')
    (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RIGELLIAN_REFINING_RETAINED_LAUNCHER_OK', flush=True)


if __name__ == '__main__':
    main()
