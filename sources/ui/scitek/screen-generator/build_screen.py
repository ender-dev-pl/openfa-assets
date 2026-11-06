"""PB10/ST23: three luminous lattice masts, tip suppressers and base oscillators."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='66b484bc9c79a39b7f65bccc0fd12bda7a10e2d3e359a7b0c4fa8bdb4341b953'
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
root=bpy.data.objects.new('ScreenResearchRoot',None);s.collection.objects.link(root)
parts={k:[] for k in ['chassis','three-field-masts','reverse-polarity-suppressers','phase-synchronising-oscillators']};meshes=[];segments=[]
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=['Foundation drum']
foundation=dst.objects[0];s.collection.objects.link(foundation);foundation.parent=root;foundation.scale.z=.25;meshes.append(foundation);parts['chassis'].append(foundation)
olive=g.material('Research worn olive screen housing',(.32,.34,.18),.45,.59);navy=g.material('Research used navy screen panels',(.055,.046,.075),.45,.61);silver=g.material('Research mast carrier used silver',(.35,.42,.43),.65,.49)
for mat in [olive,navy,silver]:
 for n in mat.node_tree.nodes:
  if n.type=='BUMP':n.inputs['Distance'].default_value=.002;n.inputs['Strength'].default_value=.10
  if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=78
def add(ob,role='chassis'):ob.parent=root;meshes.append(ob);parts[role].append(ob);return ob
def lathe(n,profile,mat):
 N=48;v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in profile for i in range(N)];f=[tuple(reversed(range(N)))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(profile)-1) for i in range(N)]+[tuple((len(profile)-1)*N+i for i in range(N))];data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for p in data.polygons:p.use_smooth=True
 return add(ob)
lathe('Research low olive screen dome',[(.03,.85),(.12,1),(.25,1.02),(.42,.88),(.51,.63),(.54,.08)],olive)
# Flush curved navy covers follow the dome instead of floating as small bumps.
for i in range(3):
 angle=i*math.tau/3;N=13;profile=[(.25,1.02),(.42,.88),(.51,.63)];v=[]
 for side in [0,1]:
  for z,r in profile:
   for k in range(N):
    a=angle+(k/(N-1)-.5)*math.pi/3;rr=r*(1.004 if side==0 else .999);v.append((rr*math.cos(a),rr*math.sin(a),z+(.002 if side==0 else -.002)))
 count=len(profile)*N;f=[]
 for side in [0,1]:
  for j in range(len(profile)-1):
   for k in range(N-1):
    q=(side*count+j*N+k,side*count+j*N+k+1,side*count+(j+1)*N+k+1,side*count+(j+1)*N+k);f.append(q if side==0 else tuple(reversed(q)))
 border=list(range(N))+[j*N+N-1 for j in range(1,3)]+list(range(3*N-2,2*N-1,-1))+[N]
 for k,p0 in enumerate(border):
  p1=border[(k+1)%len(border)];f.append((p0,p0+count,p1+count,p1))
 data=bpy.data.meshes.new('Research curved navy cover');data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(data);bm.free();ob=bpy.data.objects.new('Research broad dark screen cover '+str(i),data);s.collection.objects.link(ob);ob.data.materials.append(navy);add(ob)
def rod(n,a,b,r,mat,role):
 a,b=Vector(a),Vector(b);direction=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=direction.length,location=(a+b)/2);ob=bpy.context.object;ob.name=n;ob.rotation_euler=direction.to_track_quat('Z','Y').to_euler();ob.data.materials.append(mat);add(ob,role);segments.append((role,a.copy(),b.copy()));return ob
pulse=[];glowing=[]
for i,x in enumerate([-.55,0,.55]):
 start=Vector((x,0,.58));axis=Vector((x*.42,0,1.15));rotation=axis.to_track_quat('Z','Y');axis=axis.normalized()
 def point(z,rad=0,a=0):return start+axis*z+rotation@Vector((rad*math.cos(a),rad*math.sin(a),0))
 add(g.uv('Research phase oscillator '+str(i),tuple(start-Vector((0,0,.04))),(.12,.12,.11),silver),'phase-synchronising-oscillators')
 light=bpy.data.materials.new('Research luminous field mast '+str(i));light.use_nodes=True;bs=light.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.65,.85,1,1);bs.inputs['Emission Color'].default_value=(.65,.85,1,1);bs.inputs['Emission Strength'].default_value=2.2;light.diffuse_color=(.65,.85,1,1);glowing.append(light)
 rod('Research central mast conductor '+str(i),point(0),point(1.13),.009,silver,'three-field-masts')
 profile=[(0,0),(.25,.10),(.55,.15),(.85,.10),(1.10,0)]
 for k in range(4):
  a=k*math.pi/2
  for (z,r),(zz,rr) in zip(profile,profile[1:]):rod('Research luminous lattice '+str(i),point(z,r,a),point(zz,rr,a),.008,light,'three-field-masts')
  for (z,r),(zz,rr) in zip(profile[1:-1],profile[2:-1]):rod('Research luminous diagonal '+str(i),point(z,r,a),point(zz,rr,a+math.pi/2),.006,light,'three-field-masts')
 for k in range(9):
  bpy.ops.mesh.primitive_torus_add(major_radius=.030,minor_radius=.006,major_segments=16,minor_segments=6,location=point(.98+k*.015));ob=bpy.context.object;ob.name='Research polarity suppressor coil '+str(i);ob.rotation_euler=rotation.to_euler();ob.data.materials.append(silver);add(ob,'reverse-polarity-suppressers')
 add(g.uv('Research polarity suppressor ball '+str(i),tuple(point(1.15)),(.044,.044,.044),light),'reverse-polarity-suppressers')
# Original PB10 repeats the broad camera silhouette around frame30; two turns
# are authored over60updates. The light-strength track is an interpreted pulse.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/30;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
for f in range(1,62):
 values=[]
 for i,mat in enumerate(glowing):
  value=2.2+.9*math.sin((f-1)*math.tau/30+i*math.pi/3)**2;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Strength'].default_value=value;bs.inputs['Emission Strength'].keyframe_insert(data_path='default_value',frame=f);values.append(value)
 if f<=60:pulse.append(dict(frame=f-1,strengths=values))
s.frame_set(1);bpy.context.view_layer.update();wiremat=bpy.data.materials.new('Technical green');wiremat.use_nodes=True;nt=wiremat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
rod_names={ob.name for ob in parts['three-field-masts']}
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 def line(a,b):spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
 for which,a,b in segments:
  if which==role:line(a,b)
 for ob in obs:
  if ob.name in rod_names:continue
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
  for edge in bm.edges:
   if 'suppressor ball' in ob.name or 'phase oscillator' in ob.name:
    a0,b0=[v.co for v in edge.verts]
    if abs(a0.z-b0.z)<1e-6:
     if round(math.acos(max(-1,min(1,a0.z)))/math.pi*24)%3:continue
    elif round(math.atan2(a0.y,a0.x)/math.tau*48)%4:continue
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_basis@v.co for v in edge.verts];line(a,b)
  bm.free()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(wiremat);ob.hide_render=True
target=Vector((0,0,.88));g.camera.location=(4,-10,5.3);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=2.9;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'screen-generator.blend'));export_solid(root,meshes,out/'screen-generator.glb');s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(['three-field-masts','reverse-polarity-suppressers','phase-synchronising-oscillators']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,0,1.14],[0,0,1.67],[0,0,.55]][i],closeup_rotation_euler=[[0,0,0],[0,0,0],[0,0,0]][i],ortho_scale=[1.3,.44,.65][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:screen-generator',legacy_index=23,components={k:[o.name for o in v] for k,v in parts.items()},phases=phases,whole_information_local_target=[0,0,.87],whole_information_rotation_euler=[.12,0,.25],whole_information_ortho_scale=3.3,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=['Foundation drum'],new_presentation_meshes=[o.name for o in meshes if o!=foundation],limitations=['Existing foundation geometry, UVs and material slots retained with compressed Z placement. Three in-line tilted lattices, nine-coil tip suppressors and base oscillators are authored approximations from actual PB10/ST23. Body turn rate and pulse are interpreted from colour phases.']),indent=2)+'\n')
(out/'emission-timeline.json').write_text(json.dumps(dict(frame_count=60,fps=15,root=root.name,whole_device_turns=2,materials=[m.name for m in glowing],timeline=pulse,portable_contract='Apply per-material emission strengths; GLB does not portably carry animated shader parameters.'),indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('SCREEN_VARIANTS_READY',len(meshes))
