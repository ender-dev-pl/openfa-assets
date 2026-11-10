"""Render a real imported AC12 clip using a stable centered review camera."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from verify_achaean_building_centered import setup
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main(scratch,ffmpeg):
    assert scratch.is_absolute() and not scratch.exists(),'Use a fresh task-owned frame directory'
    folder=ROOT/'sources/objects/achaean/landing-pad';media=ROOT/'gallery/media/objects/achaean/landing-pad'
    meta=json.loads((folder/'model.json').read_bytes())
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30
    bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));s=setup();points=[]
    for frame in range(1,62):
        s.frame_set(frame);points.extend(o.matrix_world@Vector(v) for o in s.objects if o.type=='MESH' for v in o.bound_box)
    centre=Vector([(min(p[a] for p in points)+max(p[a] for p in points))/2 for a in range(3)])
    direction=Vector((5,-12,9)).normalized();s.camera.location=centre+direction*15;s.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    q=[s.camera.matrix_world.inverted()@p for p in points];s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2
    s.camera.location+=s.camera.matrix_world.to_3x3()@Vector(((min(p.x for p in q)+max(p.x for p in q))/2,(min(p.y for p in q)+max(p.y for p in q))/2,0))
    s.cycles.samples=12;s.render.resolution_x=s.render.resolution_y=384;s.render.film_transparent=False;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.018,.023,.029,1)
    scratch.mkdir(parents=True);poses=set();frames=48;fps=24
    for i in range(frames):
        frame=1+60*i/(frames-1);integer=int(frame);s.frame_set(integer,subframe=frame-integer)
        poses.add(tuple(round(v,6) for name in sorted(meta['animation']['retained_open_translations']) for row in bpy.data.objects[name].matrix_world for v in row))
        s.render.filepath=str(scratch/f'{i:04d}.png');bpy.ops.render.render(write_still=True)
    assert len(poses)>20
    video=media/'animation-00.webm'
    subprocess.run([str(ffmpeg),'-y','-loglevel','error','-framerate',str(fps),'-i',str(scratch/'%04d.png'),'-an','-c:v','libvpx-vp9','-crf','30','-b:v','0','-threads','2','-pix_fmt','yuv420p',str(video)],check=True)
    for ext,h in meta['binaries'].items():assert sha(folder/f'model.{ext}')==h
    clip,=glb_clips(folder/'model.glb');clip.update(video=video.relative_to(ROOT).as_posix(),sha256=sha(video),frames=frames,fps=fps,distinct_pose_count=len(poses))
    helper=Path(__file__).with_name('verify_achaean_building_centered.py')
    manifest=dict(id=meta['id'],stage='canonical-game-remaster',glb=(folder/'model.glb').relative_to(ROOT).as_posix(),glb_sha256=meta['binaries']['glb'],blend_sha256=meta['binaries']['blend'],renderer=Path(__file__).relative_to(ROOT).as_posix(),renderer_sha256=sha(Path(__file__)),renderer_helpers={helper.relative_to(ROOT).as_posix():sha(helper),'tools/gallery_animation_assets.py':sha(ROOT/'tools/gallery_animation_assets.py')},blender=bpy.app.version_string,clips=[clip])
    (media/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+chr(10),encoding='utf-8');print('AC12_ANIMATION_OK',frames,len(poses),video.stat().st_size,flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--scratch',type=Path,required=True);parser.add_argument('--ffmpeg',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.scratch,args.ffmpeg)
