"""Verify actual Scatter recess, casing relief and nozzle in native/GLB geometry."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes
from verify_cannon_equipment import ray

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/scatter'


def structure(meshes):
    lookup={obj.name:obj for obj in meshes}
    vanes=sorted([obj for obj in meshes if obj.name.startswith('Scatter thick swept gold vane')],key=lambda obj:obj.name)
    inserts=sorted([obj for obj in meshes if obj.name.startswith('Scatter vane thermal insert')],key=lambda obj:obj.name)
    assert len(vanes)==4 and len(inserts)==4
    shaft=lookup['Scatter silver pressure shaft']
    for i,(vane,insert) in enumerate(zip(vanes,inserts)):
        angle=math.pi/4+i*math.pi/2
        direction=Vector((math.cos(angle),math.sin(angle),0))
        for z in [.61,2.58]:
            inner=ray(vane,(0,0,z),direction)
            outer=ray(vane,Vector((0,0,z))+direction*2,-direction)
            skin=ray(shaft,(0,0,z),direction)
            assert inner is not None and outer is not None and skin is not None
            assert inner.length<skin.length<outer.length,'Vane root must intersect real shaft'
        inner=ray(vane,(0,0,1.5),direction)
        outer=ray(vane,Vector((0,0,1.5))+direction*2,-direction)
        assert inner is not None and outer is not None and .080<(outer-inner).length<.100,'Actual vane thickness'
        inset_back=ray(insert,(0,0,1.5),direction)
        inset_front=ray(insert,Vector((0,0,1.5))+direction*2,-direction)
        assert inset_back is not None and inset_front is not None
        assert inset_back.length<outer.length<inset_front.length,'Thermal insert must sit in vane'
    bell=lookup['Scatter hollow propulsion bell']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis is capped'
    inner=ray(bell,(0,0,.12),(1,0,0));outer=ray(bell,(1,0,.12),(-1,0,0))
    assert inner is not None and outer is not None and .025<outer.x-inner.x<.035
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .395<min(hits)<.43,('Unexpected nozzle obstruction',min(hits))
    for name in ['Scatter broad dark nose band','Scatter red tapered warhead','Scatter silver nose collar','Scatter rounded red nose tip']:
        assert name in lookup
    assert not any(obj.animation_data for obj in meshes)


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    for ext in ['blend','glb']:
        assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(meshes);structure(meshes)
    assert len(meshes)==meta['mesh_objects']
    native=bounds(meshes);materials={slot.material.name for obj in meshes for slot in obj.material_slots}
    assert len(materials)==6
    assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
    assert any(c.asset_data for c in bpy.data.collections)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(imported);structure(imported)
    assert len(imported)==len(meshes)
    assert max(abs(a-b) for a,b in zip(native,bounds(imported)))<.002
    assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
    report=dict(issue=962,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, matching bounds/materials, positive closed volumes',
                'Four actual thick gold vanes and seated thermal inserts','Eight real vane-root/shaft intersections',
                'Open axial nozzle to recessed throat and measured bell wall',
                'No external images or invented animation'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('SCATTER_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
