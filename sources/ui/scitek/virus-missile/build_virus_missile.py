"""PM10/ST29 shared missile: six physical pods and four guidance fins."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]).resolve();base=Path(args[1]).resolve();textures=Path(args[2]).resolve();out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='00f6936fdc5d739c9d74c70f982cf33838ffc6dcf1ac39600ffb8170a81d9f37'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects.new('VirusMissileRoot',None);s.collection.objects.link(root)
old=[o for o in s.objects if o.type=='MESH'];assert len(old)==23
preserved=[ob.name for ob in old]
for ob in old:ob.parent=root
texture_inputs={}
def painted(name,file,base_colour):
 path=textures/file;texture_inputs[file]=hashlib.sha256(path.read_bytes()).hexdigest();image=bpy.data.images.load(str(path));image.pack()
 mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*base_colour,1);bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.38;bs.inputs['Roughness'].default_value=.61
 node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);return mat

sensor_mat=painted('Virus Refined | worn violet resistance sensors','sensor-violet.png',(.16,.11,.23))
sensors=[]
for i in range(4):
 angle=-math.pi/2+i*math.pi/2
 bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.20,radius2=0,depth=.58,location=(.37*math.cos(angle),.37*math.sin(angle),.88))
 ob=bpy.context.object;ob.name=f'Atmospheric resistance sensor {i+1}';ob.parent=root;ob.data.materials.append(sensor_mat)
 for p in ob.data.polygons:p.use_smooth=len(p.vertices)==3
 sensors.append(ob)
roles=['chassis','binary-agent-pods','atmospheric-resistance-sensors','main-thrusters'];parts={r:[] for r in roles}
for ob in [o for o in s.objects if o.type=='MESH']:
 if ob in sensors:role='atmospheric-resistance-sensors'
 elif ob.name.startswith('Virus bronze side form'):role='binary-agent-pods'
 elif ob.name.startswith(('Virus family hollow red nozzle','Virus family recessed nozzle throat')):role='main-thrusters'
 else:role='chassis'
 parts[role].append(ob)
meshes=[ob for obs in parts.values() for ob in obs];assert len(meshes)==27
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
target=Vector((0,0,3.2));s.camera.location=(7,-11,5.6);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=7.5
bpy.ops.wm.save_as_mainfile(filepath=str(out/'virus-missile.blend'));s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True);export_solid(root,meshes,out/'virus-missile.glb')
phases=[dict(component=r,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=t,closeup_rotation_euler=[0,0,0],ortho_scale=scale) for i,(r,t,scale) in enumerate(zip(roles[1:],[[0,0,2.9],[0,0,.92],[0,0,.28]],[3.6,1.8,1.35]))]
d=dict(id='scitek:virus-missile',object_id='openfa:virus',legacy_index=32,components={r:[o.name for o in obs] for r,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,3.2],whole_information_rotation_euler=[.04,0,.20],whole_information_ortho_scale=7.4,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,removed_source_meshes=[],new_presentation_meshes=[ob.name for ob in sensors],source_transform_refinements={},shared_root_scale=[1,1,1],authoring_texture_inputs=texture_inputs,wire_geometry_contract='Every technical segment is an evaluated shared-solid edge.',limitations=['Existing revision2 geometry retained. Four pointed resistance sensors added from ST32 closeups; exact hidden placement and dimensions are inferred. Sensor visibility and skirt clearance require native/import visual review before publication.'])
(out/'model.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print('VIRUS_MISSILE_DRAFT_READY',len(meshes))
