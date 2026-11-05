import bpy,bmesh,sys,json,hashlib,struct
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(o/'long-range-transmitter.blend'))
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
m=json.loads((o/'model.json').read_text());root=bpy.data.objects['TransmitterRotor']
roles=['chassis','audio-visual-console','data-cartridge-drives','data-encryption-device']
assert list(m['components'])==roles
meshes=0;curves=0;names=sum(m['components'].values(),[])
for name in names:
 ob=bpy.data.objects[name];assert ob.parent==root
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data)
  assert all(e.is_manifold for e in bm.edges),name
  assert all(f.calc_area()>1e-12 for f in bm.faces),name
  bm.free();meshes+=1
 else:
  assert ob.type=='CURVE' and ob.data.use_fill_caps,name
  assert all(len(sp.points)>2 for sp in ob.data.splines),name
  curves+=1
for prefix,total in [('Wear ',20),('Console RGB control button',3),('Data cartridge drive casing',2),('Front coloured service loop',3),('Solid-only green packet glyphs',1),('Encryption status indicator',4)]:
 assert sum(n.startswith(prefix) for n in names)==total,(prefix,total)
assert [p['component'] for p in m['phases']]==roles[1:]
fr=m['solid_framing'];assert fr['frame_count']==60 and len(fr['ndc_bounds'])==60
assert all(min(b)>.02 and max(b)<.98 for b in fr['ndc_bounds'])
assert abs(fr['ortho_scale']-s.camera.data.ortho_scale)<1e-6
start=root.matrix_world.copy();s.frame_set(61);bpy.context.view_layer.update()
assert max(abs(start[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-5
raw=(o/'long-range-transmitter.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length])
assert len(doc['animations'])==1 and not doc.get('images')
assert sum(n.get('name','').startswith('Wear ') for n in doc['nodes'])==20
s.frame_set(1)
camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
result=dict(closed_meshes=meshes,capped_curve_objects=curves,explicit_wear_meshes=20,three_rgb_controls=True,paired_cartridge_drives=True,three_service_loops=True,authored_static_green_glyphs=True,embedded_images=0,loop_closes=True,all60_poses_contained=True,solid_camera=camera,root_scale=list(root.scale),whole_information_rotation_euler=m['whole_information_rotation_euler'],blend_sha256=hashlib.sha256((o/'long-range-transmitter.blend').read_bytes()).hexdigest())
(o/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print('TRANSMITTER_GEOMETRY_VERIFIED',meshes,curves)
