"""Preserve the articulated source, validate frozen diagram edges and imported motion."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,kdtree
args=sys.argv[sys.argv.index('--')+1:];assets,out=map(lambda p:Path(p).resolve(),args[:2]);out.mkdir(parents=True,exist_ok=True)
baseline=assets/'sources/ui/scitek/anti-missile-pod';folder=Path(args[2]).resolve() if len(args)>2 else assets/'sources/objects/terran/anti-missile-pod/refined'
source=folder/('anti-missile-pod.blend' if (folder/'anti-missile-pod.blend').exists() else 'model.blend');glb=folder/('anti-missile-pod.glb' if (folder/'anti-missile-pod.glb').exists() else 'model.glb')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((baseline/'model.json').read_text());names=sum(model['components'].values(),[]);assert len(names)==31
def signature(ob):
 d=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={u.name:[list(p.uv) for p in u.data] for u in ob.data.uv_layers},materials=[m.name for m in ob.data.materials],matrix=[list(r) for r in ob.matrix_basis],parent=ob.parent.name if ob.parent else None)
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(baseline/'anti-missile-pod.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();expected={n:signature(bpy.data.objects[n]) for n in names}
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert {n:signature(bpy.data.objects[n]) for n in names}==expected
assert sha(glb)==sha(baseline/'anti-missile-pod.glb')
deps=bpy.context.evaluated_depsgraph_get();edges=[];volumes={};seam_checks={}
for name in names:
 ob=bpy.data.objects[name];raw=bmesh.new();raw.from_mesh(ob.data);assert all(e.is_manifold for e in raw.edges),name;raw.free()
 ev=ob.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
 before=sum(not e.is_manifold for e in bm.edges);vertices_before=len(bm.verts)
 if before:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 assert all(e.is_manifold for e in bm.edges),name
 seam_checks[name]=dict(nonmanifold_before=before,vertices_before=vertices_before,vertices_after=len(bm.verts),validation_only_weld_tolerance=1e-6 if before else 0,nonmanifold_after=0)
 volume=bm.calc_volume(signed=True);assert volume>0,(name,volume);volumes[name]=volume;bm.free()
 points=[ob.matrix_world@v.co for v in mesh.vertices];edges.extend((points[e.vertices[0]],points[e.vertices[1]]) for e in mesh.edges);ev.to_mesh_clear()
tree=kdtree.KDTree(len(edges))
for i,(a,b) in enumerate(edges):tree.insert((a+b)*.5,i)
tree.balance();wire={}
for ob in s.objects:
 if not ob.name.endswith(' technical wire'):continue
 maximum=0
 for sp in ob.data.splines:
  assert len(sp.points)==2;a,b=[ob.matrix_world@Vector(p.co[:3]) for p in sp.points];errors=[]
  for _,index,_ in tree.find_range((a+b)*.5,2e-5):
   c,d=edges[index];errors.append(min(max((a-c).length,(b-d).length),max((a-d).length,(b-c).length)))
  assert errors and min(errors)<2e-5,ob.name;maximum=max(maximum,min(errors))
 wire[ob.name]=dict(segments=len(ob.data.splines),maximum_endpoint_error=maximum)
assert len(wire)==4
nodes=names+['PodResearchRoot','PodTrackingHead','PodFixedBase'];poses={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();poses[f]={n:bpy.data.objects[n].matrix_world.copy() for n in nodes}
assert all(poses[f]['PodFixedBase']==poses[1]['PodFixedBase'] for f in poses)
assert max(abs(poses[1]['PodResearchRoot'][i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))<1e-6
assert max(abs(poses[1]['PodTrackingHead'][i][j]-poses[16]['PodTrackingHead'][i][j]) for i in range(4) for j in range(4))>.5
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene;assert len([o for o in s.objects if o.type=='MESH'])==31;maximum=0
for f in poses:
 s.frame_set(f);bpy.context.view_layer.update()
 for n,m in poses[f].items():maximum=max(maximum,max(abs(bpy.data.objects[n].matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)))
assert maximum<1e-4
report=dict(source_sha256=sha(source),glb_sha256=sha(glb),preserved_research_meshes=31,preserved_signatures=expected,colour_glb_unchanged=True,evaluated_closed_positive_meshes=volumes,wire_components=wire,wire_segments=sum(x['segments'] for x in wire.values()),actual_evaluated_edge_correspondence=True,all61_import_pose_max_error=maximum,gameplay_root_identity=True,fixed_base_and_moving_head_verified=True,technical_wire_frozen_head_frame=1,limitations=['Head aiming integration and gameplay scale require client checks. Technical mode uses the initial head pose. Existing authored slot count and hidden construction remain approximations.'])
report['topology_seam_checks']=seam_checks
(out/'shared-geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('POD_SHARED_GEOMETRY_VERIFIED',report['wire_segments'],maximum)
