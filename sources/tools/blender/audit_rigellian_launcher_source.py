"""Read-only RI18 source-motion audit before choosing the canonical remaster."""
import hashlib
import json
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'sources/docs/assets/reconstruction/launch-facilities/rigellian/ri18'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world @ v.co for v in obj.data.vertices],
                               [tuple(p.vertices) for p in obj.data.polygons])


def inspect():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    leaves = [obj for obj in meshes if obj.name.startswith('Split pointed cap') and 'scuff' not in obj.name]
    assert len(leaves) == 2
    topology = {}
    for obj in meshes:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        topology[obj.name] = dict(closed=all(e.is_manifold for e in bm.edges),
                                  signed_volume=bm.calc_volume(signed=True))
        bm.free()
    fixed = [obj for obj in meshes if obj.name in [
        'RI18 stepped green silo casing','RI18 bronze foundation drum',
        'RI18 angled bronze attachment','RI18 angled attachment root sleeve']]
    assert len(fixed) == 4
    samples = []
    matrices = {}
    for frame in range(1,62):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        shapes = {obj.name: tree(obj) for obj in leaves+fixed}
        intersections = []
        for leaf in leaves:
            for other in fixed:
                pairs = shapes[leaf.name].overlap(shapes[other.name])
                if pairs:
                    envelopes = []
                    for a,b in pairs:
                        left = [(leaf.matrix_world @ leaf.data.vertices[i].co).z
                                for i in leaf.data.polygons[a].vertices]
                        right = [(other.matrix_world @ other.data.vertices[i].co).z
                                 for i in other.data.polygons[b].vertices]
                        envelopes.append((max(min(left),min(right)),min(max(left),max(right))))
                    intersections.append(dict(leaf=leaf.name, fixed=other.name,
                        triangle_pairs=len(pairs),
                        triangle_overlap_z_envelope=[min(a for a,b in envelopes),max(b for a,b in envelopes)],
                        seating_vs_unwanted_penetration_classified=False))
        heights = []
        if frame == 31:
            all_shapes = [tree(obj) for obj in meshes]
            for x,y in [(0,0),(.10,0),(-.10,0),(0,.10),(0,-.10)]:
                hits = [t.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),8)[0] for t in all_shapes]
                heights.append(max((p.z for p in hits if p is not None),default=-20))
        samples.append(dict(frame=frame, leaf_fixed_surface_intersections=intersections,
                            open_bore_heights=heights))
        matrices[frame] = {obj.name:[float(v) for row in obj.matrix_world for v in row] for obj in meshes}
    return dict(meshes=len(meshes), topology=topology, samples=samples), matrices


def main():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'),load_ui=False,use_scripts=False)
    bpy.context.scene.render.fps = 30
    native, native_matrices = inspect()
    for obj in list(bpy.context.scene.objects):
        if obj.type in ['MESH','EMPTY']:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE/'model.glb'))
    imported, imported_matrices = inspect()
    assert native_matrices.keys() == imported_matrices.keys()
    assert all(native_matrices[f].keys() == imported_matrices[f].keys() for f in native_matrices)
    error = max(abs(a-b) for f in native_matrices for name in native_matrices[f]
                for a,b in zip(native_matrices[f][name],imported_matrices[f][name]))
    report = dict(id='openfa:building/legacy/057',issue=253,
                  source_blend_sha256=sha(SOURCE/'model.blend'),source_glb_sha256=sha(SOURCE/'model.glb'),
                  auditor_sha256=sha(Path(__file__)),blender=bpy.app.version_string,
                  native=native,imported=imported,maximum_native_import_matrix_error=error,
                  scope='Diagnostic only: sampled surface intersections include intentional seating contacts. Not continuous clearance or final acceptance.',
                  canonical_delivery_ready=False)
    destination = ROOT/'sources/docs/reconstruction/models/ri18-source-motion-audit.json'
    destination.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI18_SOURCE_MOTION_AUDITED',error,flush=True)


if __name__ == '__main__':
    main()
