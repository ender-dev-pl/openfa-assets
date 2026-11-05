"""Preserve the source, atomic scanners, physical-edge diagrams and imported poses."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,kdtree
args=sys.argv[sys.argv.index('--')+1:];assets,out=map(lambda p:Path(p).resolve(),args[:2]);out.mkdir(parents=True,exist_ok=True)
baseline=assets/'sources/ui/scitek/ore-teleporter';folder=Path(args[2]).resolve() if len(args)>2 else assets/'sources/objects/terran/ore-teleporter/refined'
source=folder/('ore-teleporter.blend' if (folder/'ore-teleporter.blend').exists() else 'model.blend');glb=folder/('ore-teleporter.glb' if (folder/'ore-teleporter.glb').exists() else 'model.glb')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((baseline/'model.json').read_text());names=sum(model['components'].values(),[]);assert len(names)==66
def signature(ob):
 d=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={u.name:[list(p.uv) for p in u.data] for u in ob.data.uv_layers},materials=[m.name for m in ob.data.materials],matrix=[list(r) for r in ob.matrix_basis],parent=ob.parent.name if ob.parent else None)
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(baseline/'ore-teleporter.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();retained=[n for n in names if n!='Tower seam.002'];expected={n:signature(bpy.data.objects[n]) for n in retained};assert len(expected)==65
seam=bpy.data.objects['Tower seam.002'];old_faces=[dict(points=[seam.data.vertices[i].co.copy() for i in p.vertices],uv={u.name:[u.data[i].uv.copy() for i in p.loop_indices] for u in seam.data.uv_layers},material=p.material_index,smooth=p.use_smooth) for p in seam.data.polygons];old_matrix=seam.matrix_basis.copy();old_parent=seam.parent.name;old_materials=[m.name for m in seam.data.materials]
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert {n:signature(bpy.data.objects[n]) for n in retained}==expected
seam=bpy.data.objects['Tower seam.002'];assert seam.matrix_basis==old_matrix and seam.parent.name==old_parent and [m.name for m in seam.data.materials]==old_materials
assert len(old_faces)==384 and len(seam.data.polygons)==386
face_error=0
for before,after in zip(old_faces,seam.data.polygons):
 assert len(before['points'])==len(after.vertices) and before['material']==after.material_index and before['smooth']==after.use_smooth
 candidates=[]
 for shift in range(len(after.vertices)):
  error=max((p-seam.data.vertices[after.vertices[(i+shift)%len(after.vertices)]].co).length for i,p in enumerate(before['points']))
  if error>=1e-6:continue
  uv_error=max((before['uv'][u.name][i]-u.data[after.loop_indices[(i+shift)%len(after.vertices)]].uv).length for u in seam.data.uv_layers for i in range(len(after.vertices))) if seam.data.uv_layers else 0
  if uv_error<1e-6:candidates.append(max(error,uv_error))
 assert candidates;face_error=max(face_error,min(candidates))
assert all(len(p.vertices)==8 for p in list(seam.data.polygons)[384:])
deps=bpy.context.evaluated_depsgraph_get();edges=[];volumes={};seam_checks={}
for name in names:
 ob=bpy.data.objects[name];raw=bmesh.new();raw.from_mesh(ob.data);raw_before=sum(not e.is_manifold for e in raw.edges)
 if raw_before:bmesh.ops.remove_doubles(raw,verts=list(raw.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(raw,edges=list(raw.edges),dist=1e-8)
 assert all(e.is_manifold for e in raw.edges),name;assert raw.calc_volume(signed=True)>0,name;raw.free()
 ev=ob.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
 before=sum(not e.is_manifold for e in bm.edges);vertices_before=len(bm.verts)
 if before:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8)
 assert all(e.is_manifold for e in bm.edges),name
 seam_checks[name]=dict(raw_nonmanifold_before=raw_before,raw_validation_only_weld_tolerance=1e-6 if raw_before else 0,raw_nonmanifold_after=0,nonmanifold_before=before,vertices_before=vertices_before,vertices_after=len(bm.verts),validation_only_weld_tolerance=1e-6 if before else 0,nonmanifold_after=0)
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
nodes=names+['OreResearchRoot'];poses={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();poses[f]={n:bpy.data.objects[n].matrix_world.copy() for n in nodes}

assert max(abs(poses[1]['OreResearchRoot'][i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))<1e-6
assert max(abs(poses[1]['OreResearchRoot'][i][j]-poses[16]['OreResearchRoot'][i][j]) for i in range(4) for j in range(4))>.5
assert max(abs(poses[1]['OreResearchRoot'][i][j]-poses[61]['OreResearchRoot'][i][j]) for i in range(4) for j in range(4))<1e-5
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene;assert len([o for o in s.objects if o.type=='MESH'])==66;maximum=0
for f in poses:
 s.frame_set(f);bpy.context.view_layer.update()
 for n,m in poses[f].items():maximum=max(maximum,max(abs(bpy.data.objects[n].matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)))
assert maximum<1e-4
report=dict(source_sha256=sha(source),glb_sha256=sha(glb),preserved_research_meshes=66,preserved_signatures=expected,colour_glb_unchanged=True,evaluated_closed_positive_meshes=volumes,wire_components=wire,wire_segments=sum(x['segments'] for x in wire.values()),actual_evaluated_edge_correspondence=True,all61_import_pose_max_error=maximum,gameplay_root_identity=True,root_turntable_verified=True,gameplay_pose_frame=1,limitations=['Disable research root turntable in gameplay. Mount/world scale require client checks; exact hidden construction remains approximate.'])
report['preserved_research_meshes']=65;report['colour_glb_unchanged']=False;report['partial_torus_repair']=dict(mesh='Tower seam.002',old_faces_preserved=384,added_octagonal_end_caps=2,maximum_existing_face_geometry_uv_error=face_error,existing_bind_materials_preserved=True)
report['topology_seam_checks']=seam_checks;report['atomic_scanner_count']=sum(n.startswith('Research atomic scanner ') for n in names);assert report['atomic_scanner_count']==3;report['native_loop_closure_verified']=True
(out/'shared-geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('ORE_SHARED_GEOMETRY_VERIFIED',report['wire_segments'],maximum)
