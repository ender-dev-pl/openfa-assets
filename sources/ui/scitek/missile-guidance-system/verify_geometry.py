import bpy,sys,json,bmesh,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'missile-guidance-system.blend'));s=bpy.context.scene
model=json.loads((o/'model.json').read_text());roles=['chassis','holographic-sphere','targeting-io','armoured-computer-casing'];assert list(model['components'])==roles
root=bpy.data.objects['GuidanceRotor'];count=0
for name in sum(model['components'].values(),[]):
 ob=bpy.data.objects[name];assert ob.parent==root
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name;assert all(f.calc_area()>1e-10 for f in bm.faces),name;bm.free();count+=1
assert [p['component'] for p in model['phases']]==roles[1:]
assert len([n for n in model['components']['targeting-io'] if n.startswith('Wear belt')])==28
assert len([n for n in model['components']['armoured-computer-casing'] if n.startswith('Wear armour')])==12
assert len([n for n in model['components']['targeting-io'] if n.startswith('Red I O status indicator')])==3
assert len([n for n in model['components']['targeting-io'] if n.startswith('Small data connector')])==8
for name in ['Pointed front armour skirt','Pointed rear armour skirt']:
 skirt=bpy.data.objects[name];assert abs(skirt.data.vertices[16].co.z-.13)<1e-5 and abs(skirt.data.vertices[0].co.z-.56)<1e-5,name
normal=Vector((0,-math.sin(.85),math.cos(.85)));centre=Vector((0,0,1.47))+normal*1.025
assert not bpy.data.objects['Arched targeting interface strap'].ray_cast(centre+normal*.30,-normal,distance=.50)[0],'The optical aperture must be an actual clear through-hole'
assert abs(model['phases'][0]['closeup_rotation_euler'][0]-math.pi/2)<1e-5
s.frame_set(1);bpy.context.view_layer.update();start=root.matrix_world.copy();s.frame_set(61);bpy.context.view_layer.update();assert max(abs(start[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-5
raw=(o/'missile-guidance-system.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);assert len(doc['animations'])==1
glasses=[m for m in doc['materials'] if m.get('name')=='Translucent violet guidance glass'];assert len(glasses)==1;glass=glasses[0];assert glass.get('alphaMode')=='BLEND' and glass['pbrMetallicRoughness']['baseColorFactor'][3]<1
assert len([n for n in doc['nodes'] if n.get('name','').startswith('Wear ')])==40
assert len([m for m in doc['materials'] if m.get('name','').startswith('Holographic map ')])==6
s.frame_set(1);camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=count,explicit_wear_meshes=40,connector_pins=8,status_indicators=3,loop_closes=True,globe_alpha_mode=glass['alphaMode'],globe_base_alpha=glass['pbrMetallicRoughness']['baseColorFactor'][3],globe_extensions=glass.get('extensions',{}),solid_camera=camera,root_scale=list(root.scale),blend_sha256=hashlib.sha256((o/'missile-guidance-system.blend').read_bytes()).hexdigest()),indent=2)+'\n');print('GUIDANCE_GEOMETRY_VERIFIED',count)
