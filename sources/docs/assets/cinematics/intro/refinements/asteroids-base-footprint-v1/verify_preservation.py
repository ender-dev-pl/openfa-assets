"""Verify authored geometry/keyframes in the opening ship and later shots remain unchanged."""
import bpy,hashlib,json,argparse,sys,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--before',type=Path,required=True);ap.add_argument('--after',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
def fingerprint(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for s in bpy.data.scenes:
  if s.name.startswith(('B — ','C — ','D — ','MASTER')):continue
  h=hashlib.sha256()
  for o in sorted(s.objects,key=lambda o:o.name):
   h.update((o.name+o.type).encode())
   if o.type=='MESH':
    for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
    for p in o.data.polygons:h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
   elif o.type=='CURVE':
    for sp in o.data.splines:
     for p in sp.points:h.update(struct.pack('<4f',*p.co))
   if o.animation_data and o.animation_data.action:
    for f in o.animation_data.action.fcurves:
     h.update((f.data_path+str(f.array_index)).encode())
     for k in f.keyframe_points:h.update(struct.pack('<6f',*k.co,*k.handle_left,*k.handle_right));h.update(k.interpolation.encode())
  result[s.name]=h.hexdigest()
 return result
before=fingerprint(a.before);after=fingerprint(a.after);assert before==after,[s for s in before if before[s]!=after.get(s)];assert len(before)==21
m=bpy.data.scenes['MASTER — Full intro basic pass'];assert m.frame_end==3748 and m.render.fps==24;assert not bpy.data.sounds;assert all(i.packed_file for i in bpy.data.images if i.source=='FILE')
a.report.write_text(json.dumps(dict(protected_scene_count=len(before),geometry_and_object_keyframes_unchanged=before,no_original_audio=True,authored_file_images_packed=True,native_sha256=hashlib.sha256(a.after.read_bytes()).hexdigest(),scope='B/C/D reference-guided refining; shader/artistic review remains separate'),indent=2)+'\n');print('PROTECTED_SCENES_VERIFIED',len(before))
# Independent normalized camera-space comparison of the footprint/end-card contour.
from mathutils import Vector
C=bpy.data.scenes['C — Surface flight and mechanical footprint'];D=bpy.data.scenes['D — Tetra Corp copper outline and fade'];src=next(o for o in C.objects if o.name=='Footprint / pale raised letter bevel');dst=next(o for o in D.objects if o.type=='CURVE');errors=[]
for frame in [741,761,777]:
 bpy.context.window.scene=C;C.frame_set(frame);bpy.context.view_layer.update();cam=C.camera;inv=cam.matrix_basis.inverted();di=D.camera.matrix_basis.inverted();width=D.camera.data.ortho_scale
 for sp,dp in zip(src.data.splines,dst.data.splines):
  assert len(sp.points)==len(dp.points)
  for p,q in zip(sp.points,dp.points):
   v=inv@(src.matrix_basis@Vector((p.co.x,p.co.y,.024)));w=di@(dst.matrix_basis@Vector(q.co[:3]));u=v.x*cam.data.lens/cam.data.sensor_width/-v.z-cam.data.shift_x;vv=v.y*cam.data.lens/cam.data.sensor_width/-v.z-cam.data.shift_y;errors.append(max(abs(u-w.x/width),abs(vv-w.y/width))*640)
assert max(errors)<.1,max(errors)
d=json.loads(a.report.read_text());d['footprint_endcard_max_contour_error_pixels']=max(errors);d['contour_test_native_frames']=[741,761,777];a.report.write_text(json.dumps(d,indent=2)+'\n');print('LOGO_DISSOLVE_CONTOURS_REGISTERED',max(errors))
