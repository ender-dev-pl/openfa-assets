import bpy
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene
cloud=next(o for o in s.objects if o.name.startswith('Next dissolve —'));cloud.location.z=-42.6;cloud.scale=(17.04,14.91,1)
s.frame_set(241)
for o in s.objects:
 if o.name.startswith(('Spiral galaxy —','Next dissolve —')):
  print('FIELD',o.name,list(o.location),o.active_material.node_tree.nodes['Shot dissolve'].outputs[0].default_value)
for image in bpy.data.images:
 if image.name.startswith('Spiral galaxy'):print('IMAGE',image.size[:],max(image.pixels[:]),sum(list(image.pixels)[0::4])/len(list(image.pixels)[0::4]))
bpy.ops.wm.save_as_mainfile(filepath=str(p/'opening-to-frame-150.blend'))
s.render.resolution_x=640;s.render.resolution_y=560;s.cycles.samples=16;s.render.filepath=str(p/'preview/frame-120.png');bpy.ops.render.render(write_still=True)
