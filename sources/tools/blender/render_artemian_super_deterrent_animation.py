"""Render the actual AR18 GLB azimuth animation for both offline galleries."""
import argparse,json,math,shutil,subprocess,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips,sha

def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.denoising_use_gpu=False;s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=512;s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world=bpy.data.worlds.new('Review studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO'
    for loc,power,size in [((4,-6,8),950,5),((-4,-2,5),700,4),((2,5,7),1100,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
    return s

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--frames',type=Path,required=True);parser.add_argument('--ffmpeg',default=shutil.which('ffmpeg'));args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);assert args.ffmpeg
    folder=ROOT/'sources/objects/artemian/super-deterrent';media=ROOT/'gallery/media/objects/artemian/super-deterrent';media.mkdir(parents=True,exist_ok=True)
    renderer_hash=sha(Path(__file__));glb_hash=sha(folder/'model.glb');blend_hash=sha(folder/'model.blend')
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24;bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'),disable_bone_shape=True)
    scene=setup();scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=384;scene.render.film_transparent=False;scene.render.image_settings.color_mode='RGB'
    clip,=glb_clips(folder/'model.glb');assert clip['name']=='SuperDeterrentAzimuth';count=97;times=[clip['start']+clip['duration']*i/(count-1) for i in range(count)];poses=set();frames=args.frames.resolve();frames.mkdir(parents=True,exist_ok=True)
    assert not list(frames.glob('*.png')),'Do not overwrite prior animation frames'
    scene.camera.location=Vector((0,0,.95))+Vector((5,-12,6)).normalized()*15;scene.camera.rotation_euler=(Vector((0,0,.95))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.9
    for index,seconds in enumerate(times):
        frame=seconds*24;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update();obj=bpy.data.objects['SuperDeterrentYaw'];poses.add(tuple(round(v,5) for row in obj.matrix_world for v in row))
        scene.render.filepath=str(frames/f'{index:04}.png');bpy.ops.render.render(write_still=True)
    assert len(poses)>90,'Actual imported rigid head must rotate through the whole clip'
    output=media/'animation-00.webm';subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str((count-1)/clip['duration']),'-i',str(frames/'%04d.png'),'-frames:v',str(count),'-c:v','libvpx-vp9','-crf','28','-b:v','0','-deadline','good','-cpu-used','4','-threads','2','-pix_fmt','yuv420p','-an',str(output)],check=True)
    assert sha(Path(__file__))==renderer_hash and sha(folder/'model.glb')==glb_hash and sha(folder/'model.blend')==blend_hash,'Inputs changed while rendering'
    preview=dict(**clip,video=output.relative_to(ROOT).as_posix(),sha256=sha(output),frames=count,fps=(count-1)/clip['duration'],distinct_pose_count=len(poses))
    manifest=dict(id='openfa:building/legacy/124',stage='canonical-game-remaster',glb='sources/objects/artemian/super-deterrent/model.glb',glb_sha256=sha(folder/'model.glb'),blend_sha256=sha(folder/'model.blend'),renderer=Path(__file__).relative_to(ROOT).as_posix(),renderer_sha256=sha(Path(__file__)),blender=bpy.app.version_string,clips=[preview])
    (media/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print('AR18_ANIMATION_RENDERED',count,len(poses),flush=True)

if __name__=='__main__':main()
