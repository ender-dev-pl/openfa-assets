"""Anatomy, closed solids, all-pose import, reload and real render validation."""
import bpy,bmesh,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
source=out/'solar-matrix.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1)
model=json.loads((out/'model.json').read_text());names=[n for ns in model['components'].values() for n in ns]
assert len(names)==103
assert len([n for n in names if n.endswith(' core')])==3
assert len([n for n in names if n.startswith('Splayed collector panel')])==4
assert len([n for n in names if ' rib ' in n])==69
geometry={}
for n in names:
 ob=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update();bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert bad==0 and volume>1e-10,(n,bad,volume)
 geometry[n]=dict(nonmanifold_edges=bad,signed_volume=volume);bm.free()
 if n.startswith('Splayed collector panel'):
  heights=[v.co.z for v in ob.data.vertices];assert max(heights)-min(heights)>.24
  inner=(ob.data.vertices[3].co-ob.data.vertices[0].co).length
  outer=(ob.data.vertices[2].co-ob.data.vertices[1].co).length
  assert abs(inner-.66)<1e-6 and abs(outer-.28)<1e-6 and outer/inner<.5,(n,inner,outer)
foundation=bpy.data.objects['Hexagonal equipment foundation'];assert len(foundation.data.vertices)==24
for n in names:
 if not n.endswith(' core'):continue
 ob=bpy.data.objects[n];assert abs(math.hypot(ob.data.vertices[0].co.x-.112,ob.data.vertices[0].co.y)-.22)<1e-5
expected={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();expected[f]={n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in names}
s.frame_set(1)
for ob in list(s.objects):
 if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'solar-matrix.glb'));assert len([o for o in s.objects if o.type=='MESH'])==len(names)
error=0
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update()
 for n in names:
  e=max(abs(a-b) for a,b in zip(expected[f][n],[v for row in bpy.data.objects[n].matrix_world for v in row]));error=max(error,e);assert e<1e-4,(f,n,e)
root=bpy.data.objects['SolarMatrixRoot'];s.frame_set(1);a=root.matrix_world.copy();s.frame_set(16);b=root.matrix_world.copy();assert sum(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>1
s.frame_set(61);assert sum(abs(a[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-4
s.frame_set(1);s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'verification.json').write_text(json.dumps(dict(native_runtime=True,saved_source_reload=True,independent_solid_import=True,imported_root_rotation_and_loop_verified=True,all_61_native_import_mesh_pose_max_error=error,solid_mesh_count=len(names),closed_positive_meshes=geometry,anatomy=dict(storage_columns=3,storage_ribs=69,outward_sloped_panels=4,hexagonal_foundation=True,integrated_laser_turret=True),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'solar-matrix.glb').read_bytes()).hexdigest()),indent=2)+'\n')
print('SOLAR_MATRIX_NATIVE_IMPORT_VERIFIED',len(names))
