"""Native/GLB structural checks; does not substitute for visual acceptance."""
import hashlib
import json
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'


def bounds(meshes):
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    points=[evaluated.matrix_world @ Vector(corner) for obj in meshes
            for evaluated in [obj.evaluated_get(graph)] for corner in evaluated.bound_box]
    return [min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)]


def check_meshes(meshes,allow_packed_images=False):
    assert meshes
    for obj in meshes:
        assert len(obj.data.polygons)>0 and obj.data.materials,obj.name
        assert all(p.area>1e-10 for p in obj.data.polygons),obj.name
        bm=bmesh.new()
        bm.from_mesh(obj.data)
        assert not any(len(edge.link_faces)>2 for edge in bm.edges),obj.name+' non-manifold fan'
        assert not any(len(edge.link_faces)==0 for edge in bm.edges),obj.name+' loose edge'
        if all(edge.is_manifold for edge in bm.edges):
            assert bm.calc_volume(signed=True)>0,obj.name+' inward or collapsed shell'
        bm.free()
    assert not any(image.source=='FILE' and not (allow_packed_images and image.packed_file) for image in bpy.data.images)


def main():
    manifest=json.loads((ROOT/'model.json').read_text())
    for extension in ['blend','glb']:
        assert hashlib.sha256((ROOT/f'model.{extension}').read_bytes()).hexdigest()==manifest[extension+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    assert len(meshes)==manifest['mesh_objects']
    check_meshes(meshes)
    native_bounds=bounds(meshes)
    assert bpy.context.scene.camera.data.type=='ORTHO'
    assert bpy.context.scene.render.film_transparent
    assert any(collection.asset_data for collection in bpy.data.collections)
    assert len([obj for obj in meshes if obj.name.startswith('Swept tessellated wing armour')])==12
    assert len([obj for obj in meshes if obj.name.startswith('Continuous wing load-bearing web')])==2
    assert len([obj for obj in meshes if obj.name.startswith('Outer drive silver fairing')])==2
    assert not any(obj.name.startswith('Swept wing access panel') for obj in meshes)
    shell=bpy.data.objects['Raised central dorsal shell']
    # Four actual recessed pockets: ray must pass below the surrounding pressure skin.
    for x in [-.34,.34]:
        for y in [-.22,.48]:
            origin=Vector((x,y*.83,2))
            inverse=shell.matrix_world.inverted()
            hit,point,_,_=shell.ray_cast(inverse @ origin,Vector((0,0,-1)))
            assert hit and (shell.matrix_world @ point).z<.44,'Pocket is not recessed'
    nozzles=[obj for obj in meshes if obj.name in ['Main exhaust -1','Main exhaust 1','Outer auxiliary exhaust -1','Outer auxiliary exhaust 1']]
    assert len(nozzles)==4
    for obj in nozzles:
        # Hollow centre: no mesh cap across exhaust axis.
        coords=[v.co for v in obj.data.vertices]
        centre_x=(min(v.x for v in coords)+max(v.x for v in coords))/2
        centre_z=(min(v.z for v in coords)+max(v.z for v in coords))/2
        hit,_,_,_=obj.ray_cast(Vector((centre_x,4,centre_z)),Vector((0,-1,0)))
        assert not hit,obj.name
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(imported)
    assert len(imported)==len(meshes)
    imported_bounds=bounds(imported)
    assert max(abs(a-b) for a,b in zip(native_bounds,imported_bounds))<.002
    assert len({slot.material.name for obj in imported for slot in obj.material_slots})==7
    report=dict(issue=953,blend_sha256=manifest['blend_sha256'],glb_sha256=manifest['glb_sha256'],
                native_meshes=len(meshes),imported_meshes=len(imported),bounds=native_bounds,
                actual_recesses=4,hollow_nozzles=4,material_count=7,
                visual_acceptance='not established by technical checks')
    output=REPO/'artifacts/ship-reference-study/fighter-validation.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('ASSAULT_FIGHTER_NATIVE_GLB_OK',len(imported),flush=True)


if __name__=='__main__':
    main()
