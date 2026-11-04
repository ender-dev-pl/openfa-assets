"""Render only the repaired details at close range in native and imported scenes."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from catalogue_rendering import evaluated_points, fit_camera
from repair_detail_uvs import verify_detail_uvs

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/detail-uv-repair'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def isolate(names):
    targets = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.hide_render = obj.name not in names
            if obj.name in names:
                targets.append(obj)
    assert {obj.name for obj in targets} == set(names)
    verify_detail_uvs(targets)
    return targets


def corner_uvs(targets):
    graph = bpy.context.evaluated_depsgraph_get()
    result = {}
    for obj in targets:
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
        corners = []
        try:
            for face in mesh.polygons:
                material = mesh.materials[face.material_index]
                texture = material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node
                vector = texture.inputs['Vector']
                uv_name = vector.links[0].from_node.uv_map if vector.is_linked else None
                chart = mesh.uv_layers[uv_name] if uv_name else mesh.uv_layers.active
                for index in face.loop_indices:
                    point = evaluated.matrix_world @ mesh.vertices[mesh.loops[index].vertex_index].co
                    corners.append((point.copy(), tuple(chart.data[index].uv), material.name))
        finally:
            evaluated.to_mesh_clear()
        result[obj.name] = corners
    return result


def compare_corners(native, imported):
    assert native.keys() == imported.keys()
    result = {}
    for name in native:
        maximum_position = maximum_uv = 0
        for origin, destination in [(native[name], imported[name]), (imported[name], native[name])]:
            tree = KDTree(len(destination))
            for index, (point, _, _) in enumerate(destination):
                tree.insert(point, index)
            tree.balance()
            for point, uv, material in origin:
                candidates = []
                for _, index, distance in tree.find_range(point, 1e-5):
                    other_uv, other_material = destination[index][1:]
                    error = max(abs(a-b) for a, b in zip(uv, other_uv))
                    if material == other_material and error <= 1e-5:
                        candidates.append((distance, error))
                assert candidates, name+': missing corresponding shader UV/material corner'
                distance, error = min(candidates)
                maximum_position = max(maximum_position, distance)
                maximum_uv = max(maximum_uv, error)
        result[name] = dict(native_corners=len(native[name]), imported_corners=len(imported[name]),
            maximum_position_error=maximum_position, maximum_uv_error=maximum_uv,
            bidirectional_shader_uv_material_corner_coverage=True)
    return result


def main():
    for slug in ['strategic-bunker', 'ultrathermal-lance']:
        folder = REPO/'docs/assets/reconstruction/buildings/rigellian'/slug
        repair = json.loads((OUTPUT/(slug+'.json')).read_text())
        names = list(repair['uv_checks'])
        before = {ext: sha(folder/('model.'+ext)) for ext in ['blend', 'glb']}
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
        targets = isolate(names)
        native_uvs = corner_uvs(targets)
        scene = bpy.context.scene
        fit_camera(scene, evaluated_points(targets), (6, -13, 8))
        camera = scene.camera
        view = (camera.location.copy(), camera.rotation_euler.copy(), camera.data.ortho_scale)
        native_path = OUTPUT/(slug+'-detail-native.png')
        render_to(scene, native_path)
        scene = setup_scene(900, 64)
        bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
        imported_uvs = corner_uvs(isolate(names))
        uv_comparison = compare_corners(native_uvs, imported_uvs)
        scene.camera.location = view[0]
        scene.camera.rotation_euler = view[1]
        scene.camera.data.ortho_scale = view[2]
        imported_path = OUTPUT/(slug+'-detail-imported.png')
        render_to(scene, imported_path)
        assert before == {ext: sha(folder/('model.'+ext)) for ext in ['blend', 'glb']}
        report = dict(issue=1111, id=repair['id'], blend_sha256=before['blend'], glb_sha256=before['glb'],
            verifier_sha256=sha(Path(__file__)), details=names,
            corner_uv_comparison=uv_comparison,
            native_render_sha256=sha(native_path), imported_render_sha256=sha(imported_path),
            source_assets_unchanged=True, final_visual_acceptance=False,
            scope='Isolated actual repaired details under matched native/import camera and scene lights; no saved source changes.')
        (OUTPUT/(slug+'-roundtrip.json')).write_text(json.dumps(report, indent=2)+'\n')
        print('DETAIL_UV_ROUNDTRIP_RENDERED', slug, flush=True)
    print('DETAIL_UV_ROUNDTRIP_OK', flush=True)


if __name__ == '__main__':
    main()
