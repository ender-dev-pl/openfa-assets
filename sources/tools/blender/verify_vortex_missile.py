"""Verify actual Vortex recess, casing relief and nozzle in native/GLB geometry."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes
from verify_cannon_equipment import ray

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/missiles/terran/vortex'


def structure(meshes):
    lookup={obj.name:obj for obj in meshes}
    upper=lookup['Vortex thick wavy upper casing'];lower=lookup['Vortex thick wavy lower casing']
    positive=ray(upper,(.62,0,3),(0,0,1));negative=ray(upper,(-.62,0,3),(0,0,1))
    assert positive is not None and negative is not None
    assert negative.z-positive.z>.95,'Upper casing must have a real sloping cut edge'
    for obj,z in [(upper,5.3),(lower,1.2)]:
        inner=ray(obj,(0,0,z),(1,0,0));outer=ray(obj,(2,0,z),(-1,0,0))
        assert inner is not None and outer is not None and .050<outer.x-inner.x<.070,'Actual casing wall thickness'
    shaft=lookup['Vortex silver pressure shaft']
    for name,z,cover in [('Vortex upper annular casing support',5.08,upper),('Vortex annular engine mount',.98,lower)]:
        support=lookup[name]
        inside=ray(support,(0,0,z),(1,0,0));outside=ray(support,(2,0,z),(-1,0,0))
        skin=ray(shaft,(0,0,z),(1,0,0));shell_inside=ray(cover,(0,0,z),(1,0,0))
        assert all(p is not None for p in [inside,outside,skin,shell_inside])
        assert inside.x<skin.x<outside.x and shell_inside.x<outside.x,'Casing support must intersect shaft and casing'
    direction=(math.cos(-1.9),math.sin(-1.9),0)
    def radius(point): return (point.x*point.x+point.y*point.y)**.5
    frame=lookup['Vortex curved red service surround'];inset=lookup['Vortex dark service inset']
    a=ray(frame,(0,0,3),direction);b=ray(inset,(0,0,3),direction)
    skin=ray(shaft,(0,0,3),direction)
    assert a is not None and b is not None and skin is not None
    assert radius(a)<radius(skin) and .61<radius(b)<.63,'Service frame/inset must be seated'
    assert len([obj for obj in meshes if obj.name.startswith('Vortex oval head side form')])==2
    flange=lookup['Vortex annular nozzle flange']
    assert ray(flange,(0,0,0),(0,0,1)) is None,'Flange must preserve propulsion axis'
    bell=lookup['Vortex hollow gold propulsion bell']
    assert ray(bell,(0,0,-1),(0,0,1)) is None,'Nozzle axis is capped'
    inner=ray(bell,(0,0,.22),(1,0,0));outer=ray(bell,(1,0,.22),(-1,0,0))
    assert inner is not None and outer is not None and .03<outer.x-inner.x<.05
    hits=[p.z for obj in meshes for p in [ray(obj,(0,0,-1),(0,0,1))] if p is not None]
    assert .83<min(hits)<.88,('Unexpected propulsion obstruction',min(hits))
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
    report=dict(issue=963,blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, positive closed volumes and matching materials/bounds',
                'Actual wavy upper edge and two 0.06-unit casing walls','Casing support/shaft intersections',
                'Curved service panel seating','Open gold nozzle and measured wall',
                'No external images or invented articulation'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('VORTEX_NATIVE_GLB_OK',len(meshes),len(materials),flush=True)


if __name__=='__main__': main()
