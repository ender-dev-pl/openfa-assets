"""Disambiguate local shell orientation from mirrored world transforms; no asset writes."""
import hashlib
import json
from pathlib import Path
import bpy
import bmesh

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'
OUTPUT=REPO/'docs/assets/reconstruction/evidence/catalogue-topology'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect():
    obj=bpy.data.objects['Swept tessellated wing armour']
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    bm=bmesh.new();bm.from_mesh(mesh)
    bm.normal_update()
    local=bm.calc_volume(signed=True)
    mesh.calc_loop_triangles()
    mesh_triangle_volume=0.0
    for triangle in mesh.loop_triangles:
        a,b,c=[mesh.vertices[i].co for i in triangle.vertices]
        mesh_triangle_volume+=a.dot(b.cross(c))/6
    triangulated=bm.copy();bmesh.ops.triangulate(triangulated,faces=list(triangulated.faces))
    triangulated.normal_update();triangulated_volume=triangulated.calc_volume(signed=True);triangulated.free()
    max_nonplanarity=max(abs((v.co-face.verts[0].co).dot(face.normal)) for face in bm.faces for v in face.verts)
    bm.transform(evaluated.matrix_world);bm.normal_update();world=bm.calc_volume(signed=True)
    result=dict(object=obj.name,world_matrix=[list(row) for row in evaluated.matrix_world],
        world_determinant=evaluated.matrix_world.to_3x3().determinant(),
        local_signed_volume=local,world_signed_volume=world,
        actual_mesh_triangle_volume=mesh_triangle_volume,bmesh_triangulated_volume=triangulated_volume,maximum_face_nonplanarity=max_nonplanarity,
        all_edges_manifold=all(e.is_manifold for e in bm.edges))
    bm.free();evaluated.to_mesh_clear();return result


def main():
    hashes={name:sha(SOURCE/name) for name in ['model.blend','model.glb']}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'));native=inspect()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE/'model.glb'));imported=inspect()
    assert hashes=={name:sha(SOURCE/name) for name in hashes}
    report=dict(issue=1107,probe_sha256=sha(Path(__file__)),sources=hashes,native=native,imported=imported,
        source_assets_unchanged=True,scope='Actual local/world winding and transform determinant for the flagged armour object; does not change geometry or accept final art.')
    (OUTPUT/'assault-fighter-winding.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ASSAULT_FIGHTER_WINDING_PROBE_OK',json.dumps(dict(native=native,imported=imported)),flush=True)


if __name__=='__main__': main()
