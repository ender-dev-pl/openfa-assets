import bpy
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent;C=bpy.data.scenes['C — Surface flight and mechanical footprint'];cam=C.camera
for f,loc,target in [(741,(0,-1.4,11.4),(.22,.45,-1)),(777,(0,-1.1,11.4),(.22,.45,-1))]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
for m in bpy.data.materials:
 if m.name.startswith(('Mechanical boots /','Boot soles /','Boot edge seams /')):
  bs=m.node_tree.nodes.get('Principled BSDF')
  if m.name.startswith('Mechanical boots /'):bs.inputs['Metallic'].default_value=.35
  for n in m.node_tree.nodes:
   if n.type=='BUMP':n.inputs['Strength'].default_value=.15;n.inputs['Distance'].default_value=.018
   if n.type=='VALTORGB':
    base=(.28,.34,.37) if m.name.startswith('Mechanical boots /') else (.04,.06,.07)
    n.color_ramp.elements[0].color=(*[x*.65 for x in base],1);n.color_ramp.elements[1].color=(*[x*1.25 for x in base],1)
for o in C.objects:
 if 'Imprint' in o.name or 'imprint' in o.name or 'engraved imprint' in o.name:
  o.hide_render=True;o.keyframe_insert('hide_render',frame=625);o.hide_render=False;o.keyframe_insert('hide_render',frame=633)
master=bpy.data.scenes['MASTER — First sequence through original frame 412'];bpy.context.window.scene=master;master.frame_set(329);bpy.ops.wm.save_as_mainfile(filepath=str(p/'first-sequence-to-412.blend'))
for s in bpy.data.scenes:
 if s.render.engine=='CYCLES':s.cycles.samples=8
for n in [150,176,380,412]:
 master.frame_set(n*2+1);master.render.filepath=str(p/'preview'/f'master-{n:03d}.png');bpy.ops.render.render(write_still=True,scene=master.name)
print('MASTER_PREVIEWS_FINISHED',flush=True)
