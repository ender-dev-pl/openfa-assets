"""Inspect unchanged transporter files and render their actual native/imported scenes."""
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_rigellian_filtration import material_values

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / 'docs/assets/bootstrap-3d/transporter-inspired'
OUTPUT = REPO / 'docs/assets/reconstruction/evidence/transporter-runtime'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    result = {}; positions = {}
    graph = bpy.context.evaluated_depsgraph_get()
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for obj in meshes:
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        assert points and mesh.polygons and obj.data.materials
        bounds = [min(p[a] for p in points) for a in range(3)] + [max(p[a] for p in points) for a in range(3)]
        positions[obj.name] = [tuple(p) for p in points]
        coordinates = sorted({tuple(round(v, 4) for v in p) for p in points})
        result[obj.name] = dict(bounds=bounds, geometric_positions=len(coordinates),
                                positions_sha256=hashlib.sha256(json.dumps(coordinates).encode()).hexdigest(),
                                evaluated_vertices=len(mesh.vertices), evaluated_faces=len(mesh.polygons),
                                materials=[m.name for m in obj.data.materials],
                                animated=bool(obj.animation_data))
        evaluated.to_mesh_clear()
    return result, material_values(meshes), positions


def render(label):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    for name, location in [('front-quarter', (9, -12, 9)), ('rear-quarter', (-9, -12, 9))]:
        scene.camera.location = location
        scene.camera.rotation_euler = (Vector((0, 0, 1)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(OUTPUT / (label + '-' + name + '.png'))
        bpy.ops.render.render(write_still=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    before = {name: sha(SOURCE / name) for name in ['transporter.blend', 'transporter.glb', 'manifest.json']}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE / 'transporter.blend'))
    native, native_materials, native_positions = snapshot()
    assert len(native) == json.loads((SOURCE / 'manifest.json').read_text())['mesh_objects'] == 61
    assert not any(i.source == 'FILE' for i in bpy.data.images)
    render('native')
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
    # Remove unused materials so original and imported material names remain comparable.
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for material in list(bpy.data.materials):
        if material.users == 0:
            bpy.data.materials.remove(material)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE / 'transporter.glb'))
    imported, imported_materials, imported_positions = snapshot()
    assert set(native) == set(imported), 'Imported object identity differs'
    differences = {}
    for name, record in native.items():
        other = imported[name]
        differences[name] = dict(maximum_bound_error=max(abs(a-b) for a, b in zip(record['bounds'], other['bounds'])),
                                 rounded_position_sets_equal=record['positions_sha256'] == other['positions_sha256'])
    for name in native:
        errors = []
        for source, target in [(native_positions[name], imported_positions[name]), (imported_positions[name], native_positions[name])]:
            tree = KDTree(len(target))
            for i, point in enumerate(target): tree.insert(point, i)
            tree.balance()
            errors.append(max(tree.find(point)[2] for point in source))
        differences[name]['maximum_bidirectional_nearest_position_error'] = max(errors)
    assert native_materials.keys() == imported_materials.keys(), 'Material names differ'
    material_error = max(abs(a-b) for name in native_materials for a,b in zip(native_materials[name][0]+native_materials[name][1:], imported_materials[name][0]+imported_materials[name][1:]))
    render('imported')
    assert before == {name: sha(SOURCE / name) for name in before}, 'Source assets changed'
    report = dict(issue=1100, blender=bpy.app.version_string, auditor_sha256=sha(Path(__file__)),
                  sources=before, native=native, imported=imported,
                  native_materials=native_materials, imported_materials=imported_materials,
                  comparisons=differences, maximum_material_value_error=material_error,
                  render_sha256={p.name: sha(p) for p in sorted(OUTPUT.glob('*.png'))},
                  source_assets_unchanged=True, final_visual_acceptance=False,
                  scope='Actual unchanged native reopen and GLB import/render. Differences are evidence, not automatic acceptance; no topology, UV, animation/state or mount completeness claim.')
    (OUTPUT / 'runtime-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print('TRANSPORTER_RUNTIME_AUDIT_OK', len(native), flush=True)


if __name__ == '__main__':
    main()
