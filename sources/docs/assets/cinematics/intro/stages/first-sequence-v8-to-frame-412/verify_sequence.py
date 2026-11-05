import bpy,json,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent;frames=[1,49,97,145,193,241,273,287,288]
def capture(scene):
 result={}
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();result[f]={o.name:[list(row) for row in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world] for o in scene.objects if o.animation_data}
 return result
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'first-scene-v7-steady-flight/opening-steady-flight.blend'));old=capture(bpy.context.scene)
bpy.ops.wm.open_mainfile(filepath=str(p/'first-sequence-to-412.blend'));A=bpy.data.scenes['A — Ship and galaxy'];bpy.context.window.scene=A;new=capture(A)
for f in frames:
 for name,m in old[f].items():
  diff=np.max(np.abs(np.array(m)-np.array(new[f].get(name,m))))
  if diff>1e-6:print('POSE_DIFF',f,name,diff)
assert max(np.max(np.abs(np.array(m)-np.array(new[f][name]))) for f in frames for name,m in old[f].items())<1e-6
cloud=next(o for o in A.objects if o.name.startswith('Next dissolve —'))
for f in range(1,289):
 A.frame_set(f);assert abs(cloud.active_material.node_tree.nodes['Shot dissolve'].outputs[0].default_value)<1e-7
master=bpy.data.scenes['MASTER — First sequence through original frame 412'];ed=master.sequence_editor;strips=ed.strips if hasattr(ed,'strips') else ed.sequences
scene_strips=[s for s in strips if s.type=='SCENE'];effects=[s for s in strips if s.type=='CROSS'];sounds=[s for s in strips if s.type=='SOUND'];assert len(scene_strips)==4 and len(effects)==3 and len(sounds) in [0,1];assert not sounds or sounds[0].sound.packed_file
assert master.frame_end==826 and master.render.fps==24
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
report=dict(first_288_cached_frame_animation_preserved=True,scene_strips=[dict(name=s.name,scene=s.scene.name,start=s.frame_final_start,end_exclusive=s.frame_final_end) for s in scene_strips],cross_dissolves=[dict(name=s.name,start=s.frame_final_start,end_exclusive=s.frame_final_end) for s in effects],sound_packed=bool(sounds),textures_packed=True,frames=826,fps=24,output_resolution=[640,480],source_range_inclusive=[0,412],master_view_transform=master.view_settings.view_transform,master_look=master.view_settings.look)
(p/'sequence-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('SEQUENCE_VERIFIED',report)
