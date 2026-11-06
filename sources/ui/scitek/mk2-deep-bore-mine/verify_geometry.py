import bpy,sys,json,bmesh,hashlib,math
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(out/'mk2-deep-bore-mine.blend'))
model=json.loads((out/'model.json').read_text());expected=['chassis','radio-seismic-probe','drill-assemblies','coolant-connectors'];assert list(model['components'])==expected
obs=list(bpy.context.scene.objects);meshes=[x for x in obs if x.type=='MESH'];root=bpy.data.objects['DeepBoreRotor']
for ob in meshes:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;bm.free();assert ob.parent==root
for prefix,n in [('Independent multi-head drill ',4),('Carbon cutting crown ',4),('Carbon drill cutting tip',16),('Radio seismic torpedo probe',1),('Probe support arm',2),('Upper collar coolant connector annulus',8),('Upper collar coolant connector dark bore',8),('Upper collar coolant connector connector sleeve',8),('Lower collar service socket annulus',8),('Hanging deep bore cable loop',2),('Secondary hanging cable loop',2)]:assert len([x for x in obs if x.name.startswith(prefix)])==n,prefix
assert model['components']['radio-seismic-probe']==['Radio seismic torpedo probe']
assert all(x['scitek_component']=='chassis' for x in obs if x.name.startswith('Probe support arm'))
for ob in obs:
 if ob.name.startswith('Hanging deep bore cable loop'):
  points=ob.data.splines[0].points;assert abs(abs(points[0].co.x)-.49)<1e-5 and abs(abs(points[-1].co.x)-.35)<1e-5
assert abs(root.scale.x-1.11)<1e-5
assert [x['component'] for x in model['phases']]==expected[1:]
assert abs(model['phases'][2]['closeup_rotation_euler'][0]-math.pi/2)<1e-5
(out/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=len(meshes),drills=4,carbon_tips=16,radio_seismic_probes=1,coolant_connectors=8,lower_service_sockets=8,cable_loops=4,root_scale=list(root.scale),probe_supports_highlighted=False,coolant_view='top-down',blend_sha256=hashlib.sha256((out/'mk2-deep-bore-mine.blend').read_bytes()).hexdigest()),indent=2)+'\n',newline='\n');print('DEEP_BORE_GEOMETRY_VERIFIED',len(meshes))
