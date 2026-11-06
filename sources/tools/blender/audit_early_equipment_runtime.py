"""Actual read-only native/export comparisons for existing cannons and shields."""
import json
from pathlib import Path
import sys
import bpy
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_transporter_runtime import snapshot, sha
from catalogue_rendering import evaluated_points, fit_camera

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / 'docs/assets/reconstruction/evidence/early-equipment-runtime'
VIEWS = [('front-quarter', (7, -12, 9)), ('rear-quarter', (-7, 12, 8))]


def render(folder, kind, cameras):
    scene = bpy.context.scene
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    for name, (location, rotation, scale) in cameras.items():
        scene.camera.location = location
        scene.camera.rotation_euler = rotation
        scene.camera.data.ortho_scale = scale
        scene.render.filepath = str(folder / (kind + '-' + name + '.png'))
        bpy.ops.render.render(write_still=True)


def main():
    for slug in ['photon-cannon', 'plasma-cannon', 'shield-x10', 'shield-x20', 'shield-x30', 'shield-x40', 'shield-x50']:
        source = REPO / 'docs/assets/reconstruction/hardpoints' / slug
        output = OUTPUT / slug
        output.mkdir(parents=True, exist_ok=True)
        before = {name: sha(source / name) for name in ['model.blend', 'model.glb', 'model.json']}
        bpy.ops.wm.open_mainfile(filepath=str(source / 'model.blend'))
        native, materials, positions = snapshot()
        points = evaluated_points([o for o in bpy.context.scene.objects if o.type == 'MESH'])
        cameras = {}
        for name, direction in VIEWS:
            fit_camera(bpy.context.scene, points, direction)
            cam = bpy.context.scene.camera
            cameras[name] = (cam.location.copy(), cam.rotation_euler.copy(), cam.data.ortho_scale)
        render(output, 'native', cameras)
        for obj in list(bpy.context.scene.objects):
            if obj.type == 'MESH': bpy.data.objects.remove(obj, do_unlink=True)
        for mesh in list(bpy.data.meshes):
            if mesh.users == 0: bpy.data.meshes.remove(mesh)
        for material in list(bpy.data.materials):
            if material.users == 0: bpy.data.materials.remove(material)
        bpy.ops.import_scene.gltf(filepath=str(source / 'model.glb'))
        imported, other_materials, other_positions = snapshot()
        assert native.keys() == imported.keys(), 'Object identity differs'
        assert materials.keys() == other_materials.keys(), 'Material identity differs'
        differences = {}
        for name in native:
            errors = []
            for a, b in [(positions[name], other_positions[name]), (other_positions[name], positions[name])]:
                tree = KDTree(len(b))
                for index, point in enumerate(b): tree.insert(point, index)
                tree.balance()
                errors.append(max(tree.find(point)[2] for point in a))
            differences[name] = dict(maximum_bidirectional_position_error=max(errors),
                maximum_bounds_error=max(abs(a-b) for a,b in zip(native[name]['bounds'], imported[name]['bounds'])))
        material_error = max(abs(a-b) for name in materials for a,b in zip(materials[name][0]+materials[name][1:], other_materials[name][0]+other_materials[name][1:]))
        render(output, 'imported', cameras)
        assert before == {name: sha(source / name) for name in before}, 'Source changed'
        report = dict(issue=1103, id='openfa:'+slug, blender=bpy.app.version_string,
            auditor_sha256=sha(Path(__file__)), snapshot_helper_sha256=sha(Path(__file__).with_name('audit_transporter_runtime.py')),
            sources=before, native=native, imported=imported, comparisons=differences,
            native_materials=materials, imported_materials=other_materials, maximum_material_value_error=material_error,
            render_sha256={p.name:sha(p) for p in sorted(output.glob('*.png'))}, source_assets_unchanged=True,
            final_visual_acceptance=False, scope='Evaluated geometry/material and actual matched-render evidence only; no final art, UV/state/mount or game integration acceptance.')
        (output / 'runtime-audit.json').write_text(json.dumps(report, indent=2)+'\n')
        print('EARLY_EQUIPMENT_RUNTIME_AUDIT_OK', slug, len(native), flush=True)


if __name__ == '__main__':
    main()
