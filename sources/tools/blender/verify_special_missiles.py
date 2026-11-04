"""Verify authored PM11/PM12 interpretations without asserting unavailable visual fidelity."""
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
from verify_nuclear_missile import geometry_bounds

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/terran'


def structure(meshes,name):
    lookup={obj.name:obj for obj in meshes};bug=name=='bug-hunter'
    prefix='Bug Hunter blue stabilizer sector' if bug else 'Meat Eater blue open frame sector'
    sectors=sorted([obj for obj in meshes if obj.name==prefix or obj.name.startswith(prefix+'.')],key=lambda obj:obj.name)
    assert len(sectors)==4
    for i,sector in enumerate(sectors):
        angle=i*math.pi/2;radial=Vector((math.cos(angle),-math.sin(angle),0))
        z=2.0 if bug else 3.9
        inside=ray(sector,(0,0,z),radial);outside=ray(sector,Vector((0,0,z))+radial,-radial)
        expected=.07 if bug else .065
        assert inside is not None and outside is not None and expected-.008<(outside-inside).length<expected+.008
        other=lookup['Bug Hunter silver pressure shaft'] if bug else None
        contacts=[(1.44,other),(2.60,other)] if bug else [(3.28,lookup['Meat Eater blue lower frame ring']),(4.67,lookup['Meat Eater blue upper frame ring'])]
        for height,root in contacts:
            a=ray(sector,(0,0,height),radial);b=ray(sector,Vector((0,0,height))+radial,-radial)
            c=ray(root,(0,0,height),radial);d=ray(root,Vector((0,0,height))+radial,-radial)
            assert all(p is not None for p in [a,b,c,d]),(name,sector.name,height)
            def r(p): return (p.x*p.x+p.y*p.y)**.5
            if bug:
                assert r(a)<r(c)<r(b),'Blue root must cross the solid shaft skin'
            else:
                assert max(r(a),r(c))<min(r(b),r(d)),'Blue sector root must contact annular support'
    direction=Vector((math.sqrt(.5),math.sqrt(.5),0))
    mid=2.0 if bug else 3.9
    assert all(ray(obj,(0,0,mid),direction) is None for obj in sectors),'Frame window must be real negative space'
    bell=lookup['Bug Hunter hollow propulsion bell' if bug else 'Meat Eater hollow red nozzle']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis capped'
    z=.18 if bug else .2475
    a=ray(bell,(0,0,z),(1,0,0));b=ray(bell,(1,0,z),(-1,0,0))
    assert a is not None and b is not None and .024<b.x-a.x<.036
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert (.53<min(hits)<.58 if bug else .59<min(hits)<.63),('Unexpected nozzle obstruction',min(hits))
    assert ('Bug Hunter blunt gold tip' in lookup)==bug
    assert ('Meat Eater rounded gray head' in lookup)!=bug
    assert not any(obj.animation_data for obj in meshes)


def main():
    refs=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']
    hashes=[]
    for name in ['bug-hunter','meat-eater']:
        root=ROOT/name;meta=json.loads((root/'model.json').read_text())
        assert meta['id']=='openfa:missile/terran/'+name
        ref=next(r for r in refs if r['id']==meta['id'])
        assert ref['management_preview'] is None and meta['references']['management'] is None
        assert ref['surface']['source_sha256']==meta['references']['surface']
        for ext in ['blend','glb']:
            assert hashlib.sha256((root/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
        hashes.append(meta['blend_sha256'])
        bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(meshes);structure(meshes,name)
        assert len(meshes)==meta['mesh_objects']
        native=geometry_bounds(meshes);materials={slot.material.name for obj in meshes for slot in obj.material_slots}
        assert len(materials)==(7 if name=='bug-hunter' else 5)
        assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
        assert any(c.asset_data for c in bpy.data.collections)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(imported);structure(imported,name)
        assert len(imported)==len(meshes)
        assert max(abs(a-b) for a,b in zip(native,geometry_bounds(imported)))<.002
        assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
        report=dict(issue=968,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
            mesh_objects=len(meshes),material_count=len(materials),bounds=native,
            checks=['Native/GLB topology, positive volumes and matching evaluated geometry/materials',
                    'Exact catalogue IDs and runtime provenance; no invented management preview',
                    'Four measured thick blue sectors, eight support contacts and actual gaps',
                    'Open nozzle axis to recessed throat and measured wall','No external image dependencies or animation'],
            reference_limit='Low-resolution interpretation only; high-resolution original geometry unresolved',final_visual_acceptance=False)
        (root/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('SPECIAL_MISSILE_NATIVE_GLB_OK',name,len(meshes),len(materials),flush=True)
    assert hashes[0]!=hashes[1]


if __name__=='__main__': main()
