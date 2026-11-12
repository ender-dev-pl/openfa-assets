"""PM10/ST29 shared missile: six physical pods and four guidance fins."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]).resolve();base=Path(args[1]).resolve();textures=Path(args[2]).resolve();out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='4b9ce515dd8d97644d7ec457d7d8fef73856c0d99b9006c4106b09a6a3c556a2'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects.new('WarpGeneratorRoot',None);s.collection.objects.link(root)
old=[o for o in s.objects if o.type=='MESH'];assert len(old)==41
preserved=[];removed=[]
for ob in old:
 if ob.name.startswith('Warp Generator copper connector '):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 else:ob.parent=root;preserved.append(ob.name)
assert len(preserved)==37 and len(removed)==4
added=[];ducts=[];monitors=[]
def ellipsoid(name,location,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=location);ob=bpy.context.object;ob.name=name;ob.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.parent=root;ob.data.materials.append(material)
 ob.data.uv_layers.active.name='Authored box wear'
 for p in ob.data.polygons:p.use_smooth=True
 added.append(ob);return ob
for i in range(4):
 angle=i*math.pi/2;x=.32*math.cos(angle);z=.32*math.sin(angle)
 ducts.append(ellipsoid(f'Monitored energy duct {i+1}',(x,.225,z),(.10,.25,.10),bpy.data.materials['Warp Generator | worn copper connectors']))
 monitors.append(ellipsoid(f'Energy flow monitoring circuit {i+1}',(.23*math.cos(angle),-.91,.23*math.sin(angle)),(.065,.10,.065),bpy.data.materials['Warp Generator | worn pale shell alloy']))
monitors.append(ellipsoid('Energy flow monitoring central circuit',(0,-.985,0),(.11,.12,.11),bpy.data.materials['Warp Generator | worn pale shell alloy']))
roles=['chassis','warp-field-generator','flux-capacitor-and-energy-ducts','energy-flow-monitoring'];parts={r:[] for r in roles}
for ob in [o for o in s.objects if o.type=='MESH']:
 if ob in monitors:role='energy-flow-monitoring'
 elif ob in ducts or ob.name.startswith(('Warp Generator rounded module','Warp Generator connector sleeve','Warp Generator yellow band','Warp Generator rear ')):role='flux-capacitor-and-energy-ducts'
 elif ob.name.startswith(('Warp Generator flared dome','Warp Generator dome sector','Warp Generator front ')):role='warp-field-generator'
 else:role='chassis'
 parts[role].append(ob)
meshes=[ob for obs in parts.values() for ob in obs];assert len(meshes)==46
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
target=Vector((0,0,0));s.camera.location=(7,-11,5.6);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=3.4
bpy.ops.wm.save_as_mainfile(filepath=str(out/'warp-generator.blend'));s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True);export_solid(root,meshes,out/'warp-generator.glb')
phases=[dict(component=r,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=target,closeup_rotation_euler=rotation,ortho_scale=scale) for i,(r,target,rotation,scale) in enumerate(zip(roles[1:],[[0,-.78,0],[0,.47,0],[0,-.99,0]],[[1.05,0,0],[0,0,math.pi/2],[.5,0,0]],[1.8,1.65,.85]))]
d=dict(id='scitek:warp-generator',object_id='openfa:warp-generator',legacy_index=33,components={r:[o.name for o in obs] for r,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,0],whole_information_rotation_euler=[.04,0,math.pi/2],whole_information_ortho_scale=3.25,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,removed_source_meshes=removed,new_presentation_meshes=[o.name for o in added],source_transform_refinements={},shared_root_scale=[1,1,1],authoring_texture_inputs={},wire_geometry_contract='Every technical segment is an evaluated shared-solid edge.',limitations=['Existing revision1 retained except four straight copper connectors replaced with rounded ducts from PH09/ST33. Four peripheral monitoring nodes and one central node added from ST33. Exact hidden circuit depth, dimensions and mount calibration are authored approximations; source comparison and anatomy/import verification required before publication. Existing packed wear maps reused for new surfaces.'])
(out/'model.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print('WARP_GENERATOR_DRAFT_READY',len(meshes))
