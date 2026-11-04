"""Read-only in-memory correction study for issue #1108; never saves a model."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fighter_plate_topology import repair_plate
from audit_detail_uv_proposal import geometry
from build_refined_terran import render_to
from catalogue_rendering import evaluated_points, fit_camera
from verify_assault_fighter import bounds

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'
OUTPUT = REPO/'docs/assets/reconstruction/evidence/fighter-armour-repair'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(obj):
    graph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
    mesh.calc_loop_triangles()
    points = [vertex.co.copy() for vertex in mesh.vertices]
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    volume = sum(points[a].dot(points[b].cross(points[c]))/6 for a, b, c in triangles)
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True)
    intersections = sorted({tuple(sorted((a, b))) for a, b in tree.overlap(tree)
                            if a != b and not set(triangles[a]) & set(triangles[b])})
    bm = bmesh.new()
    bm.from_mesh(mesh)
    result = dict(vertices=len(points), polygons=len(mesh.polygons), triangles=len(triangles),
        triangle_signed_volume=volume, all_edges_manifold=all(edge.is_manifold for edge in bm.edges),
        nonadjacent_triangle_intersections=[list(pair) for pair in intersections],
        minimum_face_area=min(face.calc_area() for face in bm.faces))
    bm.free()
    evaluated.to_mesh_clear()
    return result


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_hashes = {ext: sha(SOURCE/('model.'+ext)) for ext in ['blend', 'glb']}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'))
    targets = sorted([obj for obj in bpy.context.scene.objects if obj.name.startswith('Swept tessellated wing armour')], key=lambda obj: obj.name)
    assert len(targets) == 12
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    original = geometry()
    original_bounds = bounds(meshes)
    original_vertices = {obj.name: [list(v.co) for v in obj.data.vertices] for obj in targets}
    points = evaluated_points(meshes)
    views = [('front-quarter', (8, -12, 10)), ('top', (0, 0, 20)), ('side', (14, 0, 4)), ('belly', (7, -10, -12))]
    renders = {}
    for name, direction in views:
        fit_camera(bpy.context.scene, points, direction)
        path = OUTPUT/('proposal-'+name+'-before.png')
        render_to(bpy.context.scene, path)
        renders[path.name] = sha(path)
    before = {obj.name: measure(obj) for obj in targets}
    changes = [repair_plate(obj) for obj in targets]
    bpy.context.view_layer.update()
    after = {obj.name: measure(obj) for obj in targets}
    current = geometry()
    assert all(original[name] == value for name, value in current.items() if value['type'] == 'MESH' and name not in original_vertices)
    assert original_vertices == {obj.name: [list(v.co) for v in obj.data.vertices] for obj in targets}
    assert bounds(meshes) == original_bounds
    for name, direction in views:
        fit_camera(bpy.context.scene, points, direction)
        path = OUTPUT/('proposal-'+name+'-after.png')
        render_to(bpy.context.scene, path)
        renders[path.name] = sha(path)
    assert source_hashes == {ext: sha(SOURCE/('model.'+ext)) for ext in ['blend', 'glb']}
    report = dict(issue=1108, source_hashes=source_hashes, probe_sha256=sha(Path(__file__)),
        helper_sha256=sha(Path(__file__).with_name('fighter_plate_topology.py')),
        before=before, after=after, changes=changes, source_assets_unchanged=True,
        other_mesh_geometry_unchanged=True, original_vertices=original_vertices, bounds_before_and_after=original_bounds,
        unchanged_mesh_snapshots={name: value for name, value in original.items() if value['type'] == 'MESH' and name not in original_vertices},
        renders=renders,
        final_visual_acceptance=False, scope='In-memory cap connectivity proposal, not an applied source/export repair or artistic acceptance.')
    (OUTPUT/'proposal.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FIGHTER_ARMOUR_TESSELLATION_PROBE_OK', json.dumps(dict(before=before, after=after)), flush=True)


if __name__ == '__main__':
    main()
