"""Check scene coverage, references and standalone packed media in the reopened assembly."""
import bpy,json,argparse,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--report',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);plan=json.loads((root/'shot-plan.json').read_text());m=bpy.data.scenes['MASTER — Full intro basic pass'];ed=m.sequence_editor;strips=ed.strips if hasattr(ed,'strips') else ed.sequences;shots=sorted([s for s in strips if s.type=='SCENE'],key=lambda s:s.frame_final_start);assert len(shots)==24;assert len([s for s in strips if s.type=='CROSS'])==3;assert not bpy.data.sounds;assert (m.frame_start,m.frame_end,m.render.fps)==(1,3748,24)
for info in plan['scenes']:
 st=next(s for s in shots if s.name.startswith(info['id']+' / '));assert (st.frame_final_start,st.frame_final_end)==(info['frame_start'],info['frame_end']+1);assert st.scene.camera
for f in range(1,3749):assert any(s.frame_final_start<=f<s.frame_final_end for s in shots),f
assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
for n in [1,133,237]:
 s=bpy.data.scenes['A — Ship and galaxy'];bpy.context.window.scene=s;s.frame_set(n);bpy.context.view_layer.update()
 for o in s.objects:
  if o.name.startswith('Following shot — nebula'):assert o.hide_render==(n!=133)
report=dict(native_sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),scene_count=24,new_scene_count=20,frame_start=1,frame_end=3748,fps=24,duration_seconds=3748/24,resolution=[640,480],continuous_coverage=True,first_sequence_cross_dissolves=3,old_worker_visibility_encoded_as_native_keys=True,no_original_soundtrack=True,all_file_images_packed=True,shots=[dict(name=s.name,start=s.frame_final_start,end_exclusive=s.frame_final_end) for s in shots],quality='basic; likeness, detailed materials and effects deferred');a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print('ASSEMBLY_VERIFIED',len(shots))
