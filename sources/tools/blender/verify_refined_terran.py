"""Check detailed variants, actual rig motion and independent animated GLB imports."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_refined_terran import ROOT, SOURCE, signature
from verify_directional_catalogue import geometry, difference
from catalogue_rendering import evaluated_points


def check_motion(scene, head, base, imported=False):
    if imported:
        start,end=head.animation_data.action.frame_range
    else:
        start,end=1,17
    def pose(progress):
        frame=start+(end-start)*progress
        scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))
    pose(0)
    fixed,moving=geometry(base.children),geometry(head.children)
    for index in range(16):
        pose(index/16)
        assert difference(fixed,geometry(base.children))<1e-6
    pose(.25)
    assert difference(moving,geometry(head.children))>.1
    pose(1)
    assert difference(moving,geometry(head.children))<1e-5
    pose(0)


def check_iris(scene,leaves,imported=False):
    if imported:
        start,end=leaves[0].animation_data.action.frame_range
    else:
        start,end=1,33
    def pose(progress):
        frame=start+(end-start)*progress
        scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))
    pose(0)
    closed=geometry(leaves)
    graph=bpy.context.evaluated_depsgraph_get()
    hit,_,_,_,obj,_=scene.ray_cast(graph,Vector((0.02,0.01,5)),Vector((0,0,-1)))
    assert hit and obj.name in {leaf.name for leaf in leaves},obj.name if obj else None
    pose(.5)
    assert difference(closed,geometry(leaves))>.2
    hit,location,_,_,obj,_=scene.ray_cast(graph,Vector((0.02,0.01,5)),Vector((0,0,-1)))
    assert hit and obj.name not in {leaf.name for leaf in leaves} and location.z<.2,(obj.name,location[:])
    pose(1)
    assert difference(closed,geometry(leaves))<1e-5
    pose(0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    ids=set(map(int,args.ids.split(','))) if args.ids else set(range(40))
    code_hash=signature()
    checked=[]
    for index in sorted(ids):
        output=ROOT/f'pb{index:02}'
        meta=json.loads((output/'model.json').read_text(encoding='utf-8'))
        assert meta['global_type']==index and meta['generator_sha256']==code_hash
        assert meta['source_blend_sha256']==hashlib.sha256((SOURCE/'terran'/f'pb{index:02}'/'model.blend').read_bytes()).hexdigest()
        assert meta['detail_objects']>=12 and meta['detail_features']
        assert meta['mesh_faces']>meta['source_faces']
        bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
        scene=bpy.context.scene
        meshes=[obj for obj in scene.objects if obj.type=='MESH']
        assert len(meshes)==meta['mesh_objects']
        assert not any(obj.name.startswith('Inset service window') for obj in meshes)
        assert all(obj.data.polygons and obj.data.materials for obj in meshes)
        assert not any(image.source=='FILE' for image in bpy.data.images)
        assert scene.render.resolution_x==scene.render.resolution_y==768
        assert scene.render.film_transparent and scene.camera.data.type=='ORTHO'
        assets=[collection for collection in bpy.data.collections if collection.asset_data]
        assert len(assets)==1 and assets[0]['building_id']==meta['building_id']
        assert list(assets[0]['footprint'])==meta['footprint']
        detailed=[obj for obj in meshes if 'detail_role' in obj]
        assert len(detailed)==meta['detail_objects']
        if index==5:
            refinement=meta['filter_direction_refinement']
            expected=hashlib.sha256((Path(__file__).parent/'refine_radiation_filter.py').read_bytes()).hexdigest()
            assert refinement['generator_sha256']==expected
            assert len(refinement['tubes'])==3
            axes=[Vector(direction) for direction in refinement['intake_directions']]
            assert all(axes[a].dot(axes[b])<-.1 for a,b in [(0,1),(1,2),(2,0)])
            for name,axis in zip(refinement['tubes'],axes):
                obj=bpy.data.objects[name]
                assert obj['filter_tube']
                points=[obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
                base=sum(points[:96],Vector())/96
                mouth=sum(points[-96:],Vector())/96
                lateral=Vector((mouth.x-base.x,mouth.y-base.y,0)).normalized()
                assert lateral.dot(axis)>.999
                outer=sum((point-mouth).length for point in points[-96:-48])/48
                inner=sum((point-mouth).length for point in points[-48:])/48
                assert .20<outer<.22 and .15<inner<.18 and outer-inner>.03
        if index==10:
            refinement=meta['screen_emitter_refinement']
            expected=hashlib.sha256((Path(__file__).parent/'refine_screen_generator.py').read_bytes()).hexdigest()
            assert refinement['generator_sha256']==expected
            assert len(refinement['crystals'])==3
            for name in refinement['crystals']:
                obj=bpy.data.objects[name]
                assert obj['field_emitter_crystal'] and not any(face.use_smooth for face in obj.data.polygons)
                assert len(obj.data.materials)==3
            for name,angle in zip(refinement['assemblies'],refinement['tilt_y_degrees']):
                root=bpy.data.objects[name]
                assert abs(math.degrees(root.rotation_euler.y)-angle)<.001
                assert any(obj.name in refinement['crystals'] for obj in root.children)
            assert refinement['tilt_y_degrees'][0]<-15 and refinement['tilt_y_degrees'][-1]>15
            assert any(surface.node_tree.nodes.get('Principled BSDF') and
                surface.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value>1
                for surface in bpy.data.materials if surface.use_nodes)
        if meta.get('rotation_rig'):
            rig=meta['rotation_rig']
            head,base=bpy.data.objects[rig['head']],bpy.data.objects[rig['base']]
            assert {obj.name for obj in head.children}==set(rig['moving_meshes'])
            assert {obj.name for obj in base.children}==set(rig['static_meshes'])
            for obj in detailed:
                assert obj.parent==(head if obj['detail_role']=='head' else base),obj.name
            check_motion(scene,head,base)
        if meta.get('iris_rig'):
            leaves=[bpy.data.objects[name] for name in meta['iris_rig']['leaves']]
            assert len(leaves)==meta['iris_rig']['leaf_count']==8
            check_iris(scene,leaves)
        points=evaluated_points(meshes)
        low=[min(p[axis] for p in points) for axis in range(3)]
        high=[max(p[axis] for p in points) for axis in range(3)]
        assert all(abs(low[axis]-meta['bounds_min'][axis])<.001 and abs(high[axis]-meta['bounds_max'][axis])<.001 for axis in range(3))
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
        assert len([obj for obj in bpy.context.scene.objects if obj.type=='MESH'])==len(meshes)
        assert not any(image.source=='FILE' for image in bpy.data.images)
        if index==10:
            for name in meta['screen_emitter_refinement']['assemblies']:
                assert bpy.data.objects[name].children
        if meta.get('rotation_rig'):
            head,base=bpy.data.objects['DirectionalHead'],bpy.data.objects['StaticBase']
            assert len(head.children)==len(meta['rotation_rig']['moving_meshes'])
            assert len(base.children)==len(meta['rotation_rig']['static_meshes'])
            check_motion(bpy.context.scene,head,base,True)
        if meta.get('iris_rig'):
            leaves=[bpy.data.objects[name] for name in meta['iris_rig']['leaves']]
            assert all(leaf.animation_data for leaf in leaves)
            check_iris(bpy.context.scene,leaves,True)
        checked.append(index)
        print('REFINED_TERRAN_VERIFIED',index,flush=True)
    assert set(checked)==ids
    print('REFINED_TERRAN_VERIFICATION_OK',len(checked),flush=True)


if __name__=='__main__':
    main()
