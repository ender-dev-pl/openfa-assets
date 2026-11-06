"""PB18/ST18: stationary armour base and swivelling egg-shaped photon barrel."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='7dd961ea8f26c38c4a8b4fcc0ded0b43fc1cb5762c7f0b1775739f7c54259126'
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
names=['Pedestal foundation joint','Azimuth race flange','Pedestal systems hatch dark gasket','Pedestal systems hatch lid','Pedestal systems hatch rim','Pedestal systems hatch locking handle']
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=list(names)
root=bpy.data.objects.new('PhotonResearchRoot',None);s.collection.objects.link(root);root.scale.z=1.15
head=bpy.data.objects.new('PhotonWeaponAzimuth',None);s.collection.objects.link(head);head.parent=root
parts={k:[] for k in ['chassis','strengthened-photon-barrel','elastoplastic-fixed-base','armoured-tracking-receiver']};meshes=[]
for ob in dst.objects:
 assert ob is not None
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
 parts['armoured-tracking-receiver' if ob.name.startswith('Pedestal systems hatch') else 'elastoplastic-fixed-base'].append(ob)
preserved=[ob.name for ob in meshes]
copper=g.material('Research worn pink copper elastoplastic',(.43,.25,.21),.56,.57)
bronze=g.material('Research handled golden photon casing',(.42,.34,.20),.58,.49)
dark=g.material('Research dark joint and bore',(.035,.026,.022),.3,.68)
for mat in [copper,bronze,dark]:
 for node in mat.node_tree.nodes:
  if node.type=='BUMP':node.inputs['Distance'].default_value=.002;node.inputs['Strength'].default_value=.10
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=78
def add(ob,role):
 ob.parent=head if role=='strengthened-photon-barrel' else root;meshes.append(ob);parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None,role='strengthened-photon-barrel'):return add(g.tube(n,a,b,r,mat,r2),role)
def lathe(n,profile,mat,role,segments=48):
 v=[(rad*math.cos(i*math.tau/segments),rad*math.sin(i*math.tau/segments),z) for z,rad in profile for i in range(segments)]
 f=[tuple(reversed(range(segments)))]+[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(profile)-1) for i in range(segments)]+[tuple((len(profile)-1)*segments+i for i in range(segments))]
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for face in data.polygons:face.use_smooth=True
 return add(ob,role)
lathe('Research rounded elastoplastic armour',[(0,.96),(.06,1),(.20,.98),(.40,.89),(.63,.71),(.80,.45),(.82,.40)],copper,'elastoplastic-fixed-base')
for z,r in [(.10,.994),(.42,.882),(.75,.54)]:
 lathe('Research armour horizontal seam',[(z-.008,r),(z+.008,r)],dark,'elastoplastic-fixed-base')
# Cup supports the independent weapon without changing the fixed base.
lathe('Research swivelling weapon cup',[(.81,.39),(.94,.43),(1.18,.38),(1.18,.34),(.94,.36),(.87,.32)],copper,'chassis')
egg=add(g.uv('Research strengthened egg barrel',(0,-.035,1.40),(.33,.32,.53),bronze),'strengthened-photon-barrel');egg.rotation_euler.x=math.radians(32)
axis=Vector((0,-math.sin(math.radians(32)),math.cos(math.radians(32))))
centre=Vector((0,-.035,1.40));a=centre+axis*.43;b=centre+axis*.78
tube('Research tapered photon nozzle',tuple(a),tuple(b),.13,bronze,.075)
tube('Research dark photon aperture',tuple(b),tuple(b+axis*.006),.053,dark)
tube('Research slim barrel indicator',(-.20,-.10,1.64),(-.20,-.32,2.04),.006,bronze)
# Barrel casing seam is a narrow structural strap, not a texture overlay.
for sign in [-1,1]:tube('Research barrel lower trunnion',(sign*.29,.02,1.17),(sign*.34,.02,1.17),.10,copper)
head.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:head.rotation_euler.z=-(f-1)*math.tau/60;head.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in head.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
rig=[]
for f in range(1,61):
 s.frame_set(f);bpy.context.view_layer.update();rig.append(dict(frame=f-1,mesh_root_matrices={ob.name:[v for row in (root.matrix_world.inverted()@ob.matrix_world) for v in row] for ob in parts['strengthened-photon-barrel']}))
s.frame_set(1);bpy.context.view_layer.update()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);wires={}
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
  for edge in bm.edges:
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[(root.matrix_world.inverted()@ob.matrix_world)@v.co for v in edge.verts];spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
  bm.free()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';target=Vector((0,0,1.20));g.camera.location=(4,-10,5.3);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.0;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'photon-turret.blend'));export_solid(root,meshes,out/'photon-turret.glb')
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
normal=bpy.data.objects['Pedestal systems hatch lid'].matrix_world.to_3x3().inverted().transposed()@Vector((0,0,1));receiver_pose=list(normal.rotation_difference(Vector((0,-12,.15)).normalized()).to_euler('XYZ'))
phases=[]
for i,role in enumerate(['strengthened-photon-barrel','elastoplastic-fixed-base','armoured-tracking-receiver']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,-.10,1.48],[0,0,.38],[.55,-.83,.44]][i],closeup_rotation_euler=[[0,0,.90],[0,0,0],receiver_pose][i],ortho_scale=[1.65,2.30,.60][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:photon-turret',legacy_index=18,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,1],whole_information_rotation_euler=[.12,0,.25],whole_information_ortho_scale=3.5,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],limitations=['Six selected PB18 mesh geometries, UVs and material slots retained. New egg barrel, cup and rounded pink armour interpreted from actual PB18/ST18; hidden geometry and exact materials approximate.']),indent=2)+'\n')
(out/'solid-animation-timeline.json').write_text(json.dumps(dict(frame_count=60,fps=15,root=root.name,body_turntable=False,root_scale=list(root.scale),mechanism='PhotonWeaponAzimuth',animated_mesh_nodes=list(rig[0]['mesh_root_matrices']),bind_root_matrices=rig[0]['mesh_root_matrices'],format='Absolute row-major4x4 matrices, Blender column-vector math/Z-up; GLB hierarchy authoritative.',timeline=rig,source_blend_sha256=hashlib.sha256((out/'photon-turret.blend').read_bytes()).hexdigest(),source_glb_sha256=hashlib.sha256((out/'photon-turret.glb').read_bytes()).hexdigest()),separators=(',',':'))+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('PHOTON_VARIANTS_READY',len(meshes))
