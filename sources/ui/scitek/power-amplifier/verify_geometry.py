import bpy,sys,json,bmesh,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'power-amplifier.blend'));s=bpy.context.scene
model=json.loads((o/'model.json').read_text());roles=['chassis','ethereal-vapour-generator','distorted-reflector','optical-coupling-ports'];assert list(model['components'])==roles
root=bpy.data.objects['AmplifierRotor'];count=0
for name in sum(model['components'].values(),[]):
 ob=bpy.data.objects[name];assert ob.parent==root
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name;assert all(f.calc_area()>1e-10 for f in bm.faces),name;bm.free();count+=1
assert [p['component'] for p in model['phases']]==roles[1:]
assert len([n for n in sum(model['components'].values(),[]) if n.startswith('Wear ')])==27
assert len([n for n in model['components']['chassis'] if n.endswith(' amplifier collar')])==3
assert len([n for n in model['components']['optical-coupling-ports'] if n.startswith('Optical coupling red lens ')])==2
assert len(model['components']['distorted-reflector'])==1
assert abs(root.scale.x-1.04)<1e-5
assert abs(model['phases'][1]['closeup_rotation_euler'][0]-math.pi/2)<1e-5
assert not bpy.data.objects['Upper central chamber shell'].ray_cast(Vector((0,-.70,2.28)),Vector((0,1,0)),distance=.42)[0],'The U-shaped front opening must be physically clear'
s.frame_set(1);bpy.context.view_layer.update();start=root.matrix_world.copy();s.frame_set(61);bpy.context.view_layer.update();assert max(abs(start[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-5
raw=(o/'power-amplifier.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);assert len(doc['animations'])==1
assert len([n for n in doc['nodes'] if n.get('name','').startswith('Wear ')])==27
s.frame_set(1);camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=count,explicit_wear_meshes=27,collars=3,optical_lenses=2,reflector_meshes=1,physical_front_opening=True,loop_closes=True,solid_camera=camera,root_scale=list(root.scale),bind_component_yaw_degrees=-30,blend_sha256=hashlib.sha256((o/'power-amplifier.blend').read_bytes()).hexdigest()),indent=2)+'\n');print('AMPLIFIER_GEOMETRY_VERIFIED',count)
