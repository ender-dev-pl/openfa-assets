"""Build higher-detail Terran variants while preserving the previous catalogue for comparison."""
import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from catalogue_rendering import evaluated_points, fit_camera
from refined_terran_parts import Detailer, reduce_toy_materials
from refine_terran_models import refine_building


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO/'docs/assets/bootstrap-3d/full-catalogue'
ROOT = REPO/'docs/assets/bootstrap-3d/terran-refined'


def signature():
    names = ['build_refined_terran.py','refined_terran_parts.py','refine_terran_models.py','refine_terran_special.py','refined_silo_iris.py']
    return hashlib.sha256(b''.join((Path(__file__).parent/name).read_bytes() for name in names)).hexdigest()


def stage_path(extension):
    stage=REPO/'artifacts/refined-terran/render-stage'
    stage.mkdir(parents=True,exist_ok=True)
    return stage/(uuid.uuid4().hex+extension)


def publish(temporary,target):
    for attempt in range(10):
        try:
            os.replace(temporary,target)
            return
        except OSError:
            if attempt==9:
                raise
            time.sleep(.2)


def render_to(scene, target):
    # Windows readers can briefly lock displayed assets. Write fresh staging
    # files and atomically publish, rather than truncate the displayed file.
    bpy.ops.render.render(write_still=False)
    temporary=stage_path('.png')
    bpy.data.images['Render Result'].save_render(str(temporary),scene=scene)
    publish(temporary,target)


def export_glb_to(target,animated=False):
    temporary=stage_path('.glb')
    bpy.ops.export_scene.gltf(filepath=str(temporary),export_format='GLB',
        use_selection=True,export_apply=True,export_animations=animated,
        export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True)
    publish(temporary,target)


def save_blend_to(target):
    temporary=stage_path('.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
    publish(temporary,target)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids',help='Optional PB global types, default all 40 Terran buildings')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    records=json.loads((SOURCE/'recipes.json').read_text(encoding='utf-8'))['buildings'][:40]
    requested=set(map(int,args.ids.split(','))) if args.ids else set(range(40))
    assert requested <= set(range(40))
    code_hash=signature()
    for record in records:
        index=record['global_type']
        if index not in requested:
            continue
        source=SOURCE/'terran'/record['preview'].lower()
        output=ROOT/record['preview'].lower()
        output.mkdir(parents=True,exist_ok=True)
        source_hash=hashlib.sha256((source/'model.blend').read_bytes()).hexdigest()
        if args.resume and (output/'model.json').exists():
            previous=json.loads((output/'model.json').read_text())
            if previous.get('generator_sha256')==code_hash and previous.get('source_blend_sha256')==source_hash:
                expected=['model.blend','model.glb','front-quarter.png','rear-quarter.png','top.png']
                if previous.get('rotation_rig'):
                    expected += [f'directions/{i:02}.png' for i in range(16)]
                if previous.get('iris_rig'):
                    expected += [f'iris/{i:02}.png' for i in range(17)]
                if all((output/name).is_file() for name in expected):
                    print('REFINED_CACHED',record['preview'],flush=True)
                    continue
        bpy.ops.wm.open_mainfile(filepath=str(source/'model.blend'))
        scene=bpy.context.scene
        scene.frame_set(1)
        scene.render.resolution_x=scene.render.resolution_y=768
        scene.render.resolution_percentage=100
        scene.cycles.samples=48
        bpy.context.preferences.filepaths.save_version=0
        collection=next(collection for collection in bpy.data.collections if collection.asset_data)
        bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
        old_meshes=[obj for obj in collection.objects if obj.type=='MESH']
        old_faces=sum(len(obj.data.polygons) for obj in old_meshes)
        source_count=len(old_meshes)
        proxy_windows=[obj for obj in old_meshes if obj.name.startswith('Inset service window')]
        for obj in proxy_windows:
            bpy.data.objects.remove(obj,do_unlink=True)
        reduce_toy_materials()
        details=Detailer(collection)
        refine_building(index,details,record)
        assert len(details.created)>=12,record['preview']
        meshes=[obj for obj in collection.objects if obj.type=='MESH']
        # Replacing many proxy window cubes need not increase object count.
        # Actual geometry growth and named functional details are the quality contract.
        assert sum(len(obj.data.polygons) for obj in meshes)>old_faces
        head=bpy.data.objects.get('DirectionalHead')
        base=bpy.data.objects.get('StaticBase')
        iris=list(collection.get('iris_leaves',[]))
        points=[]
        for frame in (range(1,18) if iris else range(1,17) if head else [1]):
            scene.frame_set(frame)
            points.extend(evaluated_points(meshes))
        scene.frame_set(1)
        views=[('front-quarter',(8,-12,10.1)),('rear-quarter',(-8,12,10.1)),('top',(0,0,20))]
        for view,direction in views:
            fit_camera(scene,points,direction)
            scene.render.filepath=str(output/(view+'.png'))
            render_to(scene,output/(view+'.png'))
        fit_camera(scene,points,views[0][1])
        if head:
            (output/'directions').mkdir(exist_ok=True)
            for index_heading in range(16):
                scene.frame_set(index_heading+1)
                scene.render.filepath=str(output/'directions'/f'{index_heading:02}.png')
                render_to(scene,output/'directions'/f'{index_heading:02}.png')
        if iris:
            (output/'iris').mkdir(exist_ok=True)
            for iris_frame in range(17):
                scene.frame_set(iris_frame+1)
                render_to(scene,output/'iris'/f'{iris_frame:02}.png')
        scene.frame_set(1)
        neutral=evaluated_points(meshes)
        low=[min(p[axis] for p in neutral) for axis in range(3)]
        high=[max(p[axis] for p in neutral) for axis in range(3)]
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collection.objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active=head or meshes[0]
        export_glb_to(output/'model.glb',bool(head or iris))
        collection.asset_data.description=record['building_id']+'; refined independent mechanical study'
        collection['detail_features']='; '.join(details.features)
        scene.render.filepath=str(output/'front-quarter.png')
        save_blend_to(output/'model.blend')
        metadata={key:record[key] for key in ['global_type','building_id','name','culture','preview','footprint']}
        metadata.update(generator_sha256=code_hash,source_blend_sha256=source_hash,
            source_meshes=source_count,mesh_objects=len(meshes),source_faces=old_faces,
            removed_proxy_windows=len(proxy_windows),
            mesh_faces=sum(len(obj.data.polygons) for obj in meshes),detail_objects=len(details.created),
            detail_features=details.features,bounds_min=low,bounds_max=high,resolution=768,samples=48,
            views=[view for view,_ in views],imported_geometry_or_textures=[],
            source='independently authored catalogue geometry',blender=bpy.app.version_string)
        if head:
            metadata['rotation_rig']=dict(head=head.name,base=base.name,pivot=list(head.location),
                moving_meshes=sorted(obj.name for obj in head.children),static_meshes=sorted(obj.name for obj in base.children),
                direction_count=16,axis='+Z',zero_forward='-Y',positive='counterclockwise')
        if iris:
            metadata['iris_rig']=dict(leaves=iris,leaf_count=len(iris),closed_frame=1,open_frame=17,
                loop_end_frame=33,preview_frames=17,mechanism='rim-pivoted overlapping curved leaves with vertical retraction',
                reference='PB14 surface overlay frames 2..14; leaf count and hidden mechanism authored')
        (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
        print('REFINED_TERRAN_OK',record['preview'],len(meshes),'meshes',len(details.created),'detail objects',flush=True)
    print('REFINED_GENERATION_OK',len(requested),flush=True)


if __name__=='__main__':
    main()
