import bpy
from pathlib import Path
p=Path(__file__).resolve().parent;m=bpy.data.scenes['MASTER — First sequence through original frame 412'];m.view_settings.view_transform='AgX';m.view_settings.look='AgX - Medium High Contrast';a=bpy.data.scenes['A — Ship and galaxy'];a.render.resolution_x=640;a.render.resolution_y=480;bpy.context.window.scene=m;m.frame_set(353);bpy.ops.wm.save_as_mainfile(filepath=str(p/'first-sequence-to-412.blend'))
for s in bpy.data.scenes:
 if s.render.engine=='CYCLES':s.cycles.samples=8
for n in [60,176,380]:
 m.frame_set(n*2+1);m.render.filepath=str(p/'preview'/f'final-master-{n:03d}.png');bpy.ops.render.render(write_still=True,scene=m.name)
print('MASTER_AGX_CHECK_FINISHED')
