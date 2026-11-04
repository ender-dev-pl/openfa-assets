"""Original fighter assertions plus actual repaired-panel triangle/intersection checks."""
import json
import sys
from pathlib import Path

import bpy
import bmesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_detail_uv_proposal import geometry
from probe_fighter_armour_tessellation import measure, sha, SOURCE, OUTPUT
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from catalogue_rendering import evaluated_points, fit_camera
from apply_fighter_armour_repair import VIEWS
import verify_assault_fighter as original

REPO = Path(__file__).resolve().parents[2]


def check(targets, imported=False):
    measurements = {}
    for obj in targets:
        original_mesh = obj.data
        temporary = None
        if imported:
            temporary = original_mesh.copy()
            bm = bmesh.new()
            bm.from_mesh(temporary)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
            bm.to_mesh(temporary)
            bm.free()
            obj.data = temporary
        try:
            measurements[obj.name] = measure(obj)
        finally:
            obj.data = original_mesh
            if temporary:
                bpy.data.meshes.remove(temporary)
    assert len(measurements) == 12
    for name, value in measurements.items():
        assert value['triangle_signed_volume'] > 1e-8, name+' inward/collapsed actual triangles'
        assert value['all_edges_manifold'] and value['minimum_face_area'] > 1e-10
        assert not value['nonadjacent_triangle_intersections'], name+' intersecting nonadjacent triangles'
    return measurements


def main():
    meta = json.loads((SOURCE/'model.json').read_text())
    proposal = json.loads((OUTPUT/'proposal.json').read_text())
    applied = json.loads((OUTPUT/'applied.json').read_text())
    for ext in ['blend', 'glb']:
        assert meta[ext+'_sha256'] == applied[ext+'_sha256'] == sha(SOURCE/('model.'+ext))
    assert meta['helper_sha256']['fighter_plate_topology.py'] == sha(Path(__file__).with_name('fighter_plate_topology.py'))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'))
    snapshot = geometry()
    assert all(snapshot[name] == value for name, value in proposal['unchanged_mesh_snapshots'].items())
    for name, vertices in proposal['original_vertices'].items():
        assert vertices == [list(vertex.co) for vertex in bpy.data.objects[name].data.vertices]
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    targets = [obj for obj in meshes if obj.name in proposal['original_vertices']]
    native = check(targets)
    cameras = {}
    for name, direction in VIEWS:
        fit_camera(bpy.context.scene, evaluated_points(meshes), direction)
        camera = bpy.context.scene.camera
        cameras[name] = (camera.location.copy(), camera.rotation_euler.copy(), camera.data.ortho_scale)
    original.main()
    imported = check([obj for obj in bpy.context.scene.objects if obj.name in proposal['original_vertices']], imported=True)
    for name in native:
        assert abs(native[name]['triangle_signed_volume']-imported[name]['triangle_signed_volume']) < 1e-6
    scene = setup_scene(768, 48)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE/'model.glb'))
    for name, _ in VIEWS:
        scene.camera.location, scene.camera.rotation_euler, scene.camera.data.ortho_scale = cameras[name]
        render_to(scene, SOURCE/('imported-glb-'+name+'.png'))
    report = dict(issue=1108, id=meta['id'], revision=meta['revision'],
        blend_sha256=meta['blend_sha256'], glb_sha256=meta['glb_sha256'],
        verifier_sha256=sha(Path(__file__)), original_verifier_sha256=sha(Path(original.__file__)),
        mesh_objects=150, repaired_panels=12, native=native, imported=imported,
        original_vertices_and_other_meshes_unchanged=True,
        checks=['Original native/import structural, recessed-well, exhaust and bounds assertions',
                'All actual repaired-panel triangle volumes positive in native and GLB',
                'Closed welded panel surfaces without nonadjacent triangle intersections',
                'Every original panel vertex and the other 138 mesh snapshots preserved',
                'Matched-camera native and actual GLB renders'], final_visual_acceptance=False)
    (SOURCE/'technical-review.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FIGHTER_ARMOUR_NATIVE_GLB_REPAIR_OK', len(native), flush=True)


if __name__ == '__main__':
    main()
