import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=Path(__file__).resolve().parent
samples=[1,49,97,145,193,241,281,301,302]
def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;ship=next(o for o in s.objects if o.name.startswith('SHIP —'));data={}
 for f in samples:
  s.frame_set(f);anchors=[]
  for x in [-1.35,1.35]:
   uv=world_to_camera_view(s,s.camera,ship.matrix_world@Vector((x,-2.78,0)));anchors.append([480+(uv.x*960-480)*7/6,360+(uv.y*720-360)*(262/560)*(7/6)])
  data[f]=dict(midpoint=np.mean(anchors,axis=0),background={o.name:np.array(o.matrix_world) for o in s.objects if o!=ship and o.parent!=ship},parts={o.name:np.array(o.matrix_basis) for o in s.objects if o.parent==ship})
 return data,dict(camera_lens=s.camera.data.lens,resolution=[s.render.resolution_x,s.render.resolution_y],pixel_aspect=[s.render.pixel_aspect_x,s.render.pixel_aspect_y],fps=s.render.fps,frame_end=s.frame_end,packed_images=all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
a,meta=capture(p.parent/'first-scene-v6-letterbox/opening-letterbox.blend');b,newmeta=capture(p/'opening-steady-flight.blend');assert meta==newmeta
error=0
for f in samples:
 error=max(error,float(np.abs(a[f]['midpoint']-b[f]['midpoint']).max()))
 for group in ['background','parts']:
  assert a[f][group].keys()==b[f][group].keys()
  for name,m in a[f][group].items():assert np.max(np.abs(m-b[f][group][name]))<1e-6,(f,group,name)
assert error<.001,error
(p/'scene-verification.json').write_text(json.dumps(dict(background_and_part_local_transforms_unchanged=True,camera_and_letterbox_preserved=True,maximum_engine_midpoint_drift_native_pixels=error,sample_frames=samples,**newmeta),indent=2)+'\n');print('SCENE_VERIFIED',error)
