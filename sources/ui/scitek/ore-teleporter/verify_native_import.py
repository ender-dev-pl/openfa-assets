"""Verify scoped PB11 reuse, new closed hardware and independent runtime import."""
import bpy,bmesh,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
model=json.loads((out/'model.json').read_text());selected=model['preserved_source_meshes']
def sig(ob):
 data=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers},materials=[m.name for m in ob.data.materials])
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(base));expected={n:sig(bpy.data.objects[n]) for n in selected};base_hash=hashlib.sha256(base.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(out/'ore-teleporter.blend'));s=bpy.context.scene;s.frame_set(1)
assert {n:sig(bpy.data.objects[n]) for n in selected}==expected
geometry={}
for n in model['new_presentation_meshes']:
 ob=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bm.normal_update()
 bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 assert bad==0 and volume>1e-10,(n,bad,volume)
 geometry[n]=dict(nonmanifold_edges=bad,signed_volume=volume);bm.free()
assert len([n for n in model['new_presentation_meshes'] if n.startswith('Research atomic scanner')])==3
assert len(model['components']['long-range-transceiver'])>=4
assert len(model['components']['data-throughput-supercomputer'])==6
count=sum(len(v) for v in model['components'].values())
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'ore-teleporter.glb'));assert len([o for o in s.objects if o.type=='MESH'])==count
root=bpy.data.objects['OreResearchRoot'];s.frame_set(1);a=root.matrix_world.copy();s.frame_set(16);b=root.matrix_world.copy();assert sum(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>1
s.frame_set(61);assert sum(abs(a[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-4
s.frame_set(1);s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'ore-teleporter.blend'));s=bpy.context.scene;s.frame_set(1);s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'verification.json').write_text(json.dumps(dict(native_runtime=True,saved_source_reload=True,independent_solid_import=True,imported_root_rotation_and_loop_verified=True,reused_mesh_count=len(selected),source_mesh_signatures=expected,new_mesh_geometry=geometry,base_sha256=base_hash,source_sha256=hashlib.sha256((out/'ore-teleporter.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'ore-teleporter.glb').read_bytes()).hexdigest()),indent=2)+'\n')
assert base_hash==hashlib.sha256(base.read_bytes()).hexdigest()
print('ORE_NATIVE_IMPORT_VERIFIED',count)
