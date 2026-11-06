"""Preserve the source, opposing generators, physical-edge diagrams and imported poses."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,kdtree
args=sys.argv[sys.argv.index('--')+1:];assets,out=map(lambda p:Path(p).resolve(),args[:2]);out.mkdir(parents=True,exist_ok=True)
baseline=assets/'sources/ui/scitek/screen-generator';folder=Path(args[2]).resolve() if len(args)>2 else assets/'sources/objects/terran/screen-generator/refined'
source=folder/('screen-generator.blend' if (folder/'screen-generator.blend').exists() else 'model.blend');glb=folder/('screen-generator.glb' if (folder/'screen-generator.glb').exists() else 'model.glb')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((baseline/'model.json').read_text());names=sum(model['components'].values(),[]);assert len(names)==113
def signature(ob):
 d=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={u.name:[list(p.uv) for p in u.data] for u in ob.data.uv_layers},materials=[m.name for m in ob.data.materials],matrix=[list(r) for r in ob.matrix_basis],parent=ob.parent.name if ob.parent else None)
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(baseline/'screen-generator.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();expected={n:signature(bpy.data.objects[n]) for n in names}
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert {n:signature(bpy.data.objects[n]) for n in names}==expected
assert sha(glb)==sha(baseline/'screen-generator.glb')
deps=bpy.context.evaluated_depsgraph_get();edges=[];volumes={};seam_checks={}
for name in names:
 ob=bpy.data.objects[name];raw=bmesh.new();raw.from_mesh(ob.data);raw.free()
 ev=ob.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
 before=sum(not e.is_manifold for e in bm.edges);vertices_before=len(bm.verts)
 if before:
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 bm.normal_update()
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
nodes=names+['ScreenResearchRoot'];poses={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();poses[f]={n:bpy.data.objects[n].matrix_world.copy() for n in nodes}

assert max(abs(poses[1]['ScreenResearchRoot'][i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))<1e-6
assert max(abs(poses[1]['ScreenResearchRoot'][i][j]-poses[16]['ScreenResearchRoot'][i][j]) for i in range(4) for j in range(4))>.5
assert max(abs(poses[1]['ScreenResearchRoot'][i][j]-poses[61]['ScreenResearchRoot'][i][j]) for i in range(4) for j in range(4))<1e-5
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene;assert len([o for o in s.objects if o.type=='MESH'])==113;maximum=0
for f in poses:
 s.frame_set(f);bpy.context.view_layer.update()
 for n,m in poses[f].items():maximum=max(maximum,max(abs(bpy.data.objects[n].matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)))
assert maximum<1e-4
report=dict(source_sha256=sha(source),glb_sha256=sha(glb),preserved_research_meshes=113,preserved_signatures=expected,colour_glb_unchanged=True,evaluated_closed_positive_meshes=volumes,wire_components=wire,wire_segments=sum(x['segments'] for x in wire.values()),actual_evaluated_edge_correspondence=True,all61_import_pose_max_error=maximum,gameplay_root_identity=True,root_turntable_verified=True,gameplay_pose_frame=1,limitations=['Disable research root turntable in gameplay. Mount/world scale require client checks; exact hidden construction remains approximate.'])
report['topology_seam_checks']=seam_checks;report['three_tip_balls_verified']=sum(n.startswith('Research polarity suppressor ball ') for n in names)==3;report['three_oscillators_verified']=sum(n.startswith('Research phase oscillator ') for n in names)==3;assert report['three_tip_balls_verified'] and report['three_oscillators_verified'];report['native_loop_closure_verified']=True
(out/'shared-geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SCREEN_SHARED_GEOMETRY_VERIFIED',report['wire_segments'],maximum)
