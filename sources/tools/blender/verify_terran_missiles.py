"""Verify missile source/export topology, recessed instrument channel and open nozzle."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes
from verify_cannon_equipment import ray

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran'


def structure(meshes,area):
    lookup={obj.name:obj for obj in meshes}
    nozzle=lookup['Hollow propulsion bell']
    assert ray(nozzle,(0,0,-1),(0,0,1)) is None,'Nozzle must have an open axis'
    assert ray(nozzle,(.365,0,-1),(0,0,1)) is not None,'Nozzle wall is missing'
    inner=ray(nozzle,(0,0,.20),(1,0,0))
    outer=ray(nozzle,(1,0,.20),(-1,0,0))
    assert inner is not None and outer is not None and .035<outer.x-inner.x<.055,'Nozzle wall thickness'
    axis_hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert min(axis_hits)>.56,('Aft cavity must reach the recessed throat',min(axis_hits))
    jacket=lookup['Red warhead jacket']
    point=ray(jacket,(0,-3,4.94),(0,1,0))
    assert point is not None and point.y>-.55,'Instrumentation channel must penetrate jacket'
    assert len([obj for obj in meshes if obj.name.startswith('Red tail stabilizer pod')])==4
    assert ('Area layered rounded nose' in lookup)==area
    assert ('Explosive long instrument insert' in lookup)!=area
    if area:
        nose=lookup['Area layered rounded nose']
        rims=sorted([obj for obj in meshes if obj.name.startswith('Area stepped nose retaining rim')],key=lambda obj:obj.name)
        for rim,z in zip(rims,[5.71,5.94,6.13]):
            inner=ray(rim,(0,0,z),(1,0,0))
            skin=ray(nose,(2,0,z),(-1,0,0))
            assert inner is not None and skin is not None and inner.x<skin.x,'Floating nose rim'
    assert len([obj for obj in meshes if obj.name.startswith('Area stepped nose retaining rim')])==(3 if area else 0)


def main():
    for name in ['explosive','area-explosive']:
        root=ROOT/name;meta=json.loads((root/'model.json').read_text())
        for ext in ['blend','glb']:
            assert hashlib.sha256((root/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(meshes);structure(meshes,name=='area-explosive')
        assert len(meshes)==meta['mesh_objects']
        native=bounds(meshes)
        materials={slot.material.name for obj in meshes for slot in obj.material_slots}
        assert len(materials)==5
        assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
        assert any(c.asset_data for c in bpy.data.collections)
        assert not any(obj.animation_data for obj in meshes)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(imported);structure(imported,name=='area-explosive')
        assert len(imported)==len(meshes)
        assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
        assert max(abs(a-b) for a,b in zip(native,bounds(imported)))<.002
        report=dict(issue=959,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
            mesh_objects=len(meshes),material_count=5,bounds=native,
            checks=['Native and imported topology, materials and bounds','Positive closed volumes',
                    'Open nozzle axis, 0.045-unit wall and recessed throat','Real jacket instrumentation recess',
                    'Distinct head structures','No external images or invented animation'],final_visual_acceptance=False)
        (root/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('TERRAN_MISSILE_NATIVE_GLB_OK',name,len(meshes),flush=True)


if __name__=='__main__': main()
