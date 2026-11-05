"""Verify the separate legacy-labelled assemblies and real GLB animation."""
import bpy,bmesh,sys,json,struct,hashlib
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'missile-bay-extension.blend'));s=bpy.context.scene
model=json.loads((o/'model.json').read_text());root=bpy.data.objects['MissileBayRig'];carriage=bpy.data.objects['HydraulicTransferCarriage']
assert list(model['components'])==['chassis','revolving-storage-rack','missile-loading-assembly','targeting-control']
assert len(model['phases'])==3 and model['information_timeline_frames']==423
assert root.animation_data is None
closed=0
for name in sum(model['components'].values(),[]):
 ob=bpy.data.objects[name];parent=ob.parent
 while parent and parent!=root:parent=parent.parent
 assert parent==root,name
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name
  assert all(f.calc_area()>1e-10 for f in bm.faces),name
  bm.free();closed+=1
rig=json.loads((o/'solid-animation-timeline.json').read_text());assert rig['frame_count']==180 and len(rig['timeline'])==180 and not rig['body_turntable']
assert rig['source_blend_sha256']==hashlib.sha256((o/'missile-bay-extension.blend').read_bytes()).hexdigest()
assert rig['source_glb_sha256']==hashlib.sha256((o/'missile-bay-extension.glb').read_bytes()).hexdigest()
assert len(rig['animated_mesh_nodes'])==5
assert len([n for n in model['components']['revolving-storage-rack'] if n.startswith('Stored missile body')])==20
raw=(o/'missile-bay-extension.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);assert len(doc['animations'])==1
camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_hardware_meshes=closed,stored_missiles=20,animated_meshes=5,preview_frames=180,body_turntable=False,single_animation_clip=True,solid_camera=camera,source_blend_sha256=rig['source_blend_sha256']),indent=2)+'\n')
print('MISSILE_BAY_GEOMETRY_VERIFIED',closed)
