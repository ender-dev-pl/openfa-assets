"""Verify actual Nuclear recess, casing relief and nozzle in native/GLB geometry."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/nuclear'


def geometry_bounds(meshes):
    graph=bpy.context.evaluated_depsgraph_get();points=[]
    bpy.context.view_layer.update()
    for obj in meshes:
        evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
        try:
            points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    return [min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)]


def structure(meshes):
    lookup={obj.name:obj for obj in meshes}
    casing=lookup['Nuclear tapered dark pressure casing']
    pods=sorted([obj for obj in meshes if obj.name.startswith('Nuclear swept red tail pod')],key=lambda obj:obj.name)
    feet=sorted([obj for obj in meshes if obj.name.startswith('Nuclear silver tail foot')],key=lambda obj:obj.name)
    assert len(pods)==4 and len(feet)==4
    for i,pod in enumerate(pods):
        angle=math.pi/4+i*math.pi/2;direction=Vector((math.cos(angle),math.sin(angle),0))
        for z in [1.25,1.65]:
            inside=ray(pod,(0,0,z),direction);skin=ray(casing,(0,0,z),direction)
            outside=ray(pod,Vector((0,0,z))+direction*2,-direction)
            assert all(p is not None for p in [inside,skin,outside])
            assert inside.length<skin.length<outside.length,'Red tail root must meet casing'
    assert len([obj for obj in meshes if obj.name.startswith('Nuclear upper silver side form')])==2
    marks=[obj for obj in meshes if obj.name.startswith('Nuclear conformal yellow trefoil blade')]
    assert len(marks)==3
    for mark in marks:
        top=[];back=[]
        normals=mark.matrix_world.to_3x3().inverted().transposed()
        for face in mark.data.polygons:
            point=mark.matrix_world @ face.center
            radial=Vector((point.x,point.y,0)).normalized()
            facing=(normals @ face.normal).normalized().dot(radial)
            if abs(facing)<.8: continue
            skin=ray(casing,(0,0,point.z),radial)
            assert skin is not None
            offset=Vector((point.x-skin.x,point.y-skin.y,0)).dot(radial)
            (top if facing>0 else back).append(offset)
        assert top and back
        assert min(top)>.001 and max(top)<.006,'Trefoil face buried or floating'
        assert min(back)>-.007 and max(back)<-.002,'Trefoil back must embed in casing'
    bell=lookup['Nuclear hollow propulsion bell']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis capped'
    inner=ray(bell,(0,0,.20),(1,0,0));outer=ray(bell,(1,0,.20),(-1,0,0))
    assert inner is not None and outer is not None and .027<outer.x-inner.x<.038
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .46<min(hits)<.51,('Nozzle obstruction',min(hits))
    assert 'Nuclear long yellow tip' in lookup
    assert not any(obj.animation_data for obj in meshes)


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    for ext in ['blend','glb']:
        assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(meshes);structure(meshes)
    assert len(meshes)==meta['mesh_objects']
    native=geometry_bounds(meshes);materials={slot.material.name for obj in meshes for slot in obj.material_slots}
    assert len(materials)==6
    assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
    assert any(c.asset_data for c in bpy.data.collections)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(imported);structure(imported)
    assert len(imported)==len(meshes)
    imported_bounds=geometry_bounds(imported)
    assert max(abs(a-b) for a,b in zip(native,imported_bounds))<.002,(native,imported_bounds)
    assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
    report=dict(issue=964,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, positive volumes, matching materials and evaluated-vertex bounds',
                'Eight actual red-pod/casing root intersections','Three conformal trefoil faces and embedded backs',
                'Four tail feet and two silver upper fittings','Open nozzle axis to throat and measured bell wall',
                'No external images or invented animation'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('NUCLEAR_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
