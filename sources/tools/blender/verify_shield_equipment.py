"""Validate native/imported shield walls, true openings, topology and material exports."""
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import bounds,check_meshes

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/hardpoints'


def radial_hit(obj,y,angle,outward):
    ray=Vector((math.cos(angle),0,math.sin(angle)))
    centre=Vector((0,y,0))
    origin=centre if outward else centre+ray*3
    direction=ray if outward else -ray
    inverse=obj.matrix_world.inverted()
    hit,point,_,_=obj.ray_cast(inverse @ origin,(inverse.to_3x3() @ direction).normalized())
    if not hit:
        return None
    point=obj.matrix_world @ point
    return math.hypot(point.x,point.z)


def check_shells(meshes,tier):
    prefixes={10:'Open swept shell petal',20:'Broad opposed shell lobe',30:'Windowed enclosure wall',
              40:'Windowed enclosure wall',50:'Unbroken enclosure wall'}
    obj=next(obj for obj in meshes if obj.name.startswith(prefixes[tier]))
    angle=math.radians(60 if tier in [10,20] else 180)
    y=-.70 if tier in [10,20] else -.65
    outer=radial_hit(obj,y,angle,False)
    inner=radial_hit(obj,y,angle,True)
    assert outer and inner and .06<outer-inner<.09,(tier,outer,inner)
    if tier in [30,40]:
        assert radial_hit(obj,-.65,math.radians(40),True) is None,'Side window is filled'
    if tier==50:
        assert radial_hit(obj,-.65,math.radians(50),True),'Closed variant must enclose the corresponding area'
    return outer-inner


def main():
    for tier in [10,20,30,40,50]:
        root=ROOT/f'shield-x{tier}'
        metadata=json.loads((root/'model.json').read_text())
        for extension in ['blend','glb']:
            assert hashlib.sha256((root/f'model.{extension}').read_bytes()).hexdigest()==metadata[extension+'_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(root/'model.blend'))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        assert len(meshes)==metadata['mesh_objects']
        check_meshes(meshes)
        wall=check_shells(meshes,tier)
        native_bounds=bounds(meshes)
        materials={slot.material.name for obj in meshes for slot in obj.material_slots}
        assert len(materials)==6
        assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
        assert any(collection.asset_data for collection in bpy.data.collections)
        assert not any(obj.animation_data for obj in meshes),'Do not invent articulation from inventory rotation'
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(root/'model.glb'))
        imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
        check_meshes(imported)
        assert len(imported)==len(meshes)
        imported_wall=check_shells(imported,tier)
        assert abs(wall-imported_wall)<.002
        assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
        assert max(abs(a-b) for a,b in zip(native_bounds,bounds(imported)))<.002
        report=dict(issue=956,blend_sha256=metadata['blend_sha256'],glb_sha256=metadata['glb_sha256'],
                    native_meshes=len(meshes),imported_meshes=len(imported),material_count=6,wall_thickness_measured=wall,
                    checks=['native and imported topology/positive volumes','true shell thickness','true window/closed-wall distinction',
                            'matching bounds and materials','no external images','no invented mechanical animation'],
                    final_visual_acceptance=False)
        (root/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('SHIELD_NATIVE_GLB_OK',tier,len(meshes),flush=True)


if __name__=='__main__':
    main()
