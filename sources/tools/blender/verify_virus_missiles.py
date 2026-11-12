"""Verify separate PM07/PM08 models, equipment contacts, scallops and nozzle paths."""
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


def structure(meshes,anti):
    lookup={obj.name:obj for obj in meshes}
    body=lookup['Anti Virus long-neck pressure casing' if anti else 'Virus two-row pressure casing']
    prefix='Anti Virus long violet side form' if anti else 'Virus bronze side form'
    forms=sorted([obj for obj in meshes if obj.name.startswith(prefix)],key=lambda obj:obj.name)
    assert len(forms)==(4 if anti else 8)
    other_prefix='Virus bronze side form' if anti else 'Anti Virus long violet side form'
    assert not any(obj.name.startswith(other_prefix) for obj in meshes)
    for i,obj in enumerate(forms):
        angle=-math.pi/2+(i%4)*math.pi/2;direction=Vector((math.cos(angle),math.sin(angle),0))
        centre=2.90 if anti else 2.25 if i<4 else 3.52
        for z in [centre,centre+.20]:
            inner=ray(obj,(0,0,z),direction);outer=ray(obj,Vector((0,0,z))+direction*2,-direction)
            skin=ray(body,(0,0,z),direction)
            assert all(p is not None for p in [inner,outer,skin])
            assert inner.length<skin.length<outer.length,'Side equipment must intersect actual casing'
    skirt=lookup['Virus family scalloped olive skirt']
    high=ray(skirt,(.52,0,0),(0,0,1));low=ray(skirt,(.52/math.sqrt(2),.52/math.sqrt(2),0),(0,0,1))
    assert high is not None and low is not None and high.z-low.z>.50,'Scalloped edge must be real geometry'
    inner=ray(skirt,(0,0,1.1),(1,0,0));outer=ray(skirt,(1,0,1.1),(-1,0,0))
    assert inner is not None and outer is not None and .060<outer.x-inner.x<.074
    nozzles=sorted([obj for obj in meshes if obj.name.startswith('Virus family hollow red nozzle')],key=lambda obj:obj.name)
    assert len(nozzles)==4
    centres=[(-.176,-.176),(.176,-.176),(-.176,.176),(.176,.176)]
    for obj,(x,y) in zip(nozzles,centres):
        assert ray(obj,(x,y,-1),(0,0,1)) is None,'Nozzle axis capped'
        inner=ray(obj,(x,y,.2),(1,0,0));outer=ray(obj,(x+1,y,.2),(-1,0,0))
        assert inner is not None and outer is not None and .022<outer.x-inner.x<.032
        hits=[p.z for mesh in meshes for p in [ray(mesh,(x,y,-1),(0,0,1))] if p is not None]
        assert .38<min(hits)<.42,('Propulsion obstruction',min(hits))
    assert ('Anti Virus pale nose collar' in lookup)==anti
    assert ('Virus yellow nose collar' in lookup)!=anti
    assert not any(obj.animation_data for obj in meshes)


def main():
    refs=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']
    pair=[next(r for r in refs if r['id']=='openfa:'+name) for name in ['virus','anti-virus']]
    assert pair[0]['surface']['decoded_shape_sha256']==pair[1]['surface']['decoded_shape_sha256']
    assert pair[0]['management_preview']['source_sha256']!=pair[1]['management_preview']['source_sha256']
    hashes=[];heights=[]
    for name in ['virus','anti-virus']:
        root=ROOT/name;meta=json.loads((root/'model.json').read_text());anti=name=='anti-virus'
        for ext in ['blend','glb']:
            assert hashlib.sha256((root/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
        hashes.append(meta['blend_sha256'])
        bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(meshes);structure(meshes,anti)
        assert len(meshes)==meta['mesh_objects']
        native=geometry_bounds(meshes);heights.append(native[5])
        materials={slot.material.name for obj in meshes for slot in obj.material_slots}
        assert len(materials)==(6 if anti else 7)
        assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
        assert any(c.asset_data for c in bpy.data.collections)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(imported);structure(imported,anti)
        assert len(imported)==len(meshes)
        assert max(abs(a-b) for a,b in zip(native,geometry_bounds(imported)))<.002
        assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
        report=dict(issue=965,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
            mesh_objects=len(meshes),material_count=len(materials),bounds=native,
            checks=['Native/GLB topology, positive volumes, matching evaluated geometry bounds/materials',
                    'Distinct management variants despite matching runtime sequence','Actual side-equipment/casing intersections',
                    'True skirt scallops and 0.066-unit walls','Four hollow nozzle axes to recessed throats and measured walls',
                    'No external images or invented animation'],final_visual_acceptance=False)
        (root/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('VIRUS_FAMILY_NATIVE_GLB_OK',name,len(meshes),len(materials),flush=True)
    assert hashes[0]!=hashes[1] and heights[0]-heights[1]>.5,'Preserve distinct antenna lengths'


if __name__=='__main__': main()
