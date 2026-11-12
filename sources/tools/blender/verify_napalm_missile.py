"""Reopen Napalm source and GLB; verify open structural spaces and shell depth."""
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

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/napalm'


def structure(meshes):
    lookup={obj.name:obj for obj in meshes}
    assert len([obj for obj in meshes if obj.name.startswith('Napalm tapered red reservoir')])==3
    shrouds=[obj for obj in meshes if obj.name.startswith('Napalm thick angular shroud')]
    assert len(shrouds)==3
    assert all(not obj.animation_data for obj in meshes)
    # The neck is not filled by a hidden solid cone beneath the raised head.
    for x in [-.60,.60]:
        assert not any(ray(obj,(x,-3,3.91),(0,1,0)) is not None for obj in meshes),'Neck side gap filled'
    mount=lookup['Napalm annular reservoir support']
    assert ray(mount,(0,0,0),(0,0,1)) is None,'Mount must preserve nozzle axis'
    for angle in [-math.pi/6,math.pi/2,7*math.pi/6]:
        p=ray(mount,(.44*math.cos(angle),-.44*math.sin(angle),0),(0,0,1))
        assert p is not None and .85<p.z<.88,'Reservoir mounting ring missing'
    bell=lookup['Napalm hollow nozzle']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis is capped'
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .65<min(hits)<.71,('Unexpected nozzle obstruction',min(hits))
    for obj,angle in zip(sorted(shrouds,key=lambda obj:obj.name),[-math.pi/2,math.pi/6,5*math.pi/6]):
        direction=Vector((math.cos(angle),-math.sin(angle),0))
        inner=ray(obj,(0,0,2),direction)
        outer=ray(obj,Vector((0,0,2))+direction*2,-direction)
        assert inner is not None and outer is not None
        assert .075<(outer-inner).length<.095,'Shroud must have real 0.085-unit walls'
    assert 'Napalm pear pressure head' in lookup and 'Napalm forward amber feed bottle' in lookup


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    for ext in ['blend','glb']:
        assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    assert len(meshes)==meta['mesh_objects']
    check_meshes(meshes);structure(meshes)
    native=bounds(meshes);materials={slot.material.name for obj in meshes for slot in obj.material_slots}
    assert len(materials)==8
    assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
    assert any(c.asset_data for c in bpy.data.collections)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(imported);structure(imported)
    assert len(imported)==len(meshes)
    assert max(abs(a-b) for a,b in zip(native,bounds(imported)))<.002
    assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
    report=dict(issue=960,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native and GLB topology, bounds, intentional materials, positive closed volumes',
                'No file-image dependencies or invented animation','Two clear side-neck rays',
                'Three actual 0.085-unit shroud walls','Open axial nozzle to recessed throat',
                'Three declared reservoirs and distinct separated head'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('NAPALM_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
