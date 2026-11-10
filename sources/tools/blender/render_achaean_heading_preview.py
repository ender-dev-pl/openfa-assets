"""Render one imported AC20 directional clip without modifying either canonical binary."""
import bpy,sys,json,math,subprocess
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from verify_achaean_building_left_quarter import setup
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips,sha

def main():
    folder=ROOT/'sources/objects/achaean/defence-battery';media=ROOT/'gallery/media/objects/achaean/defence-battery';before={ext:sha(folder/f'model.{ext}') for ext in ['blend','glb']};clip,=glb_clips(folder/'model.glb')
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];times=[clip['start']+clip['duration']*i/23 for i in range(24)];points=[];poses=set()
    def frame(t):f=t*30;bpy.context.scene.frame_set(math.floor(f),subframe=f%1);bpy.context.view_layer.update()
    for t in times:
        frame(t);poses.add(tuple(round(v,5) for o in meshes for row in o.matrix_world for v in row));points.extend(o.matrix_world@Vector(c) for o in meshes for c in o.bound_box)
    assert len(poses)>20;s=setup();s.cycles.samples=8;s.render.resolution_x=s.render.resolution_y=384;centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]);v=Vector((-5,-12,7)).normalized();s.camera.location=centre+v*15;s.camera.rotation_euler=(-v).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();q=[s.camera.matrix_world.inverted()@p for p in points];s.camera.data.ortho_scale=max(max(p.x for p in q)-min(p.x for p in q),max(p.y for p in q)-min(p.y for p in q))*1.2
    scratch=ROOT/'artifacts/achaean-defence-heading-preview';scratch.mkdir(parents=True,exist_ok=True);assert not list(scratch.glob('*.png')),'Preserve existing frames for review';frame_hashes={}
    for i,t in enumerate(times):
        frame(t);p=scratch/f'{i:03}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True);frame_hashes[p.name]=sha(p)
    video=media/'animation-00.webm';ffmpeg=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'ffmpeg';subprocess.run([ffmpeg,'-y','-loglevel','error','-framerate','24','-i',str(scratch/'%03d.png'),'-c:v','libvpx-vp9','-crf','34','-b:v','0','-pix_fmt','yuv420p',str(video)],check=True)
    preview={**clip,'video':video.relative_to(ROOT).as_posix(),'sha256':sha(video),'frames':24,'fps':24,'distinct_pose_count':len(poses)};helper=Path(__file__).with_name('verify_achaean_building_left_quarter.py');manifest=dict(blend_sha256=before['blend'],glb_sha256=before['glb'],renderer=Path(__file__).relative_to(ROOT).as_posix(),renderer_sha256=sha(Path(__file__)),renderer_helpers={helper.relative_to(ROOT).as_posix():sha(helper)},clips=[preview],actual_imported_frame_sha256=frame_hashes,scope='Actual imported heading demonstration; original firing/idle timing not recovered.')
    (media/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');assert before=={ext:sha(folder/f'model.{ext}') for ext in ['blend','glb']}
    for name,h in frame_hashes.items():
        p=(scratch/name).resolve();assert p.parent==scratch.resolve() and sha(p)==h;p.unlink()
    scratch.rmdir();print('AC20_PREVIEW_OK',len(poses),flush=True)
if __name__=='__main__':main()
