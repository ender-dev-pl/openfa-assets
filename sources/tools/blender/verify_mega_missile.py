"""Verify actual Mega recess, casing relief and nozzle in native/GLB geometry."""
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

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/mega'


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
    body=lookup['Mega cylindrical pressure casing']
    vanes=sorted([obj for obj in meshes if obj.name.startswith('Mega solid diamond vane')],key=lambda obj:obj.name)
    panels=sorted([obj for obj in meshes if obj.name.startswith('Mega thick copper lower panel')],key=lambda obj:obj.name)
    assert len(vanes)==3 and len(panels)==3
    assert len([obj for obj in meshes if obj.name.startswith('Mega vane transverse rib')])==36
    for i,(vane,panel) in enumerate(zip(vanes,panels)):
        angle=[-math.pi/2,math.pi/6,5*math.pi/6][i]
        radial=Vector((math.cos(angle),math.sin(angle),0));tangent=Vector((-math.sin(angle),math.cos(angle),0))
        for z in [1.8,3.5]:
            inside=ray(vane,(0,0,z),radial);skin=ray(body,(0,0,z),radial)
            outside=ray(vane,Vector((0,0,z))+radial*2,-radial)
            assert all(p is not None for p in [inside,skin,outside])
            assert inside.length<skin.length<outside.length,'Vane root must contact pressure casing'
        origin=radial*(.65*1.15)+Vector((0,0,2.7))
        a=ray(vane,origin+tangent,-tangent);b=ray(vane,origin-tangent,tangent)
        assert a is not None and b is not None and .075<(a-b).length<.086,'Actual thick vane structure'
        for z in [.82,.90]:
            inside=ray(panel,(0,0,z),radial);skin=ray(body,(0,0,z),radial)
            outside=ray(panel,Vector((0,0,z))+radial*2,-radial)
            assert all(p is not None for p in [inside,skin,outside])
            assert inside.length<skin.length<outside.length,'Copper lower panel must sit on casing'
    collar=lookup['Mega upper silver nose collar'];nose=lookup['Mega ivory nose cone']
    a=ray(collar,(0,0,4.99),(1,0,0));b=ray(nose,(2,0,4.99),(-1,0,0))
    assert a is not None and b is not None and a.x<b.x,'Nose collar must be seated'
    bell=lookup['Mega hollow copper nozzle']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis capped'
    inside=ray(bell,(0,0,.18),(1,0,0));outside=ray(bell,(1,0,.18),(-1,0,0))
    assert inside is not None and outside is not None and .034<outside.x-inside.x<.047
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .57<min(hits)<.62,('Propulsion obstruction',min(hits))
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
    assert len(materials)==5
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
    report=dict(issue=966,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, positive volumes, matching evaluated geometry bounds/materials',
                'Three actual 0.0805-unit vanes and six casing root contacts','Three shaped lower panels seated on casing',
                'Silver nose collar seating','Measured nozzle wall and full open path to throat',
                'No external images or invented animation'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MEGA_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
