import bpy,bmesh,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
def signature(ob):
 a=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={u.name:[list(v.uv) for v in u.data] for u in ob.data.uv_layers},matrix=[list(row) for row in ob.matrix_basis]);return hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(base));expected=signature(bpy.data.objects['Central segmented field orb'])
bpy.ops.wm.open_mainfile(filepath=str(out/'gravity-nullifier.blend'));s=bpy.context.scene;assert signature(bpy.data.objects['Central segmented field orb'])==expected;model=json.loads((out/'model.json').read_text());meshes=[o for o in s.objects if o.type=='MESH'];count=len(meshes);volumes={}
for ob in meshes:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;v=bm.calc_volume(signed=True);assert v>0,(ob.name,v);volumes[ob.name]=v;bm.free()
sensors=[o for o in meshes if o.name.startswith('Research cardinal sensor ')];assert len(sensors)==4
baseparts=[bpy.data.objects[n] for n in model['components']['fixed-shaped-base'] if not n.startswith('Wear')]
def base_hit(x,y):
 for ob in baseparts:
  inv=ob.matrix_world.inverted();a=inv@Vector((x,y,.6));b=inv.to_3x3()@Vector((0,0,-1))
  if ob.ray_cast(a,b)[0]:return True
 return False
import math
holes=[]
for angle in [math.pi/6,5*math.pi/6,3*math.pi/2]:
 x=.75*math.cos(angle);y=.75*math.sin(angle);assert not base_hit(x,y);holes.append([x,y])
for angle in [math.pi/2,7*math.pi/6,11*math.pi/6]:assert base_hit(.75*math.cos(angle),.75*math.sin(angle))
for ob in list(s.objects):
 if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'gravity-nullifier.glb'));assert len([o for o in s.objects if o.type=='MESH'])==count
root=bpy.data.objects['NullifierResearchRoot'];s.frame_set(1);a=root.matrix_world.copy();s.frame_set(16);b=root.matrix_world.copy();assert sum(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))>1;s.frame_set(1);s.render.filepath=str(out/'imported-solid.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'gravity-nullifier.blend'));s=bpy.context.scene;s.frame_set(1);s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True)
(out/'verification.json').write_text(json.dumps(dict(native_runtime=True,saved_source_reload=True,independent_solid_import=True,imported_root_rotation_verified=True,reused_orb_geometry_uv_local_transform_sha256=expected,original_source_sha256=hashlib.sha256(base.read_bytes()).hexdigest(),source_sha256=hashlib.sha256((out/'gravity-nullifier.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'gravity-nullifier.glb').read_bytes()).hexdigest(),closed_positive_meshes=volumes,cardinal_sensors=4,verified_open_base_sectors=holes,scoped_arm_support_rays_passed=True,limitations=['Scoped open-sector/support rays; authored approximate construction, not exhaustive mechanical or recovered-source geometry acceptance.']),indent=2)+'\n',encoding='utf-8');print('NULLIFIER_NATIVE_IMPORT_VERIFIED',count)
