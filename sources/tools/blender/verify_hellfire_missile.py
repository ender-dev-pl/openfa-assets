"""Verify actual Hellfire recess, casing relief and nozzle in native/GLB geometry."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes
from verify_cannon_equipment import ray

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/hellfire'


def structure(meshes):
    lookup={obj.name:obj for obj in meshes}
    casing=lookup['Hellfire fusiform pressure casing']
    for x,z in [(-.28*1.14,3.60),(-.15*1.14,4.04)]:
        point=ray(casing,(x,-3,z),(0,1,0))
        assert point is not None and point.y>-.60,'Keyhole recess is filled'
    point=ray(casing,(-.15*1.14,-3,3.55),(0,1,0))
    assert point is not None and point.y<-.70,'Lower port must be narrower than upper bulb'
    form=lookup['Hellfire large oval side form']
    body_point=ray(casing,(0,-3,2.25),(0,1,0))
    relief_point=ray(form,(0,-3,2.25),(0,1,0))
    assert body_point is not None and relief_point is not None
    assert .18<body_point.y-relief_point.y<.27,'Oval form must have substantial casing relief'
    joint=lookup['Hellfire nose pressure joint']
    nose=lookup['Hellfire long tapered nose']
    rim=ray(joint,(0,0,4.43),(1,0,0))
    skin=ray(nose,(2,0,4.43),(-1,0,0))
    assert rim is not None and skin is not None and rim.x<skin.x,'Nose joint must sit in casing'
    patch=lookup['Hellfire nose red identification patch']
    offsets=[]
    for vertex in patch.data.vertices:
        p=patch.matrix_world @ vertex.co
        skin=ray(nose,(0,0,p.z),(p.x,p.y,0))
        assert skin is not None,'Nose marking outside casing'
        offsets.append((p.x*p.x+p.y*p.y)**.5-(skin.x*skin.x+skin.y*skin.y)**.5)
    assert -.008<min(offsets)<-.004 and 0<max(offsets)<.006,'Marking must conform to nose skin'
    bell=lookup['Hellfire hollow nozzle']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis is capped'
    inner=ray(bell,(0,0,.14),(1,0,0));outer=ray(bell,(1,0,.14),(-1,0,0))
    assert inner is not None and outer is not None and .030<outer.x-inner.x<.038,'Actual bell wall thickness'
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .59<min(hits)<.64,('Nozzle obstruction',min(hits))
    assert 'Hellfire small red tip' in lookup and 'Hellfire nose red identification patch' in lookup
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
    report=dict(issue=961,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, matching bounds/materials, positive closed volumes',
                'Actual keyhole recess depth and wider upper bulb','Substantial oval casing relief',
                'Open axial nozzle to recessed throat and measured bell wall',
                'No external images or invented animation'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('HELLFIRE_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
