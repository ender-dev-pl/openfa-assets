"""Read-only source retention, actual solid-edge diagrams and all imported poses."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,kdtree,Matrix
args=sys.argv[sys.argv.index('--')+1:];assets,out=map(lambda p:Path(p).resolve(),args[:2]);out.mkdir(parents=True,exist_ok=True)
folder=Path(args[2]).resolve() if len(args)>2 else assets/'sources/objects/terran/mega-missile/refined';base=assets/'sources/docs/assets/reconstruction/missiles/terran/mega/model.blend';source=folder/('mega-missile.blend' if (folder/'mega-missile.blend').exists() else 'model.blend');glb=folder/('mega-missile.glb' if (folder/'mega-missile.glb').exists() else 'model.glb');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sig(ob):
 d=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers},matrix=[list(row) for row in ob.matrix_basis],materials=[m.name for m in ob.data.materials]);return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(base));expected={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Mega ') and not any(token in o.name for token in ['thick copper lower panel','hollow lower casing','hollow copper nozzle','annular nozzle support','recessed throat','cylindrical pressure casing'])};packed={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file};assert len(expected)==56
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert {n:sig(bpy.data.objects[n]) for n in expected}==expected
assert all(any(im.name==name and im.packed_file and hashlib.sha256(im.packed_file.data).hexdigest()==digest for im in bpy.data.images) for name,digest in packed.items())
names=[n for group in json.loads((folder/'model.json').read_text())['components'].values() for n in group];assert len(names)==65
import bmesh
closed={}
for name in names:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name;closed[name]=bm.calc_volume(signed=True);assert closed[name]>0;bm.free()
edges=[];deps=bpy.context.evaluated_depsgraph_get()
for name in names:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(deps);mesh=ev.to_mesh();vs=[ob.matrix_world@v.co for v in mesh.vertices];edges.extend((vs[e.vertices[0]],vs[e.vertices[1]]) for e in mesh.edges);ev.to_mesh_clear()
tree=kdtree.KDTree(len(edges))
for i,(a,b) in enumerate(edges):tree.insert((a+b)*.5,i)
tree.balance();wire={}
for ob in s.objects:
 if not ob.name.endswith(' technical wire'):continue
 maximum=0
 for spline in ob.data.splines:
  assert len(spline.points)==2;a,b=[ob.matrix_world@Vector(p.co[:3]) for p in spline.points];errors=[]
  for _,index,_ in tree.find_range((a+b)*.5,2e-5):
   c,d=edges[index];errors.append(min(max((a-c).length,(b-d).length),max((a-d).length,(b-c).length)))
  assert errors and min(errors)<2e-5,(ob.name,a,b);maximum=max(maximum,min(errors))
 wire[ob.name]=dict(segments=len(ob.data.splines),maximum_edge_endpoint_error=maximum)
assert len(wire)==4
poses={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();poses[f]={n:bpy.data.objects[n].matrix_world.copy() for n in names}
s.frame_set(1);assert max(abs(bpy.data.objects['MegaResearchRoot'].matrix_world[i][j]-Matrix.Identity(4)[i][j]) for i in range(4) for j in range(4))<1e-6
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene;assert len([o for o in s.objects if o.type=='MESH'])==65;maximum=0
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update()
 for name,pose in poses[f].items():maximum=max(maximum,max(abs(bpy.data.objects[name].matrix_world[i][j]-pose[i][j]) for i in range(4) for j in range(4)))
assert maximum<1e-4
report=dict(base_sha256=sha(base),source_sha256=sha(source),glb_sha256=sha(glb),preserved_base_meshes=56,preserved_signatures=expected,preserved_packed_images=packed,all_diagram_segments_are_evaluated_solid_edges=True,wire_components=wire,wire_segment_count=sum(x['segments'] for x in wire.values()),all61_native_import_pose_max_error=maximum,gameplay_pose_frame=1,gameplay_root_matrix_identity=True,closed_native_meshes=closed,limitations=['Wire display omits some physical edges and uses authored semantic regions; no invented diagram edges. Lower neck is authored from ST13; separate profile verification checks the scoped edit. Hidden geometry and threefold fin layout remain interpretations.'])
(out/'shared-geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('MEGA_SHARED_GEOMETRY_VERIFIED',report['wire_segment_count'],maximum)
