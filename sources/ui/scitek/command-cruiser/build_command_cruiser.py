"""PM10/ST29 shared missile: six physical pods and four guidance fins."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]).resolve();base=Path(args[1]).resolve();textures=Path(args[2]).resolve();out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='b2d5c1ba3176d8a945669588cce343894b1dd8a19dc216d961c3c33bf6ba5ea9'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects['PlacementRoot'];root.name='CommandCruiserRoot'
old=[o for o in s.objects if o.type=='MESH'];assert len(old)==76
preserved=[];removed=[]
for ob in old:
 if ob.name.startswith(('Command Cruiser raised aft block','Command Cruiser aft dark grille','Command Cruiser aft grille bar')):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 else:ob.parent=root;preserved.append(ob.name)
assert len(preserved)==67 and len(removed)==9
added=[];radar=[];pods=[];aux=[];texture_inputs={}
def wear_uv(ob,name='Authored box wear'):
 while ob.data.uv_layers:ob.data.uv_layers.remove(ob.data.uv_layers[0])
 uv=ob.data.uv_layers.new(name=name);points=[v.co for v in ob.data.vertices];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 for p in ob.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=tuple((v[i]-lo[i])/max(1e-8,hi[i]-lo[i]) for i in axes)
def bronze():
 path=textures/'auxiliary-bronze.png';texture_inputs[path.name]=hashlib.sha256(path.read_bytes()).hexdigest();im=bpy.data.images.load(str(path));im.pack();m=bpy.data.materials.new('Command Refined | worn ancillary exhaust bronze');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.78;bs.inputs['Roughness'].default_value=.66;tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);return m
bronze_mat=bronze();hull_mat=bpy.data.materials['Command Cruiser | worn violet hull'];red_mat=bpy.data.materials['Command Cruiser | worn red markings']
def lathe(name,profile,xy,mat):
 n=48;verts=[(xy[0]+rad*math.cos(i*math.tau/n),xy[1]+rad*math.sin(i*math.tau/n),z) for z,rad in profile for i in range(n)];faces=[]
 for row in range(len(profile)-1):
  for i in range(n):a=row*n+i;b=row*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 ob=bpy.data.objects.new(name,mesh);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);wear_uv(ob)
 for p in mesh.polygons:p.use_smooth=True
 added.append(ob);return ob
radar.append(lathe('Xradar pedestal',[(.27,0),(.27,.055),(.43,.055),(.43,0)],(0,1.36),hull_mat))
radar.append(lathe('Xradar circular sensor casing',[(.40,0),(.40,.32),(.48,.35),(.56,.30),(.62,.19),(.65,0)],(0,1.36),hull_mat))
for i,(x,z) in enumerate([(-.045,.91),(.035,.80)]):radar.append(lathe(f'Xradar antenna {i+1}',[(.59,0),(.59,.009),(z,.009),(z,0)],(x,1.36),hull_mat))
for side in [-1,1]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(side*.96,1.04,-.14));ob=bpy.context.object;ob.name=f'Subwing communication pod {side}';ob.scale=(.21,.62,.19);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.parent=root;ob.data.materials.append(red_mat);wear_uv(ob)
 for p in ob.data.polygons:p.use_smooth=True
 added.append(ob);pods.append(ob)
 pods.append(lathe(f'Lateral weapon hardpoint collar {side}',[(.0,.065),(.0,.10),(.05,.10),(.05,.065),(.0,.065)],(side*1.05,1.10),hull_mat))
from mathutils import Matrix
for i,z in enumerate([.25,-.45]):
 transform=Matrix.Translation(Vector((0,2.16,z)))@Matrix.Diagonal((.55,.90,.55,1))@Matrix.Translation(Vector((.30,-2.16,.10)))
 for source,label in [('Command Cruiser engine housing -1','housing'),('Command Cruiser exhaust -1','hollow exhaust'),('Command Cruiser exhaust throat -1','recessed throat')]:
  original=bpy.data.objects[source];ob=original.copy();ob.data=original.data.copy();s.collection.objects.link(ob);ob.name=f'Ancillary thruster {i+1} {label}';ob.parent=root;ob.matrix_world=transform@original.matrix_world
  if label=='hollow exhaust':ob.data.materials.clear();ob.data.materials.append(bronze_mat);wear_uv(ob,'Wear UV')
  added.append(ob);aux.append(ob)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,1.80,-.30));support=bpy.context.object;support.name='Ancillary lower thruster hull attachment';support.scale=(.18,.32,.16);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);support.parent=root;support.data.materials.append(hull_mat);wear_uv(support);added.append(support);aux.append(support)
roles=['chassis','xradar-sensor','subwing-communications','drive-thrusters'];parts={r:[] for r in roles}
for ob in [o for o in s.objects if o.type=='MESH']:
 if ob in radar:role='xradar-sensor'
 elif ob in pods or ob.name.startswith(('Command Cruiser outrigger wing','Command Cruiser red outrigger band','Command Cruiser outboard probe')):role='subwing-communications'
 elif ob in aux or ob.name.startswith(('Command Cruiser engine housing','Command Cruiser exhaust','Command Cruiser cooling rib')):role='drive-thrusters'
 else:role='chassis'
 parts[role].append(ob)
meshes=[ob for obs in parts.values() for ob in obs];assert len(meshes)==82
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0020;curve.bevel_resolution=0
 source_obs=obs
 for ob in source_obs:
  ev=ob.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
  for edge in bm.edges:
   if edge.calc_length()<.008:continue
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_world@v.co for v in edge.verts]
   sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();ev.to_mesh_clear()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s.render.resolution_x=360;s.render.resolution_y=480;s.render.film_transparent=True
target=Vector((0,-.3,0));s.camera.location=(7,-11,5.6);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=7.2
bpy.ops.wm.save_as_mainfile(filepath=str(out/'command-cruiser.blend'));s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True);export_solid(root,meshes,out/'command-cruiser.glb')
phases=[dict(component=r,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=target,closeup_rotation_euler=rotation,ortho_scale=scale) for i,(r,target,rotation,scale) in enumerate(zip(roles[1:],[[0,1.36,.52],[.96,1.04,-.05],[0,2.16,-.10]],[[.3,0,.15],[1.15,0,.3],[0,0,math.pi]],[1.45,1.8,1.45]))]
d=dict(id='scitek:command-cruiser',object_id='openfa:command-cruiser',legacy_index=35,components={r:[o.name for o in obs] for r,obs in parts.items()},phases=phases,whole_information_local_target=[0,-.3,0],whole_information_rotation_euler=[.6,0,.65],whole_information_ortho_scale=6.5,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,removed_source_meshes=removed,new_presentation_meshes=[o.name for o in added],source_transform_refinements={},shared_root_scale=[1,1,1],authoring_texture_inputs=texture_inputs,wire_geometry_contract='Every technical segment is an evaluated shared-solid edge.',limitations=['Revision1 retained except nine aft block/grille parts replaced with circular Xradar casing and antennas. Two subwing pod bodies and collars plus two smaller engine assemblies added from ST35. Exact hidden shapes/dimensions and mount calibration are authored. Source sockets remain under the renamed original PlacementRoot. Draft requires anatomy and source/runtime visual verification before publication.'])
(out/'model.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print('COMMAND_CRUISER_DRAFT_READY',len(meshes))
