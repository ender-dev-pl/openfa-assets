"""Apply issue #1108 connectivity repair without regenerating any ship geometry."""
import json
import shutil
import sys
import uuid
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fighter_plate_topology import repair_plate
from probe_fighter_armour_tessellation import measure, sha, SOURCE, OUTPUT
from audit_detail_uv_proposal import geometry
from build_refined_terran import export_glb_to, render_to, save_blend_to
from catalogue_rendering import evaluated_points, fit_camera
from verify_assault_fighter import bounds

REPO = Path(__file__).resolve().parents[2]
VIEWS = [('front-quarter', (8, -12, 10)), ('rear-quarter', (-8, 12, 10)), ('top', (0, 0, 20)),
         ('side', (14, 0, 4)), ('rear', (0, 14, 4)), ('belly', (7, -10, -12))]


def main():
    proposal = json.loads((OUTPUT/'proposal.json').read_text())
    meta = json.loads((SOURCE/'model.json').read_text())
    assert meta['revision'] == 3
    assert proposal['helper_sha256'] == sha(Path(__file__).with_name('fighter_plate_topology.py'))
    for ext in ['blend', 'glb']:
        assert proposal['source_hashes'][ext] == meta[ext+'_sha256'] == sha(SOURCE/('model.'+ext))
    original_files = {str(p.relative_to(SOURCE)).replace('\\', '/'): sha(p) for p in SOURCE.rglob('*') if p.is_file()}
    backup = REPO/'artifacts/issue-1108-armour-repair'/uuid.uuid4().hex
    shutil.copytree(SOURCE, backup/'original')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    targets = sorted([obj for obj in meshes if obj.name in proposal['original_vertices']], key=lambda obj: obj.name)
    assert len(targets) == 12 and len(meshes) == 150
    changes = [repair_plate(obj) for obj in targets]
    assert changes == proposal['changes']
    current = geometry()
    assert all(current[name] == value for name, value in proposal['unchanged_mesh_snapshots'].items())
    assert proposal['original_vertices'] == {obj.name: [list(v.co) for v in obj.data.vertices] for obj in targets}
    assert bounds(meshes) == proposal['bounds_before_and_after']
    measurements = {obj.name: measure(obj) for obj in targets}
    assert all(value['triangle_signed_volume'] > 0 and value['all_edges_manifold']
               and not value['nonadjacent_triangle_intersections'] for value in measurements.values())
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    export_glb_to(SOURCE/'model.glb')
    save_blend_to(SOURCE/'model.blend')
    previous = {key: meta[key] for key in ['blend_sha256', 'glb_sha256']}
    meta['revision'] = 4
    for ext in ['blend', 'glb']:
        meta[ext+'_sha256'] = sha(SOURCE/('model.'+ext))
    meta['generator_sha256'] = sha(REPO/'tools/blender/build_assault_fighter.py')
    meta['helper_sha256'] = {'fighter_plate_topology.py': sha(Path(__file__).with_name('fighter_plate_topology.py'))}
    meta['faces'] = sum(len(obj.data.polygons) for obj in meshes)
    meta['technical_armour_repair'] = dict(issue=1108, previous=previous,
        script='tools/blender/apply_fighter_armour_repair.py', script_sha256=sha(Path(__file__)),
        original_vertices_and_other_meshes_unchanged=True, new_wear_or_textures=False)
    (SOURCE/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    current = geometry()
    assert all(current[name] == value for name, value in proposal['unchanged_mesh_snapshots'].items())
    assert proposal['original_vertices'] == {name: [list(v.co) for v in bpy.data.objects[name].data.vertices]
                                             for name in proposal['original_vertices']}
    scene = bpy.context.scene
    points = evaluated_points(meshes)
    for name, direction in VIEWS:
        fit_camera(scene, points, direction)
        render_to(scene, SOURCE/(name+'.png'))
    report = dict(issue=1108, revision=4, previous=previous,
        blend_sha256=meta['blend_sha256'], glb_sha256=meta['glb_sha256'],
        proposal_sha256=sha(OUTPUT/'proposal.json'), helper_sha256=meta['helper_sha256']['fighter_plate_topology.py'],
        migration_sha256=sha(Path(__file__)), original_files=original_files,
        backup=str((backup/'original').relative_to(REPO)).replace('\\', '/'),
        changes=changes, native_measurements=measurements, saved_native_reopened=True,
        original_vertices_and_other_meshes_unchanged=True, final_visual_acceptance=False)
    (OUTPUT/'applied.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FIGHTER_ARMOUR_REPAIR_APPLIED_OK', len(changes), flush=True)


if __name__ == '__main__':
    main()
