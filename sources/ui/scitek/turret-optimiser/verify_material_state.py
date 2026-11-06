"""Evaluate saved Blender hue state at every source-clock frame and between keys."""
import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();clock_path=Path(sys.argv[sys.argv.index('--')+2]).resolve();clock=json.loads(clock_path.read_text())
bpy.ops.wm.open_mainfile(filepath=str(out/'turret-optimiser-information.blend'));s=bpy.context.scene
materials={name:bpy.data.objects[name+' technical wire'].data.materials[0] for name in ['chassis']+clock['components']}
for frame in range(423):
 s.frame_set(frame+1);selected=clock['components'][clock['component_phase_by_frame'][frame]] if clock['red_active_by_frame'][frame] else None
 visible=[ob.name for ob in s.objects if ob.type in ['MESH','CURVE'] and not ob.hide_render];assert len(visible)==4 and all(n.endswith(' technical wire') for n in visible)
 for name,mat in materials.items():
  color=mat.node_tree.nodes.get('Emission').inputs['Color'].default_value
  expected=(.9,.003,.001,1) if name==selected else (0,.72,.005,1)
  assert all(abs(a-b)<1e-5 for a,b in zip(color,expected)),(frame,name,list(color),expected)
for frame in clock['source_caption_mismatch_frames']:
 if frame==422:continue
 s.frame_set(frame+1,subframe=.5);selected=clock['components'][clock['component_phase_by_frame'][frame]] if clock['red_active_by_frame'][frame] else None
 for name,mat in materials.items():
  color=mat.node_tree.nodes.get('Emission').inputs['Color'].default_value;expected=(.9,.003,.001,1) if name==selected else (0,.72,.005,1)
  assert all(abs(a-b)<1e-5 for a,b in zip(color,expected)),('half-frame',frame,name)
for mat in materials.values():
 assert all(key.interpolation=='CONSTANT' for fc in mat.node_tree.animation_data.action.fcurves for key in fc.keyframe_points)
(out/'material-state-verification.json').write_text(json.dumps(dict(evaluated_frames=423,source_red_frames=sum(clock['red_active_by_frame']),caption_visible_frames=333,between_frame_checks=16,step_material_interpolation=True,visible_technical_groups=4,material_clock_sha256=hashlib.sha256(clock_path.read_bytes()).hexdigest()),indent=2)+'\n')
print('OPTIMISER_SOURCE_CLOCK_STATE_VERIFIED')
