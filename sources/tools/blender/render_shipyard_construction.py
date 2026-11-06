"""Render a multi-asset construction demonstration from independent canonical GLBs.

No combined distributable model is created. This offline fixture demonstrates
the binding contract; production progress remains a simulation responsibility.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import bpy
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,str(ROOT/'tools'))
from build_ship_construction_layers import sha,SHIPS
from build_shipyard_hangar import OUT,MEDIA,HALF,END
import render_gallery_animations as stock
from gallery_animation_assets import glb_clips
from publication_support import clean_png


def combined_scene(ship='assault-fighter'):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'model.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.type in ['MESH','EMPTY']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUT/'model.glb'))
    old=set(scene.objects)
    folder=ROOT/'sources/objects/terran'/ship/'construction'
    bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
    new=[o for o in scene.objects if o not in old]
    root=next(o for o in new if o.name=='ShipAssembly')
    config=json.loads((OUT/'model.json').read_text())['ships'][ship]
    root.parent=bpy.data.objects['ShipConstructionPlacement'];root.matrix_parent_inverse=Matrix.Identity(4);root.matrix_basis=Matrix(config['matrix'])
    # Neutral preview terrain hides exterior underground walls, leaving the actual hole.
    h=(HALF+.13)*.3;outer=3.8;vertices=[(x,y,-.002) for x,y in [(-outer,-outer),(outer,-outer),(outer,outer),(-outer,outer),(-h,-h),(h,-h),(h,h),(-h,h)]]
    mesh=bpy.data.meshes.new('Preview terrain aperture');mesh.from_pydata(vertices,[],[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
    ground=bpy.data.objects.new('Preview terrain (not an asset)',mesh);scene.collection.objects.link(ground)
    mat=bpy.data.materials.new('Preview neutral terrain');mat.diffuse_color=(.055,.065,.075,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.055,.065,.075,1);bs.inputs['Roughness'].default_value=.92;mesh.materials.append(mat)
    scene.camera.location=(3.5,-5.5,4.6);scene.camera.rotation_euler=(Vector((0,0,.36))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=3.9
    scene.render.film_transparent=False;scene.render.resolution_x=scene.render.resolution_y=768;scene.cycles.samples=24
    return scene,new,config


def set_phase(scene,objects,frame):
    scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))
    stage=min(3,int(frame>=30)+int(frame>=66)+int(frame>=99))
    for obj in objects:
        if obj.type!='MESH':continue
        node=obj.parent
        while node and node.name not in ['Hull','Build01_Frame','Build02_Systems','Build03_InnerPanels']:node=node.parent
        assert node,obj.name
        index=['Build01_Frame','Build02_Systems','Build03_InnerPanels','Hull'].index(node.name)
        obj.hide_render=index>stage
    bpy.context.view_layer.update()


def render_stills():
    images={}
    for ship in SHIPS:
        scene,objects,config=combined_scene(ship)
        # Other ships use the documented local hoist height correction.
        # The complete animated demonstration is Assault Fighter-calibrated.
        frames=[('build-frame',15),('build-systems',45),('build-panels',80),('complete',115)]
        if ship=='assault-fighter':frames += [('lifted',190),('hatch-open-loaded',240),('lowering',285),('received',335),('ready',480)]
        for name,frame in frames:
            set_phase(scene,objects,frame);path=MEDIA/(ship+'-'+name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            path.write_bytes(clean_png(path.read_bytes()));images[path.name]=sha(path)
    return images


def render_showcase():
    scene,objects,config=combined_scene();scene.render.resolution_x=scene.render.resolution_y=512;scene.cycles.samples=12
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    folder=ROOT/'artifacts/issue-227/transfer-frames';folder.mkdir(parents=True,exist_ok=True)
    count=192;poses=set()
    for i in range(count):
        frame=1+(END-1)*i/(count-1);set_phase(scene,objects,frame)
        poses.add(tuple(round(v,5) for o in [bpy.data.objects['ShipConstructionPlacement'],bpy.data.objects['LoadAttachment'],bpy.data.objects['HangarDoor_Left']] for row in o.matrix_world for v in row))
        scene.render.filepath=str(folder/f'{i:04}.png');bpy.ops.render.render(write_still=True)
    duration=(END-1)/30;video=MEDIA/'construction-transfer.webm'
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-framerate',str(count/duration),'-i',str(folder/'%04d.png'),'-frames:v',str(count),'-c:v','libvpx-vp9','-crf','27','-b:v','0','-deadline','good','-cpu-used','4','-threads','2','-pix_fmt','yuv420p','-an',str(video)],check=True)
    return dict(name='Layered construction and crane transfer (Assault Fighter)',video=video.relative_to(ROOT).as_posix(),sha256=sha(video),frames=count,duration=duration,distinct_pose_count=len(poses))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stills-only',action='store_true');parser.add_argument('--video-only',action='store_true');parser.add_argument('--yard-preview-only',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.yard_preview_only:
        study=dict(stage='layered-construction-hangar',blend=(OUT/'model.blend').relative_to(ROOT).as_posix(),glb=(OUT/'model.glb').relative_to(ROOT).as_posix(),image=(MEDIA/'front-quarter.png').relative_to(ROOT).as_posix())
        clips=[stock.render_clip(dict(id='terran:ship-yard'),study,c,shutil.which('ffmpeg')) for c in glb_clips(OUT/'model.glb')]
        manifest=dict(id='terran:ship-yard',stage=study['stage'],glb=study['glb'],glb_sha256=sha(OUT/'model.glb'),blend_sha256=sha(OUT/'model.blend'),renderer_sha256=sha(Path(stock.__file__)),blender=bpy.app.version_string,clips=clips)
        (MEDIA/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');return
    if not args.video_only:
        images=render_stills();(OUT/'showcase-stills.json').write_text(json.dumps(dict(renderer_sha256=sha(Path(__file__)),images=images),indent=2)+'\n',encoding='utf-8')
    if args.stills_only:return
    clip=render_showcase()
    files=[Path(__file__),OUT/'model.blend',OUT/'model.glb',OUT/'model.json']
    for ship in SHIPS:
        files.extend(ROOT/'sources/objects/terran'/ship/'construction'/name for name in ['model.glb','model.json'])
    data=dict(issue=227,inputs={p.relative_to(ROOT).as_posix():sha(p) for p in files},clips=[clip],scope='Offline demonstration using actual canonical imported meshes and authored attachment/visibility contract. Build timing is a preview fixture, not game simulation. Neutral preview terrain masks the underground exterior.')
    (OUT/'showcase.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('CONSTRUCTION_SHOWCASE_RENDERED',clip['frames'],clip['distinct_pose_count'],flush=True)


if __name__=='__main__':main()
