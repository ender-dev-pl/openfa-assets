"""Remove visible triangulated shading on rocks while retaining fractured silhouettes."""
import bpy
from pathlib import Path
for s in bpy.data.scenes:
 if not s.name.startswith('B — '):continue
 for o in s.objects:
  if o.type=='MESH' and o.name.startswith(('Asteroid ','Foreground hero')):
   for p in o.data.polygons:p.use_smooth=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
