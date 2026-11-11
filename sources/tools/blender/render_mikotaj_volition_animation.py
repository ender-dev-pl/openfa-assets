"""Render the actual MK11 GLB skin animation for both offline galleries."""
import argparse,importlib.util,json,math,shutil,subprocess,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips,sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--frames',type=Path,required=True);parser.add_argument('--ffmpeg',default=shutil.which('ffmpeg'));args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);assert args.ffmpeg
    folder=ROOT/'sources/objects/mikotaj/volition';media=ROOT/'gallery/media/objects/mikotaj/volition';media.mkdir(parents=True,exist_ok=True)
    verifier=Path(__file__).with_name('verify_mikotaj_volition.py');spec=importlib.util.spec_from_file_location('volition_review',verifier);review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24;bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'),disable_bone_shape=True)
    scene=review.setup();scene.cycles.samples=12;scene.render.resolution_x=scene.render.resolution_y=384;scene.render.film_transparent=False;scene.render.image_settings.color_mode='RGB'
    clip,=glb_clips(folder/'model.glb');assert clip['name']=='LaunchFacilityCycle';count=61;times=[clip['start']+clip['duration']*i/(count-1) for i in range(count)];poses=set();frames=args.frames.resolve();frames.mkdir(parents=True,exist_ok=True)
    assert not list(frames.glob('*.png')),'Do not overwrite prior animation frames'
    scene.camera.location=Vector((0,0,1.18))+Vector((5,-12,6)).normalized()*15;scene.camera.rotation_euler=(Vector((0,0,1.18))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=3.25
    for index,seconds in enumerate(times):
        frame=seconds*24;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));deps=bpy.context.evaluated_depsgraph_get();obj=bpy.data.objects['Volition single skinned spiral ribbon'];evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();poses.add(tuple(round(v,5) for vertex in mesh.vertices for v in (evaluated.matrix_world@vertex.co)));evaluated.to_mesh_clear()
        scene.render.filepath=str(frames/f'{index:04}.png');bpy.ops.render.render(write_still=True)
    assert len(poses)>20,'Skin must actually deform; object matrices alone do not prove skin motion'
    output=media/'animation-00.webm';subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str((count-1)/clip['duration']),'-i',str(frames/'%04d.png'),'-frames:v',str(count),'-c:v','libvpx-vp9','-crf','28','-b:v','0','-deadline','good','-cpu-used','4','-threads','2','-pix_fmt','yuv420p','-an',str(output)],check=True)
    preview=dict(**clip,video=output.relative_to(ROOT).as_posix(),sha256=sha(output),frames=count,fps=(count-1)/clip['duration'],distinct_pose_count=len(poses))
    manifest=dict(id='openfa:building/legacy/096',stage='canonical-game-remaster',glb='sources/objects/mikotaj/volition/model.glb',glb_sha256=sha(folder/'model.glb'),blend_sha256=sha(folder/'model.blend'),renderer=Path(__file__).relative_to(ROOT).as_posix(),renderer_sha256=sha(Path(__file__)),verifier_sha256=sha(verifier),blender=bpy.app.version_string,clips=[preview])
    (media/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print('MK11_ANIMATION_RENDERED',count,len(poses),flush=True)

if __name__=='__main__':main()
