"""Verify PM10 source retention, new pods/fins and independent runtime import."""
import bpy,bmesh,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
model=json.loads((out/'model.json').read_text());selected=model['preserved_source_meshes']
def sig(ob):
 data=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers},materials=[m.name for m in ob.data.materials])
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(base));expected={n:sig(bpy.data.objects[n]) for n in selected};base_hash=hashlib.sha256(base.read_bytes()).hexdigest()
expected_textures={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
expected_source_poses={n:bpy.data.objects[n].matrix_world.copy() for n in selected}
bpy.ops.wm.open_mainfile(filepath=str(out/'warp-generator.blend'));s=bpy.context.scene;s.frame_set(1)
assert {n:sig(bpy.data.objects[n]) for n in selected}==expected
packed={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
assert all(packed.get(n)==value for n,value in expected_textures.items())
assert all(packed.get(n)==value for n,value in model['authoring_texture_inputs'].items())
from mathutils import Vector
refinements=model['source_transform_refinements']
inverse=bpy.data.objects['WarpGeneratorRoot'].matrix_world.inverted()
unchanged_source_pose_error=max(abs((inverse@bpy.data.objects[n].matrix_world)[i][j]-pose[i][j]) for n,pose in expected_source_poses.items() if n not in refinements for i in range(4) for j in range(4))
for n,delta in refinements.items():expected_source_poses[n].translation+=Vector(delta)
source_pose_error=max(abs((inverse@bpy.data.objects[n].matrix_world)[i][j]-pose[i][j]) for n,pose in expected_source_poses.items() for i in range(4) for j in range(4))
assert source_pose_error<1e-6 and unchanged_source_pose_error<1e-6
geometry={}
for n in model['new_presentation_meshes']:
 ob=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bm.normal_update()
 bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert bad==0 and volume>1e-10,(n,bad,volume)
 geometry[n]=dict(nonmanifold_edges=bad,signed_volume=volume);bm.free()
assert len(selected)==37
assert len(model['components']['energy-flow-monitoring'])==5 and sum(n.startswith('Monitored energy duct') for n in model['components']['flux-capacitor-and-energy-ducts'])==4
assert all(bpy.data.objects.get(n) is None for n in model['removed_source_meshes'])
assert len(model['phases'])==3 and model['information_timeline_frames']==423
count=sum(len(v) for v in model['components'].values())

all_nodes=[n for names in model['components'].values() for n in names];expected_motion={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();expected_motion[f]={n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in all_nodes}
s.frame_set(1)

for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'warp-generator.glb'));assert len([o for o in s.objects if o.type=='MESH'])==count
motion_error=0
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update()
 for n in all_nodes:
  error=max(abs(a-b) for a,b in zip(expected_motion[f][n],[v for row in bpy.data.objects[n].matrix_world for v in row]));motion_error=max(motion_error,error);assert error<1e-4,(f,n,error)
root=bpy.data.objects['WarpGeneratorRoot'];s.frame_set(1);a=root.matrix_world.copy();s.frame_set(16);b=root.matrix_world.copy();assert sum(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>1
s.frame_set(61);assert sum(abs(a[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-4
s.frame_set(1);s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'warp-generator.blend'));s=bpy.context.scene;s.frame_set(1);s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'verification.json').write_text(json.dumps(dict(native_runtime=True,saved_source_reload=True,independent_solid_import=True,imported_root_rotation_and_loop_verified=True,all_61_native_import_mesh_pose_max_error=motion_error,reused_mesh_count=len(selected),source_mesh_signatures=expected,preserved_packed_texture_sha256=expected_textures,new_packed_texture_sha256=packed,source_pose_max_error=unchanged_source_pose_error,unchanged_source_pose_count=len(selected)-len(refinements),declared_source_transform_refinements=refinements,expected_refined_pose_max_error=source_pose_error,new_mesh_geometry=geometry,base_sha256=base_hash,source_sha256=hashlib.sha256((out/'warp-generator.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'warp-generator.glb').read_bytes()).hexdigest()),indent=2)+'\n')
assert base_hash==hashlib.sha256(base.read_bytes()).hexdigest()
print('WARP_MISSILE_NATIVE_IMPORT_VERIFIED',count)
