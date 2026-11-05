import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
p=Path(__file__).resolve().parent; d=json.loads((p/'pose-fit.json').read_text());s=bpy.context.scene
ship=next(o for o in s.objects if o.name.startswith('SHIP —'));ship.animation_data_clear();ship.rotation_mode='QUATERNION';cam=Matrix(d['camera_world']);prev=None
for row in d['poses']:
 x,y,z,w=row['rotation'];q=cam.to_quaternion()@Quaternion((w,x,y,z))
 if prev and prev.dot(q)<0:q.negate()
 prev=q.copy();ship.rotation_quaternion=q;ship.location=cam@Vector(row['translation']);ship.keyframe_insert('location',frame=row['frame']);ship.keyframe_insert('rotation_quaternion',frame=row['frame'])
for fc in ship.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(145);bpy.ops.wm.save_as_mainfile(filepath=str(p/'opening-reconstruction-ship-fit.blend'))
s.render.resolution_x=640;s.render.resolution_y=560;s.cycles.samples=16
(p/'preview').mkdir(exist_ok=True)
for n in [0,36,60,95]:
 s.frame_set(n*2+1);s.render.filepath=str(p/'preview'/f'frame-{n:03}.png');bpy.ops.render.render(write_still=True)
