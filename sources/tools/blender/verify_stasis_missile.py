"""Verify actual Stasis recess, casing relief and nozzle in native/GLB geometry."""
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

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/stasis'


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
    body=lookup['Stasis straight green pressure casing'];head=lookup['Stasis rounded green head']
    for name,z,skin_obj in [('Stasis pale upper band',5.46,head),('Stasis thin pale body joint',4.22,body)]:
        inner=ray(lookup[name],(0,0,z),(1,0,0));skin=ray(skin_obj,(2,0,z),(-1,0,0))
        assert inner is not None and skin is not None and inner.x<skin.x,'Pale ring must sit on casing'
    collar=lookup['Stasis broad pale lower collar']
    marks=[obj for obj in meshes if obj.name.startswith('Stasis conformal maroon round marking')]
    assert len(marks)==4
    for mark in marks:
        top=[];back=[];normals=mark.matrix_world.to_3x3().inverted().transposed()
        for face in mark.data.polygons:
            point=mark.matrix_world @ face.center;radial=Vector((point.x,point.y,0)).normalized()
            facing=(normals @ face.normal).normalized().dot(radial)
            if abs(facing)<.8: continue
            skin=ray(collar,(0,0,point.z),radial)
            assert skin is not None
            offset=Vector((point.x-skin.x,point.y-skin.y,0)).dot(radial)
            (top if facing>0 else back).append(offset)
        assert top and back
        assert min(top)>.0015 and max(top)<.007,'Collar mark buried or floating'
        assert min(back)>-.008 and max(back)<-.003,'Mark back must embed in collar'
    braces=sorted([obj for obj in meshes if obj.name.startswith('Stasis open tail frame brace')],key=lambda obj:obj.name)
    assert len(braces)==4
    bell=lookup['Stasis hollow red propulsion bell'];mount=lookup['Stasis annular engine mount']
    for i,brace in enumerate(braces):
        angle=math.pi/4+i*math.pi/2;radial=Vector((math.cos(angle),math.sin(angle),0))
        for z,other in [(.224,bell),(1.03,mount)]:
            a=ray(brace,(0,0,z),radial);b=ray(brace,Vector((0,0,z))+radial,-radial)
            c=ray(other,(0,0,z),radial);d=ray(other,Vector((0,0,z))+radial,-radial)
            assert all(p is not None for p in [a,b,c,d])
            def r(p): return (p.x*p.x+p.y*p.y)**.5
            assert max(r(a),r(c))<min(r(b),r(d)),'Frame brace must contact bell and engine mount'
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis capped'
    inner=ray(bell,(0,0,.22),(1,0,0));outer=ray(bell,(1,0,.22),(-1,0,0))
    assert inner is not None and outer is not None and .038<outer.x-inner.x<.052
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .94<min(hits)<.98,('Propulsion obstruction',min(hits))
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
    report=dict(issue=967,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, positive volumes and matching evaluated bounds/materials',
                'Seated pale bands','Four conformal mark faces and embedded backs',
                'Eight actual frame contacts with bell/mount','Measured nozzle wall and clear path to throat',
                'No external images or invented animation'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('STASIS_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
