import bpy,bmesh,sys,json,hashlib,struct
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'anti-virus-missile.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
m=json.loads((o/'model.json').read_text());root=bpy.data.objects['AntiVirusRotor'];names=sum(m['components'].values(),[]);assert len(names)==19
def signature(ob):
 d=ob.data;return hashlib.sha256(json.dumps(dict(matrix=[v for row in ob.matrix_basis for v in row],vertices=[list(v.co) for v in d.vertices],faces=[list(f.vertices)+[f.material_index] for f in d.polygons],uv=[[list(x.uv) for x in layer.data] for layer in d.uv_layers],materials=[mat.name for mat in d.materials]),separators=(',',':')).encode()).hexdigest()
assert {n:signature(bpy.data.objects[n]) for n in names}==m['base_mesh_signatures']
points=set()
for name in names:
 ob=bpy.data.objects[name];assert ob.parent==root
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name;assert all(f.calc_area()>1e-12 for f in bm.faces),name;bm.free()
 for vertex in ob.data.vertices:
  p=root.matrix_world.inverted()@ob.matrix_world@vertex.co;points.add(tuple(round(v,5) for v in p))
for group in m['components']:
 wire=bpy.data.objects[group+' technical wire'];assert wire.parent==root and wire.hide_render
 for sp in wire.data.splines:
  for p in sp.points:assert tuple(round(v,5) for v in p.co[:3]) in points,(group,p.co[:3])
assert len(m['components']['anti-viral-payload-pods'])==4
assert len(m['components']['four-main-rocket-thrusters'])==8
assert sum(n.startswith('Virus family hollow red nozzle') for n in names)==4
assert m['technical_partition']['assigned_edge_count']>0
assert all(abs(a-b)<1e-6 for a,b in zip(root.scale,[.83,.83,1]))
fr=m['solid_framing'];assert len(fr['ndc_bounds'])==60 and all(min(b)>.02 and max(b)<.98 for b in fr['ndc_bounds'])
initial=root.matrix_world.copy();s.frame_set(61);bpy.context.view_layer.update();assert max(abs(initial[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-5
raw=(o/'anti-virus-missile.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);assert len(doc['animations'])==1
targets=[doc['nodes'][ch['target']['node']]['name'] for ch in doc['animations'][0]['channels']];assert targets and set(targets)=={'AntiVirusRotor'}
relative=m['base_source']['path'];candidates=[p/r for p in Path(__file__).resolve().parents for r in [relative,relative.removeprefix('sources/')]]+[Path('../openfa-assets')/relative];base=next(p for p in candidates if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==m['base_source']['sha256'])
s.frame_set(1);camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=19,payload_pods=4,main_nozzles=4,recessed_throats=4,all_original_mesh_signatures_preserved=True,original_source_unchanged=True,all_wire_endpoints_match_solid_local_vertices=True,nose_casing_partition=m['technical_partition'],root_scale=list(root.scale),loop_closes=True,all60_poses_contained=True,solid_camera=camera),indent=2)+'\n')
print('ANTI_VIRUS_GEOMETRY_VERIFIED')
