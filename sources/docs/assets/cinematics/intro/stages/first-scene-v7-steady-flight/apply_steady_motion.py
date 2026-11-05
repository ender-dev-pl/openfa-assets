import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
p=Path(__file__).resolve().parent;s=bpy.context.scene;d=json.loads((p/'steady-poses.json').read_text());ship=next(o for o in s.objects if o.name.startswith('SHIP —'));ship.animation_data_clear();ship.rotation_mode='QUATERNION';cam=Matrix(d['camera_world']);prev=None
for row in d['poses']:
 x,y,z,w=row['rotation'];q=cam.to_quaternion()@Quaternion((w,x,y,z))
 if prev and prev.dot(q)<0:q.negate()
 prev=q.copy();ship.rotation_quaternion=q;ship.location=cam@Vector(row['translation']);ship.keyframe_insert('location',frame=row['frame']);ship.keyframe_insert('rotation_quaternion',frame=row['frame'])
for fc in ship.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s['motion_revision']='v7: damped secondary rocking and regularized angular acceleration; engine screen midpoint and depth preserved.';s.frame_set(193);bpy.ops.wm.save_as_mainfile(filepath=str(p/'opening-steady-flight.blend'))
s.render.resolution_x=640;s.render.resolution_y=480;s.cycles.samples=8;(p/'preview').mkdir(exist_ok=True)
for n in [24,48,72,96,120,150]:
 s.frame_set(2*n+1)
 for o in s.objects:
  if o.name.startswith('Following shot — nebula'):o.hide_render=n<66 or n>=118
  elif o.name.startswith('Spiral galaxy —'):o.hide_render=n<104
  elif o.name.startswith('Next dissolve —'):o.hide_render=n<144
 s.render.filepath=str(p/'preview'/f'frame-{n:03d}.png');bpy.ops.render.render(write_still=True)
