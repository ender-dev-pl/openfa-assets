import bpy
from pathlib import Path
p=Path(__file__).resolve().parent;C=bpy.data.scenes['C — Surface flight and mechanical footprint'];cam=C.camera
for f in [741,777]:
 cam.location=(0,0,11.4);cam.rotation_euler=(0,0,0);cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
for f,x,y in [(397,0,0),(701,0,0),(741,.022,.0453),(777,.022,.0453)]:
 cam.data.shift_x=x;cam.data.shift_y=y;cam.data.keyframe_insert('shift_x',frame=f);cam.data.keyframe_insert('shift_y',frame=f)
master=bpy.data.scenes['MASTER — First sequence through original frame 412'];bpy.context.window.scene=master;master.frame_set(329);bpy.ops.wm.save_as_mainfile(filepath=str(p/'first-sequence-to-412.blend'))
for s in bpy.data.scenes:
 if s.render.engine=='CYCLES':s.cycles.samples=8
master.frame_set(761);master.render.filepath=str(p/'preview/master-380.png');bpy.ops.render.render(write_still=True,scene=master.name)
print('END_CARD_ALIGNED')
