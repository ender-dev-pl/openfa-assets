"""Apply the explicitly authorized three-detail UV repair to saved original sources."""
import importlib
import json
import shutil
import sys
import uuid
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_detail_uv_proposal import geometry, images, sha
from repair_detail_uvs import bind_detail_uvs, verify_detail_uvs
from build_refined_terran import render_to, save_blend_to
from catalogue_rendering import evaluated_points, fit_camera

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/detail-uv-repair'
PROPOSAL = REPO/'docs/assets/reconstruction/evidence/detail-uv-proposal'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    backup = REPO/'artifacts/issue-1111-applied-uv-repair'/uuid.uuid4().hex
    backup.mkdir(parents=True)
    for slug, revision in [('bunker', 3), ('ultrathermal_lance', 2)]:
        builder = importlib.import_module('build_rigellian_'+slug)
        folder = builder.ROOT
        meta = json.loads((folder/'model.json').read_text())
        assert meta['revision'] == revision-1, 'This migration only applies to the recorded baseline revision'
        before_files = {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        proposal = json.loads((PROPOSAL/(folder.name+'.json')).read_text())
        assert before_files == proposal['source_files_sha256'], 'Source differs from verified proposal'
        shutil.copytree(folder, backup/folder.name)
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
        before_geometry, before_images = geometry(), images()
        assert before_geometry == proposal['exact_native_geometry_before_and_after']
        assert before_images == proposal['packed_images_before_and_after']
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        changes = bind_detail_uvs(meshes)
        assert changes == proposal['changes']
        assert not bind_detail_uvs(meshes), 'Repair must be idempotent'
        uv_checks = verify_detail_uvs(meshes)
        assert before_geometry == geometry() and before_images == images()
        bpy.ops.object.select_all(action='DESELECT')
        root = bpy.data.objects['PlacementRoot']
        for obj in bpy.context.scene.objects:
            if obj.type in ['MESH', 'EMPTY']:
                obj.select_set(True)
        bpy.context.view_layer.objects.active = root
        builder.export_glb_to(folder/'model.glb')
        save_blend_to(folder/'model.blend')
        previous = {key: meta[key] for key in ['blend_sha256', 'glb_sha256']}
        meta['revision'] = revision
        for ext in ['blend', 'glb']:
            meta[ext+'_sha256'] = sha(folder/('model.'+ext))
        meta['generator_sha256'] = sha(Path(builder.__file__))
        meta['helper_sha256']['repair_detail_uvs.py'] = sha(Path(__file__).with_name('repair_detail_uvs.py'))
        meta['technical_uv_repair'] = dict(issue=1111, previous=previous,
            script='tools/blender/apply_detail_uv_repair.py', script_sha256=sha(Path(__file__)),
            changes=changes, geometry_material_assignments_and_textures_unchanged=True)
        (folder/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
        assert before_geometry == geometry() and before_images == images(), 'Saved source changed more than UVs'
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        verify_detail_uvs(meshes)
        scene = bpy.context.scene
        points = evaluated_points(meshes)
        for name, direction in builder.VIEWS:
            fit_camera(scene, points, direction)
            render_to(scene, folder/(name+'.png'))
        report = dict(issue=1111, id=meta['id'], revision=revision,
            before_source_files_sha256=before_files, previous=previous,
            blend_sha256=meta['blend_sha256'], glb_sha256=meta['glb_sha256'],
            repair_script_sha256=sha(Path(__file__)),
            helper_sha256=sha(Path(__file__).with_name('repair_detail_uvs.py')),
            changes=changes, uv_checks=uv_checks, exact_native_geometry_before_and_after=before_geometry,
            packed_images_before_and_after=before_images,
            saved_native_reopened=True, idempotent=True,
            original_backup=str((backup/folder.name).relative_to(REPO)).replace('\\', '/'),
            final_visual_acceptance=False)
        (OUTPUT/(folder.name+'.json')).write_text(json.dumps(report, indent=2)+'\n')
        print('DETAIL_UV_REPAIR_APPLIED', meta['id'], revision, flush=True)
    print('DETAIL_UV_REPAIR_APPLY_OK', flush=True)


if __name__ == '__main__':
    main()
