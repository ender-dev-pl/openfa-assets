"""Actual corrected saved-source reload and independent GLB bind-pose render."""
import bpy, sys, json, hashlib
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve()
out=Path(sys.argv[sys.argv.index('--')+2]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.frame_set(1)
s.cycles.samples=16
s.render.resolution_x=576
s.render.resolution_y=640
s.render.film_transparent=True
s.render.filepath=str(out/'solid.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
s.frame_set(1)
s.cycles.samples=16
s.render.resolution_x=576
s.render.resolution_y=640
s.render.film_transparent=True
s.render.filepath=str(out/'reload-solid.png')
bpy.ops.render.render(write_still=True)
for ob in list(s.objects):
    if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(source.with_suffix('.glb')))
s.frame_set(1)
s.render.filepath=str(out/'imported-solid.png')
bpy.ops.render.render(write_still=True)
print('ST14_SOLID_RELOAD_IMPORT_RENDERED')
