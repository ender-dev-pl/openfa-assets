"""PB11/ST17 research assembly, reusing scoped existing Terran hardware."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='501a55a663ada193b6bb008f2717b0052997fa785892665d00c379099298d148'
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
names=['Foundation drum','Transfer ramp']+['Transfer ramp tread'+('.'+str(i).zfill(3) if i else '') for i in range(5)]+['Cylindrical tower.002','Tower seam.002','Tower crown.002']+['Transfer side tank clamp.'+str(i).zfill(3) for i in range(3,6)]
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=list(names)
root=bpy.data.objects.new('OreResearchRoot',None);s.collection.objects.link(root)
parts={k:[] for k in ['chassis','long-range-transceiver','atomic-scan-generators','data-throughput-supercomputer']}
meshes=[]
for ob in dst.objects:
 assert ob is not None
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
 role='data-throughput-supercomputer' if ob.name in names[7:] else 'chassis'
 parts[role].append(ob)
 if ob.name=='Foundation drum':ob.scale=(.68,.68,1.15)
 if ob.name.startswith('Transfer ramp'):ob.location.y+=.20
preserved=[ob.name for ob in meshes]
metal=g.material('Research used olive chamber',(.28,.29,.18),.48,.55)
trim=g.material('Research worn beige frame',(.46,.38,.22),.45,.58)
dishmat=g.material('Research used blue-grey antenna',(.25,.32,.36),.65,.44)
dark=g.material('Research recessed olive panels',(.12,.15,.10),.3,.64)
glow=g.material('Research scan chamber light',(.70,.72,.48),.2,.35)
bs=glow.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.70,.72,.48,1);bs.inputs['Emission Strength'].default_value=2.8
for mat in [metal,trim,dishmat,dark]:
 for node in mat.node_tree.nodes:
  if node.type=='BUMP':node.inputs['Distance'].default_value=.002;node.inputs['Strength'].default_value=.10
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=75
def add(ob,role='chassis'):
 ob.parent=root;meshes.append(ob);parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None,role='chassis'):return add(g.tube(n,a,b,r,mat,r2),role)
def lathe(n,profile,mat,role='chassis',segments=48):
 v=[(rad*math.cos(i*math.tau/segments),.15+rad*math.sin(i*math.tau/segments),z) for z,rad in profile for i in range(segments)]
 f=[tuple(reversed(range(segments)))]+[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(profile)-1) for i in range(segments)]+[tuple((len(profile)-1)*segments+i for i in range(segments))]
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for face in data.polygons:face.use_smooth=True
 return add(ob,role)
lathe('Research rounded ore scan chamber',[(.92,.12),(1.00,.30),(1.15,.38),(1.95,.39),(2.14,.34),(2.18,.24)],metal)
lathe('Research scan chamber crown',[(2.14,.34),(2.20,.35),(2.25,.25),(2.27,.05)],trim)
lathe('Research lower scan pedestal',[(.44,.42),(.52,.42),(.80,.20),(.89,.20),(.94,.17)],trim)
for i in range(20):
 a=i*math.tau/20
 tube('Research pedestal grille',(.36*math.cos(a),.15+.36*math.sin(a),.48),(.29*math.cos(a),.15+.29*math.sin(a),.83),.008,dark)
for i in range(6):
 a=i*math.tau/6;ob=g.uv('Research chamber inset oval',(.385*math.sin(a),.15-.385*math.cos(a),1.47),(.10,.024,.27),dark);ob.rotation_euler.z=a;add(ob)
for i in range(3):
 a=i*math.tau/3
 add(g.uv('Research atomic scanner '+str(i),(.31*math.cos(a),.15+.31*math.sin(a),.91),(.135,.135,.15),metal),'atomic-scan-generators')
 tube('Research scanner aperture '+str(i),(.31*math.cos(a),.15+.31*math.sin(a),.78),(.31*math.cos(a),.15+.31*math.sin(a),.81),.08,dark,role='atomic-scan-generators')
# Left service bay is an open framework in ST17, rather than another computer.
for x in [-.80,-.48]:
 for y in [-.32,.15]:tube('Research service bay upright',(x,y,.17),(x,y,.72),.015,trim)
for z in [.22,.48,.72]:
 for y in [-.32,.15]:tube('Research service bay rail',(-.80,y,z),(-.48,y,z),.015,trim)
for y in [-.32,.15]:tube('Research service bay crossbrace',(-.80,y,.22),(-.48,y,.72),.009,dark)
add(g.uv('Research luminous transfer chamber',(0,-.25,.65),(.35,.31,.17),glow))
role='long-range-transceiver'
tube('Research antenna mast',(0,.15,2.25),(0,.15,2.48),.025,dishmat,role=role)
for x in [-.07,.07]:tube('Research antenna support',(x,.15,2.28),(0,.15,2.48),.012,dishmat,role=role)
axis=Matrix.Rotation(math.radians(55),4,'X');origin=Vector((0,.15,2.50))
v=[];N=32;R=8
for side in [0,1]:
 for j in range(R+1):
  rad=.245*j/R
  for i in range(N):
   a=i*math.tau/N;p=axis@Vector((rad*math.cos(a),rad*math.sin(a),.14*(rad/.245)**2-side*.012));v.append(tuple(p+origin))
f=[];count=(R+1)*N
for side in [0,1]:
 for j in range(R):
  for i in range(N):
   q=(side*count+j*N+i,side*count+j*N+(i+1)%N,side*count+(j+1)*N+(i+1)%N,side*count+(j+1)*N+i);f.append(q if side==0 else tuple(reversed(q)))
for i in range(N):f.append((R*N+i,R*N+(i+1)%N,count+R*N+(i+1)%N,count+R*N+i))
f=[tuple(reversed(face)) for face in f]
data=bpy.data.meshes.new('Research paraboloid');data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new('Research tilted transceiver dish',data);s.collection.objects.link(ob);ob.data.materials.append(dishmat);add(ob,role)
tip=origin+axis@Vector((0,0,.26));tube('Research antenna feed horn',tuple(origin),tuple(tip),.014,dishmat,role=role)
# Sparse semantic wires use the actual assembly edges, not texture overlays.
bpy.context.view_layer.update();mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);wires={}
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
  for edge in bm.edges:
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_basis@v.co for v in edge.verts];spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
  bm.free()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,1.35));g.camera.location=(4,-10,5.3);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.4;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ore-teleporter.blend'))
from export_solid import export_solid
export_solid(root,meshes,out/'ore-teleporter.glb')
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,0)
for ob in meshes:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(['long-range-transceiver','atomic-scan-generators','data-throughput-supercomputer']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,.15,2.49],[0,.15,.90],[.65,-.20,.50]][i],closeup_rotation_euler=[[0,0,.8],[math.radians(-40),0,.3],[0,0,.5]][i],ortho_scale=[1.0,1.2,1.3][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:ore-teleporter',legacy_index=17,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,1.30],whole_information_rotation_euler=[.12,0,.25],whole_information_ortho_scale=3.9,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],limitations=['Existing selected mesh geometry/UV/material slots retained, foundation/ramp transforms adapted in research variant only. Chamber, three scanner interpretation, antenna and open service bay are authored from observed references. Hidden geometry, camera and wire topology approximated.']),indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('ORE_VARIANTS_READY',len(meshes))
