import bpy,bmesh,sys,json,hashlib,struct
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'anti-missile-pod.blend'))
s=bpy.context.scene;m=json.loads((o/'model.json').read_text());head=bpy.data.objects['PodTrackingHead'];base=bpy.data.objects['PodFixedBase'];root=bpy.data.objects['PodResearchRoot']
assert head.parent==base.parent==root
assert list(m['components'])==['chassis','twin-tracking-dishes','alloy-plasma-barrel','armoured-plasma-base']
names=sum(m['components'].values(),[]);counts={};mesh_count=0
for name in names:
 ob=bpy.data.objects[name];assert ob.type=='MESH',name
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name
 assert all(f.calc_area()>1e-12 for f in bm.faces),name
 bm.free();mesh_count+=1
for prefix,total in [('Twin tracking dish ',2),('Tracking dish mounting neck ',2),('Slender stepped plasma barrel',1),('Wear ',15)]:
 counts[prefix]=sum(n.startswith(prefix) for n in names);assert counts[prefix]==total,(prefix,counts[prefix])
poses=[]
for f in [1,16,31,46,61]:
 s.frame_set(f);bpy.context.view_layer.update();poses.append(dict(frame=f,head=[v for row in head.matrix_world for v in row],base=[v for row in base.matrix_world for v in row]))
assert all(x['base']==poses[0]['base'] for x in poses)
assert len({tuple(round(v,5) for v in x['head']) for x in poses[:4]})==4
assert max(abs(a-b) for a,b in zip(poses[0]['head'],poses[-1]['head']))<1e-5
fr=m['solid_framing'];assert len(fr['ndc_bounds'])==60 and all(min(b)>.02 and max(b)<.98 for b in fr['ndc_bounds'])
relative=m['base_source']['path']
if '--base-blend' in sys.argv:base_path=Path(sys.argv[sys.argv.index('--base-blend')+1]).resolve()
else:
 candidates=[p/r for p in Path(__file__).resolve().parents for r in [relative,relative.removeprefix('sources/')]]+[Path('../openfa-assets')/relative]
 base_path=next(p for p in candidates if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==m['base_source']['sha256'])
assert hashlib.sha256(base_path.read_bytes()).hexdigest()==m['base_source']['sha256']
raw=(o/'anti-missile-pod.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);assert len(doc['animations'])==1
targets=[dict(node=doc['nodes'][c['target']['node']]['name'],path=c['target']['path']) for c in doc['animations'][0]['channels']]
assert targets and all(x['node']=='PodTrackingHead' for x in targets),targets
s.frame_set(1);camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
(o/'geometry-verification.json').write_text(json.dumps(dict(mesh_count=mesh_count,component_counts=counts,source_unchanged=True,fixed_base_and_rotating_head=True,loop_closes=True,all60_poses_contained=True,poses=poses,glb_animation_targets=targets,solid_camera=camera),indent=2)+'\n')
print('POD_GEOMETRY_VERIFIED',mesh_count)
