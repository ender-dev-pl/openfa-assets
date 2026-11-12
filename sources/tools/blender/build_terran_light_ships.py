"""Build and render independently authored Combat Eagle/Scoutship studies."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from catalogue_rendering import evaluated_points,fit_camera
from terran_light_ship_parts import palette,eagle,scout,orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/ships/terran'
BUILDERS={'combat-eagle':eagle,'scoutship':scout}
VIEWS=[('front-quarter',(8,-12,10)),('rear-quarter',(-8,12,10)),('top',(0,0,20)),
       ('side',(14,0,4)),('rear',(0,14,4)),('belly',(7,-10,-12))]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids',default=','.join(BUILDERS))
    parser.add_argument('--directions-only',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for name in args.ids.split(','):
        output=ROOT/name
        output.mkdir(parents=True,exist_ok=True)
        if args.directions_only:
            bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
            scene=bpy.context.scene
            meshes=[obj for obj in scene.objects if obj.type=='MESH']
        else:
            scene=setup_scene(768,48)
            bpy.context.preferences.filepaths.save_version=0
            scene.name='Terran '+name+' | independent study'
            collection=bpy.data.collections.new(name+' editable source')
            scene.collection.children.link(collection)
            bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
            BUILDERS[name](palette())
            collection.asset_mark()
            collection.asset_data.description='Independent reference-based study; hidden mechanics and sockets unresolved'
            meshes=[obj for obj in collection.objects if obj.type=='MESH']
            orient_and_chamfer(meshes)
        points=evaluated_points(meshes)
        if not args.directions_only:
            for view,direction in VIEWS:
                fit_camera(scene,points,direction)
                render_to(scene,output/(view+'.png'))
            fit_camera(scene,points,VIEWS[0][1])
            bpy.ops.object.select_all(action='DESELECT')
            for obj in meshes:
                obj.select_set(True)
            bpy.context.view_layer.objects.active=meshes[0]
            export_glb_to(output/'model.glb')
            save_blend_to(output/'model.blend')
            metadata=dict(id='openfa:'+name,issue=954,revision=5 if name=='combat-eagle' else 3,blender=bpy.app.version_string,
                blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
                generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('terran_light_ship_parts.py')),
                mesh_objects=len(meshes),mesh_faces=sum(len(obj.data.polygons) for obj in meshes),
                views=[view for view,_ in VIEWS],reference_video='PS01.VID' if name=='combat-eagle' else 'PS02.VID',
                reference_frames=[0,15,30,45,59],imported_geometry_or_textures=[],
                inferred=['Exact dimensions','Underside and internal mechanics','Panel segmentation and service fittings'],
                unresolved=['3D weapon socket transforms','Camera-matched final review','Gameplay scale/projection'],
                acceptance='study; final artistic and integration review open')
            (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n')
        else:
            (output/'directions').mkdir(exist_ok=True)
            span=max(max(p[a] for p in points)-min(p[a] for p in points) for a in range(3))
            for heading in range(32):
                angle=heading*math.tau/32
                fit_camera(scene,points,(math.sin(angle)*14,-math.cos(angle)*14,10))
                scene.camera.data.ortho_scale=span*1.5
                render_to(scene,output/'directions'/f'{heading:02}.png')
            (output/'directions.json').write_text(json.dumps(dict(count=32,blend_sha256=sha(output/'model.blend'),
                sampling='camera orbit; fixed scale; runtime heading calibration unresolved',ortho_scale=span*1.5),indent=2)+'\n')
        print('TERRAN_LIGHT_SHIP_OK',name,len(meshes),'directions' if args.directions_only else 'model',flush=True)


if __name__=='__main__':
    main()
