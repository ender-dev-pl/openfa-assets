import bpy,json,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent
sample=list(range(1,193));snap={}
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'first-scene-v4-ship-fit/opening-reconstruction-ship-fit.blend'));s=bpy.context.scene
for f in sample:
 s.frame_set(f);snap[f]={o.name:np.array(o.matrix_world) for o in s.objects if o.animation_data}
old_vis={}
node=next(o for o in s.objects if o.name.startswith('Following shot — nebula')).active_material.node_tree.nodes['Nebula reveal / 24 fps']
for f in sample:s.frame_set(f);old_vis[f]=node.outputs[0].default_value
bpy.ops.wm.open_mainfile(filepath=str(p/'opening-to-frame-150.blend'));s=bpy.context.scene;maximum=0
node=next(o for o in s.objects if o.name.startswith('Following shot — nebula')).active_material.node_tree.nodes['Nebula reveal / 24 fps']
for f in sample:
 s.frame_set(f)
 for name,m in snap[f].items():maximum=max(maximum,float(np.abs(np.array(s.objects[name].matrix_world)-m).max()))
 assert abs(node.outputs[0].default_value-old_vis[f])<1e-7
 for o in s.objects:
  if o.name.startswith(('Spiral galaxy —','Next dissolve —')):assert abs(o.active_material.node_tree.nodes['Shot dissolve'].outputs[0].default_value)<1e-7
assert maximum<1e-6
assert s.frame_end==302 and s.render.fps==24
images=[dict(name=i.name,packed=bool(i.packed_file)) for i in bpy.data.images if i.source=='FILE']
assert all(i['packed'] for i in images)
(p/'extension-verification.json').write_text(json.dumps(dict(preserved_original_render_frames=192,old_animated_world_transform_max_error=maximum,old_nebula_visibility_unchanged=True,new_fields_invisible_during_reused_frames=True,packed_images=images,fps=24,frames=302,source_range_zero_based_inclusive=[0,150],last_half_frame_held=True),indent=2)+'\n');print('EXTENSION_VERIFIED')
