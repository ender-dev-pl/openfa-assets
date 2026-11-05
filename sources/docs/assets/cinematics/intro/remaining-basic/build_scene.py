"""Build one basic scene in an isolated output directory, with editable native and static GLB."""
import bpy,sys,argparse,json
from pathlib import Path
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root));import blockout_tools as T
from scene_models import BUILDERS
ap=argparse.ArgumentParser();ap.add_argument('--scene',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);plan=json.loads((root/'shot-plan.json').read_text());info=next(x for x in plan['scenes'] if x['id']==args.scene);out=args.out;out.mkdir(parents=True,exist_ok=True);s=T.begin(info);BUILDERS[info['milestone']](info);T.apply_black_samples(info);mid=(s.frame_start+s.frame_end)//2;s.frame_set(mid);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(out/(args.scene+'.blend')),compress=False)
# Save editable text/curves natively; convert only the transient export copy.
for obj in list(s.objects):
 if obj.type in ['FONT','CURVE']:
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(out/(args.scene+'.glb')),export_format='GLB',export_animations=False,export_current_frame=True,export_cameras=True,export_lights=False,export_apply=True)
# Reopen the native project, and render representative motion/framing samples.
bpy.ops.wm.open_mainfile(filepath=str(out/(args.scene+'.blend')));s=bpy.context.scene;s.cycles.samples=4;frames=[s.frame_start+2,mid,max(s.frame_start+2,s.frame_end-4)]
for i,f in enumerate(frames):s.frame_set(f);s.render.filepath=str(out/f'preview-{i}.png');bpy.ops.render.render(write_still=True)
(out/'build-info.json').write_text(json.dumps(dict(scene_id=args.scene,quality='basic',source_range=[info['source_start'],info['source_end']],sample_frames=frames,static_glb=True,refining='deferred'),indent=2)+'\n');print('BASIC_SCENE_BUILT',args.scene)
