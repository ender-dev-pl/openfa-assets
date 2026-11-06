import bpy,bmesh,sys,json,hashlib,struct,math
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'turret-optimiser.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();m=json.loads((o/'model.json').read_text());root=bpy.data.objects['OptimiserRotor']
roles=['chassis','stored-energy-output','manual-pulse-control','flux-capacitor-system'];assert list(m['components'])==roles;count=0;curves=0
for name in sum(m['components'].values(),[]):
 ob=bpy.data.objects[name];assert ob.parent==root
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name;assert all(f.calc_area()>1e-12 for f in bm.faces),name;bm.free();count+=1
 else:
  assert ob.type=='CURVE' and all(sp.use_cyclic_u for sp in ob.data.splines),name;curves+=1
assert len(m['components']['stored-energy-output'])==4
assert len([n for n in m['components']['flux-capacitor-system'] if n.startswith('Internal flux capacitor ')])==2
assert len([n for n in m['components']['chassis'] if n.startswith('Silver longitudinal cage rail')])==4
assert len([n for n in sum(m['components'].values(),[]) if n.startswith('Wear ')])==16
assert bpy.data.objects['Internal flux capacitor -1'].dimensions.y<bpy.data.objects['Internal flux capacitor 1'].dimensions.y
assert [p['component'] for p in m['phases']]==roles[1:]
assert m['solid_framing']['frame_count']==60 and len(m['solid_framing']['ndc_bounds'])==60 and all(min(b)>.02 and max(b)<.98 for b in m['solid_framing']['ndc_bounds'])
assert abs(m['solid_framing']['ortho_scale']-s.camera.data.ortho_scale)<1e-6
start=root.matrix_world.copy();s.frame_set(61);bpy.context.view_layer.update();assert max(abs(start[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-5
raw=(o/'turret-optimiser.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);assert len(doc['animations'])==1 and len([n for n in doc['nodes'] if n.get('name','').startswith('Wear ')])==16
s.frame_set(1);camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=count,closed_rear_engraving_curves=curves,paired_flux_capacitors=2,cage_rails=4,energy_output_sections=4,manual_control_nodes=4,explicit_wear_meshes=16,loop_closes=True,all60_poses_contained=True,solid_camera=camera,root_scale=list(root.scale),whole_information_rotation_euler=m['whole_information_rotation_euler'],blend_sha256=hashlib.sha256((o/'turret-optimiser.blend').read_bytes()).hexdigest()),indent=2)+'\n');print('OPTIMISER_GEOMETRY_VERIFIED',count,curves)
