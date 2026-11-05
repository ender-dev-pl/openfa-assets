import bpy,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
for prefix,file in [('Spiral galaxy','procedural-galaxy.npy'),('Next dissolve','procedural-next-cloud.npy')]:
 image=next(i for i in bpy.data.images if i.name.startswith(prefix));image.unpack(method='REMOVE');image.pixels.foreach_set(np.load(p/file).ravel());image.update();image.file_format='OPEN_EXR';image.filepath_raw=str(p/file.replace('.npy','.exr'));image.save();image.pack()
s.frame_set(241);bpy.ops.wm.save_as_mainfile(filepath=str(p/'opening-to-frame-150.blend'))
s.render.resolution_x=640;s.render.resolution_y=560;s.cycles.samples=16
for n in [110,120,150]:
 s.frame_set(n*2+1);s.render.filepath=str(p/'preview'/f'frame-{n:03d}.png');bpy.ops.render.render(write_still=True)
