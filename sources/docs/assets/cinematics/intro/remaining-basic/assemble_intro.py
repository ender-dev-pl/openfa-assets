"""Assemble verified shots after the preserved first sequence; no legacy media required."""
import bpy,json,argparse,sys
from pathlib import Path
root=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);plan=json.loads((root/'shot-plan.json').read_text());assert all(s['status']=='basic_verified' for s in plan['scenes'])
bpy.ops.wm.open_mainfile(filepath=str(root.parent/'stages/first-sequence-v8-to-frame-412/first-sequence-to-412.blend'))
m=bpy.data.scenes['MASTER — First sequence through original frame 412'];m.name='MASTER — Full intro basic pass';bpy.context.window.scene=m
# Encode the old render worker's visibility rule as native keys, so standalone playback agrees.
for o in bpy.data.scenes['A — Ship and galaxy'].objects:
 if o.name.startswith('Following shot — nebula'):
  for f,v in [(1,True),(132,True),(133,False),(236,False),(237,True)]:o.hide_render=v;o.keyframe_insert('hide_render',frame=f)
  for fc in o.animation_data.action.fcurves:
   if fc.data_path=='hide_render':
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
 elif o.name.startswith('Next dissolve —'):o.hide_render=True
ed=m.sequence_editor;strips=ed.strips if hasattr(ed,'strips') else ed.sequences
assert len([s for s in strips if s.type=='SCENE'])==4
for info in plan['scenes']:
 with bpy.data.libraries.load(str(root/info['native']),link=False) as (src,dst):
  names=[n for n in src.scenes if n.startswith(info['id']+' — ')];assert len(names)==1;dst.scenes=names
 s=dst.scenes[0];st=strips.new_scene(info['id']+' / '+info['name'],s,1,info['frame_start']);st.scene_input='CAMERA';st.frame_final_duration=info['frame_end']-info['frame_start']+1
 assert st.frame_final_start==info['frame_start'] and st.frame_final_end==info['frame_end']+1
m.frame_start=1;m.frame_end=3748;m.render.fps=24;m.render.resolution_x=640;m.render.resolution_y=480;m.render.resolution_percentage=100;m.render.filepath='//renders/full-intro-';m['quality']='preserved first sequence plus basic remaining scenes; refining deferred';m['source_frames']=1874;m['source_fps']=12;m.frame_set(2401)
assert not bpy.data.sounds;assert all(i.packed_file for i in bpy.data.images if i.source=='FILE');a.out.parent.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(a.out),compress=False);print('FULL_INTRO_ASSEMBLED',len([s for s in strips if s.type=='SCENE']),m.frame_end)
