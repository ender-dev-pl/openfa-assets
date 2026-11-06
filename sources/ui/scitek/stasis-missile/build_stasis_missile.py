"""PM10/ST29 shared missile: six physical pods and four guidance fins."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]).resolve();base=Path(args[1]).resolve();textures=Path(args[2]).resolve();out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='037c980ff92ed970be4ea7bdab33e26f881d445d39cd89e76a66cad5c0e9e897'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects.new('StasisMissileRoot',None);s.collection.objects.link(root)
old=[o for o in s.objects if o.type=='MESH'];assert len(old)==28
removed=[];preserved=[]
for ob in old:
 if ob.name.startswith(('Stasis conformal maroon round marking','Stasis open tail frame brace','Stasis lower frame anchor','Stasis mount captive fastener')):
  removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 else:ob.parent=root;preserved.append(ob.name)
assert len(preserved)==12 and len(removed)==16
body=bpy.data.objects['Stasis straight green pressure casing'];preserved.remove(body.name)
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(0,0,4.22),plane_no=(0,0,1),clear_inner=False,clear_outer=False);bm.to_mesh(body.data);bm.free()
texture_inputs={}
def painted(name,file,base_colour):
 path=textures/file;texture_inputs[file]=hashlib.sha256(path.read_bytes()).hexdigest();image=bpy.data.images.load(str(path));image.pack()
 mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*base_colour,1);bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.38;bs.inputs['Roughness'].default_value=.61
 node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);return mat
pod_mat=painted('Stasis Refined | worn maroon pods','pod-maroon.png',(.28,.045,.10));fin_mat=painted('Stasis Refined | worn green fins','fin-green.png',(.045,.17,.11))
pods=[];fins=[]
for i in range(6):
 angle=-math.pi/2+i*math.tau/6;bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(.47*math.cos(angle),.47*math.sin(angle),1.35));ob=bpy.context.object;ob.name=f'Tachyon dispersion pod {i+1}';ob.scale=(.19,.19,.20);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.parent=root;ob.data.materials.append(pod_mat)
 for p in ob.data.polygons:p.use_smooth=True
 for loop in ob.data.uv_layers.active.data:loop.uv.x=(loop.uv.x+i/6)%1
 pods.append(ob)
profile=[(.28,1.03),(.56,1.03),(.56,.28),(.51,.18),(.46,.20),(.46,.33),(.32,.72)]
for i in range(4):
 angle=i*math.pi/2;co,si=math.cos(angle),math.sin(angle);n=len(profile)
 vertices=[(radial*co-tangent*si,radial*si+tangent*co,z) for tangent in [-.015,.015] for radial,z in profile]
 faces=[tuple(reversed(range(n))),tuple(n+j for j in range(n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 mesh=bpy.data.meshes.new(f'Guidance fin {i+1}');mesh.from_pydata(vertices,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 uv=mesh.uv_layers.new(name='Wear UV')
 for p in mesh.polygons:
  for li in p.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;radial=v.x*co+v.y*si;uv.data[li].uv=((radial-.28)/.28,(v.z-.18)/.85)
 ob=bpy.data.objects.new(f'Guidance fin {i+1}',mesh);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(fin_mat);fins.append(ob)
roles=['chassis','navigation-and-targeting','tachyon-dispersion-pods','main-thruster'];parts={r:[] for r in roles}
for ob in [o for o in s.objects if o.type=='MESH']:
 if ob in pods:role='tachyon-dispersion-pods'
 elif ob.name in ['Stasis rounded green head','Stasis pale upper band','Stasis small red nose cap','Stasis short nose pin']:role='navigation-and-targeting'
 elif ob.name in ['Stasis hollow red propulsion bell','Stasis annular nozzle flange','Stasis recessed throat']:role='main-thruster'
 else:role='chassis'
 parts[role].append(ob)
meshes=[ob for obs in parts.values() for ob in obs];assert len(meshes)==22
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0020;curve.bevel_resolution=0
 source_obs=obs+[body] if role=='navigation-and-targeting' else obs
 for ob in source_obs:
  ev=ob.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
  for edge in bm.edges:
   if edge.calc_length()<.008:continue
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_world@v.co for v in edge.verts]
   if ob==body:
    edge_role='navigation-and-targeting' if min(a.z,b.z)>=4.22-1e-5 else 'chassis'
    if role!=edge_role:continue
   sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();ev.to_mesh_clear()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s.render.resolution_x=360;s.render.resolution_y=480;s.render.film_transparent=True
target=Vector((0,0,3.2));s.camera.location=(7,-11,5.6);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=7.5
bpy.ops.wm.save_as_mainfile(filepath=str(out/'stasis-missile.blend'));s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True);export_solid(root,meshes,out/'stasis-missile.glb')
phases=[dict(component=r,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=t,closeup_rotation_euler=[0,0,0],ortho_scale=scale) for i,(r,t,scale) in enumerate(zip(roles[1:],[[0,0,5.4],[0,0,1.35],[0,0,.55]],[2.35,1.65,1.65]))]
d=dict(id='scitek:stasis-missile',object_id='openfa:stasis',legacy_index=29,components={r:[o.name for o in obs] for r,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,3.2],whole_information_rotation_euler=[.04,0,.20],whole_information_ortho_scale=7.4,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,removed_source_meshes=removed,new_presentation_meshes=[ob.name for ob in pods+fins],source_transform_refinements={},shared_root_scale=[1,1,1],authoring_texture_inputs=texture_inputs,wire_geometry_contract='Every technical segment is an evaluated shared-solid edge.',limitations=['Six physical dispersion pods replace four inferred flat markings, following ST29 and its explicit caption. Four broad guidance fins replace the former thin support-frame interpretation. Twelve retained source mesh/UV/material signatures and poses are unchanged. Exact hidden pod depths, fin profile, camera interpolation and runtime mounting are authored approximations at approximately80% visual correspondence. Newly authored pods/fins carry packed portable wear maps; existing parts are not retrofitted.'])
d['refined_source_meshes']=[body.name];d['new_presentation_meshes'].append(body.name)
d['diagram_edge_sources']={role:[ob.name for ob in obs]+([body.name] if role=='navigation-and-targeting' else []) for role,obs in parts.items()}
d['limitations'][0]=d['limitations'][0].replace('Twelve retained source mesh/UV/material signatures and poses are unchanged.','Eleven retained source mesh/UV/material signatures and poses are unchanged. The casing is subdivided at Z=4.22 without changing its profile; its actual upper/lower edges are assigned to navigation/chassis technical regions.')
(out/'model.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print('STASIS_MISSILE_READY',len(meshes))
