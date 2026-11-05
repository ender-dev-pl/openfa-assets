"""Preserve the articulated source, validate frozen diagram edges and imported motion."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix,Vector,kdtree
args=sys.argv[sys.argv.index('--')+1:];assets,out=map(lambda p:Path(p).resolve(),args[:2]);out.mkdir(parents=True,exist_ok=True)
baseline=assets/'sources/ui/scitek/photon-turret';folder=Path(args[2]).resolve() if len(args)>2 else assets/'sources/objects/terran/photon-turret/refined'
source=folder/('photon-turret.blend' if (folder/'photon-turret.blend').exists() else 'model.blend');glb=folder/('photon-turret.glb' if (folder/'photon-turret.glb').exists() else 'model.glb')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=json.loads((baseline/'model.json').read_text());names=sum(model['components'].values(),[]);assert len(names)==17
def signature(ob,materials=True):
 d=dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={u.name:[list(p.uv) for p in u.data] for u in ob.data.uv_layers},materials=[m.name for m in ob.data.materials],matrix=[list(r) for r in ob.matrix_basis],parent=ob.parent.name if ob.parent else None)
 if not materials:d.pop('materials')
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
handle='Pedestal systems hatch locking handle';plate='Pedestal systems hatch lid';lens='Research armoured tracking sensor lens';retained=[n for n in names if n not in [handle,plate]];assert len(retained)==15
bpy.ops.wm.open_mainfile(filepath=str(baseline/'photon-turret.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();expected={n:signature(bpy.data.objects[n]) for n in retained};plate_geometry=signature(bpy.data.objects[plate],False)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert {n:signature(bpy.data.objects[n]) for n in retained}==expected
assert signature(bpy.data.objects[plate],False)==plate_geometry and handle not in bpy.data.objects
model=json.loads((folder/'model.json').read_text());names=sum(model['components'].values(),[]);assert len(names)==17 and model['components']['armoured-tracking-receiver']==[lens]
assert sha(glb)!=sha(baseline/'photon-turret.glb')
assert bpy.data.objects[plate].data.materials[0]==bpy.data.objects['Research rounded elastoplastic armour'].data.materials[0]
def inside(ob,world_point):
 start=ob.matrix_world.inverted()@Vector(world_point);direction=Vector((1,.137,.293)).normalized();hits=0
 for _ in range(100):
  ok,p,n,i=ob.ray_cast(start,direction)
  if not ok:return hits%2==1
  hits+=1;start=p+direction*1e-5
 raise AssertionError('Ray did not terminate')
witness=model['receiver_refinement']['shared_interior_witness'];assert inside(bpy.data.objects[plate],witness) and inside(bpy.data.objects[lens],witness)
assert any(n.type=='TEX_NOISE' for n in bpy.data.objects[lens].data.materials[0].node_tree.nodes)
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
nodes=names+['PhotonResearchRoot','PhotonWeaponAzimuth'];poses={}
for f in range(1,62):
 s.frame_set(f);bpy.context.view_layer.update();poses[f]={n:bpy.data.objects[n].matrix_world.copy() for n in nodes}
assert all(poses[f]['Research rounded elastoplastic armour']==poses[1]['Research rounded elastoplastic armour'] for f in poses)
fixed=[n for n in names if n not in model['components']['strengthened-photon-barrel']]
assert len(fixed)==11 and all(poses[f][n]==poses[1][n] for f in poses for n in fixed)
assert max(abs(poses[1]['PhotonResearchRoot'][i][j]-Matrix.Diagonal((1,1,1.15,1))[i][j]) for i in range(4) for j in range(4))<1e-6
assert max(abs(poses[1]['PhotonWeaponAzimuth'][i][j]-poses[16]['PhotonWeaponAzimuth'][i][j]) for i in range(4) for j in range(4))>.5
assert max(abs(poses[1]['PhotonWeaponAzimuth'][i][j]-poses[61]['PhotonWeaponAzimuth'][i][j]) for i in range(4) for j in range(4))<1e-5
rig_path=folder/'solid-animation-timeline.json'
if not rig_path.is_file():rig_path=baseline/'solid-animation-timeline.json'
rig=json.loads(rig_path.read_text());assert rig['source_blend_sha256']==sha(source) and rig['source_glb_sha256']==sha(glb) and rig['body_turntable'] is False
for f in range(1,61):
 inverse=poses[f]['PhotonResearchRoot'].inverted()
 for n,values in rig['timeline'][f-1]['mesh_root_matrices'].items():assert max(abs(a-b) for a,b in zip([v for row in inverse@poses[f][n] for v in row],values))<1e-5
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(glb));s=bpy.context.scene;assert len([o for o in s.objects if o.type=='MESH'])==17;maximum=0
for f in poses:
 s.frame_set(f);bpy.context.view_layer.update()
 for n,m in poses[f].items():maximum=max(maximum,max(abs(bpy.data.objects[n].matrix_world[i][j]-m[i][j]) for i in range(4) for j in range(4)))
assert maximum<1e-4
report=dict(source_sha256=sha(source),glb_sha256=sha(glb),preserved_research_meshes=15,preserved_signatures=expected,recoloured_plate_geometry_uv_bind_preserved=True,plate_geometry_uv_bind_signature=plate_geometry,removed_inferred_handle=handle,receiver_lens=lens,shared_lens_plate_interior_witness=witness,receiver_highlight_only_lens=True,colour_glb_unchanged=False,evaluated_closed_positive_meshes=volumes,wire_components=wire,wire_segments=sum(x['segments'] for x in wire.values()),actual_evaluated_edge_correspondence=True,all61_import_pose_max_error=maximum,gameplay_root_matches_declared_scale=True,root_scale=[1,1,1.15],fixed_base_and_moving_head_verified=True,all11_fixed_meshes_verified=True,native_head_loop_closure_verified=True,solid_matrix_timeline_verified=True,technical_wire_frozen_head_frame=1,limitations=['Head aiming and gameplay scale require client checks. Preserve rootZscale1.15; technical wires use the initial weapon pose. Lens size and hidden construction remain authored approximations from PB18/ST18.'])
report['topology_seam_checks']=seam_checks
(out/'shared-geometry-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PHOTON_SHARED_GEOMETRY_VERIFIED',report['wire_segments'],maximum)
