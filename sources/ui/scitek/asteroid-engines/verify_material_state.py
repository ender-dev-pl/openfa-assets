"""Verify saved material animation against the external source clock, including half frames."""
import bpy,sys,json,hashlib
from pathlib import Path
info,clock_path=map(lambda p:Path(p).resolve(),sys.argv[sys.argv.index('--')+1:]);clock=json.loads(clock_path.read_text());assert clock['frame_count']==425
bpy.ops.wm.open_mainfile(filepath=str(info/'asteroid-engines-information.blend'));s=bpy.context.scene;names=['chassis']+clock['components'];samples=[]
def check(time,frame):
 s.frame_set(int(time),subframe=time-int(time));selected=clock['components'][clock['component_phase_by_frame'][frame]] if clock['red_active_by_frame'][frame] else None
 for name in names:
  ob=bpy.data.objects[name+' technical wire'];colour=ob.data.materials[0].node_tree.nodes.get('Emission').inputs['Color'].default_value;expected=(.9,.003,.001,1) if name==selected else (0,.72,.005,1)
  assert all(abs(a-b)<1e-5 for a,b in zip(colour,expected)),(time,name,list(colour),expected)
 visible=[o for o in s.objects if o.type in ['MESH','CURVE'] and not o.hide_render];assert len(visible)==4 and all(o.name.endswith(' technical wire') for o in visible)
for frame in range(425):check(frame+1,frame)
for frame in range(424):
 if (clock['red_active_by_frame'][frame],clock['component_phase_by_frame'][frame])!=(clock['red_active_by_frame'][frame+1],clock['component_phase_by_frame'][frame+1]):check(frame+1.5,frame);samples.append(frame+1.5)
(info/'material-state-verification.json').write_text(json.dumps(dict(material_clock_sha256=hashlib.sha256(clock_path.read_bytes()).hexdigest(),information_blend_sha256=hashlib.sha256((info/'asteroid-engines-information.blend').read_bytes()).hexdigest(),evaluated_frames=425,half_frame_transition_samples=samples,source_material_states_verified=True,technical_only_visibility_verified=True),indent=2)+'\n',encoding='utf-8');print('ENGINES_MATERIAL_STATE_VERIFIED',425,len(samples))
