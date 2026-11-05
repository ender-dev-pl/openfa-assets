"""Extract a standalone editable shot, export its static midpoint and render samples."""
import bpy,argparse,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--scene',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--samples',default='176');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);s=next(s for s in bpy.data.scenes if s.name.startswith(a.scene+' — '));a.out.mkdir(parents=True,exist_ok=True);lib=a.out/(a.scene+'-library.blend');bpy.data.libraries.write(str(lib),{s});bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(lib)) as (src,dst):dst.scenes=src.scenes
s=dst.scenes[0];bpy.context.window.scene=s;s.frame_set((s.frame_start+s.frame_end)//2);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(a.out/(a.scene+'.blend')))
for o in list(s.objects):
 if o.type in ['FONT','CURVE']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(a.out/(a.scene+'.glb')),export_format='GLB',export_animations=False,export_current_frame=True,export_apply=True,export_cameras=True,export_lights=False)
bpy.ops.wm.open_mainfile(filepath=str(a.out/(a.scene+'.blend')));s=bpy.context.scene
for n in map(int,filter(None,a.samples.split(','))):
 s.frame_set(n*2+1);s.cycles.samples=12;s.render.filepath=str(a.out/f'{a.scene}-{n}.png');bpy.ops.render.render(write_still=True)
lib.unlink()
