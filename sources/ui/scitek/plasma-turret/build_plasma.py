"""PB17/ST19 research variant with fixed power base and head-mounted stereo sensors."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='ed9f99c84696aacde6dc3d566cef3c980acb6f1064533393c6dec214bf48c38b'
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
names=['Pedestal foundation joint','Azimuth race flange','Weapon barrel','Weapon dark bore','Barrel heat-sink collar','Barrel heat-sink collar.001','Barrel heat-sink collar.002','Barrel heat-sink collar.003','Muzzle locking ring','Rangefinder lens']
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=list(names)
root=bpy.data.objects.new('PlasmaResearchRoot',None);s.collection.objects.link(root);root.scale.z=1.15
head=bpy.data.objects.new('PlasmaWeaponAzimuth',None);s.collection.objects.link(head);head.parent=root;head.location.z=1.08
parts={k:[] for k in ['chassis','water-cooled-plasma-delivery','tracking-and-ranging-sensors','armoured-power-base']};meshes=[]
for ob in dst.objects:
 assert ob is not None
 s.collection.objects.link(ob);meshes.append(ob)
 if ob.name in names[:2]:ob.parent=root;parts['chassis' if ob.name=='Pedestal foundation joint' else 'armoured-power-base'].append(ob)
 elif ob.name=='Rangefinder lens':
  ob.parent=head;ob.location=(.48,-.40,.12);ob.rotation_euler=(math.pi/2,0,0);ob.scale=(2.5,2.5,2.5);parts['tracking-and-ranging-sensors'].append(ob)
 else:
  ob.parent=head;ob.matrix_basis=Matrix.Translation((0,-.10,.25))@Matrix.Diagonal((.55,.6,.6,1))@ob.matrix_basis;parts['water-cooled-plasma-delivery'].append(ob)
preserved=[ob.name for ob in meshes]
lens=bpy.data.objects['Rangefinder lens'];other=lens.copy();other.data=lens.data.copy();other.name='Research second ranging lens';s.collection.objects.link(other);other.location.x=-.48;meshes.append(other);parts['tracking-and-ranging-sensors'].append(other)
copper=g.material('Research worn copper power armour',(.43,.23,.19),.52,.57)
gold=g.material('Research handled gold plasma canopy',(.43,.32,.16),.57,.51)
dark=g.material('Research grime at power joints',(.035,.025,.022),.3,.67)
for mat in [copper,gold,dark]:
 for node in mat.node_tree.nodes:
  if node.type=='BUMP':node.inputs['Distance'].default_value=.002;node.inputs['Strength'].default_value=.10
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=78
def add(ob,role):
 ob.parent=root if role in ['chassis','armoured-power-base'] else head
 if ob.parent==head:ob.location.z-=head.location.z
 meshes.append(ob);parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None,role='water-cooled-plasma-delivery'):return add(g.tube(n,a,b,r,mat,r2),role)
def lathe(n,profile,mat,role,segments=48):
 v=[(rad*math.cos(i*math.tau/segments),rad*math.sin(i*math.tau/segments),z) for z,rad in profile for i in range(segments)]
 f=[tuple(reversed(range(segments)))]+[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(profile)-1) for i in range(segments)]+[tuple((len(profile)-1)*segments+i for i in range(segments))]
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for face in data.polygons:face.use_smooth=True
 return add(ob,role)
lathe('Research armoured plasma power base',[(0,.96),(.06,1),(.20,.98),(.43,.91),(.64,.74),(.80,.46),(.83,.40)],copper,'armoured-power-base')
for z,r in [(.10,.994),(.42,.916),(.75,.55)]:lathe('Research power base horizontal seam',[(z-.006,r),(z+.006,r)],dark,'armoured-power-base')
lathe('Research armoured azimuth elevation motor',[(.81,.29),(1.02,.29),(1.12,.22)],copper,'armoured-power-base')
add(g.uv('Research plasma generator housing',(0,-.08,1.24),(.30,.25,.20),copper),'water-cooled-plasma-delivery')
N=48;R=10;v=[]
for j in range(R+1):
 theta=j*math.pi/(2*R)
 for i in range(N):
  a=i*math.tau/N;v.append((.70*math.sin(theta)*math.cos(a),-.05+.50*math.sin(theta)*math.sin(a),1.26+.32*math.cos(theta)))
f=[(j*N+i,(j+1)*N+i,(j+1)*N+(i+1)%N,j*N+(i+1)%N) for j in range(R) for i in range(N)]+[tuple(reversed([R*N+i for i in range(N)]))]
data=bpy.data.meshes.new('Research shallow canopy');data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new('Research shallow golden plasma canopy',data);s.collection.objects.link(ob);ob.data.materials.append(gold)
for face in data.polygons:face.use_smooth=True
add(ob,'water-cooled-plasma-delivery')
bpy.ops.mesh.primitive_torus_add(major_radius=1,minor_radius=.012,major_segments=48,minor_segments=8,location=(0,-.05,1.26));ob=bpy.context.object;ob.name='Research canopy rim seam';ob.scale=(.70,.50,1);ob.data.materials.append(dark);add(ob,'water-cooled-plasma-delivery')
for x in [-.48,.48]:
 tube('Research stereo sensor arm',(0,-.24,1.11),(x,-.34,1.20),.025,copper,role='tracking-and-ranging-sensors')
 tube('Research stereo sensor armoured housing',(x,-.33,1.20),(x,-.40,1.20),.115,copper,role='tracking-and-ranging-sensors')
head.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:head.rotation_euler.z=math.pi-(f-1)*math.tau/60;head.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in head.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
rig=[]
for f in range(1,61):
 s.frame_set(f);bpy.context.view_layer.update();rig.append(dict(frame=f-1,mesh_root_matrices={ob.name:[v for row in (root.matrix_world.inverted()@ob.matrix_world) for v in row] for ob in meshes if ob.parent==head}))
s.frame_set(1);bpy.context.view_layer.update()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);wires={}
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  if role=='tracking-and-ranging-sensors':bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
  bm.normal_update()
  for edge in bm.edges:
   if role!='tracking-and-ranging-sensors' and len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[(root.matrix_world.inverted()@ob.matrix_world)@v.co for v in edge.verts];spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
  bm.free()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';target=Vector((0,0,1));g.camera.location=(4,-10,5.3);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=2.8;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'plasma-turret.blend'));export_solid(root,meshes,out/'plasma-turret.glb')
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(['water-cooled-plasma-delivery','tracking-and-ranging-sensors','armoured-power-base']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,.14,1.43],[-.48,.40,1.20],[0,0,.55]][i],closeup_rotation_euler=[[0,0,math.pi],[0,0,math.pi],[0,0,0]][i],ortho_scale=[1.85,.55,2.50][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:plasma-turret',legacy_index=19,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,.9],whole_information_rotation_euler=[.12,0,.25],whole_information_ortho_scale=3.2,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],limitations=['Ten selected PB17 meshes retain geometry/UV/material slots with research-only transform adaptations. Second ranging lens duplicates existing geometry. Shallow canopy, generator and copper base are authored interpretations.']),indent=2)+'\n')
(out/'solid-animation-timeline.json').write_text(json.dumps(dict(frame_count=60,fps=15,root=root.name,root_scale=list(root.scale),body_turntable=False,mechanism=head.name,animated_mesh_nodes=list(rig[0]['mesh_root_matrices']),bind_root_matrices=rig[0]['mesh_root_matrices'],format='Absolute row-major4x4 matrices, Blender column-vector math/Z-up; GLB hierarchy authoritative.',timeline=rig,source_blend_sha256=hashlib.sha256((out/'plasma-turret.blend').read_bytes()).hexdigest(),source_glb_sha256=hashlib.sha256((out/'plasma-turret.glb').read_bytes()).hexdigest()),separators=(',',':'))+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('PLASMA_VARIANTS_READY',len(meshes))
