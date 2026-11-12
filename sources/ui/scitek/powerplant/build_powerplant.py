"""PB23/ST21 four-part research presentation, preserving scoped existing hardware."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='657709c29ae32bdf5cfc579d254eee9490cfabbe699774cdad90727da55ad997'
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX';root=bpy.data.objects.new('PowerplantResearchRoot',None);s.collection.objects.link(root);root.scale.z=1.15
roles=['chassis','control-computer-and-antennae','six-fusion-reactor-cells','asteros-mini-mining-facility','four-waste-ore-pipes'];parts={k:[] for k in roles};meshes=[]
names=['Reactor flared base','Reactor raised deck','Reactor plinth armour']+['Reactor cooling vessel'+('.'+str(i).zfill(3) if i else '') for i in range(6)]
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=list(names)
for ob in dst.objects:
 assert ob is not None
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
 role='six-fusion-reactor-cells' if ob.name.startswith('Reactor cooling vessel') else 'chassis';parts[role].append(ob)
 if role=='six-fusion-reactor-cells':ob.scale.z*=.65;ob.location.z+=.10
 if ob.name=='Reactor raised deck':ob.scale.z=1/3;ob.location.z=.72
preserved=[ob.name for ob in meshes]
tan=g.material('Research used control-computer ochre',(.39,.31,.15),.5,.56);metal=g.material('Research worn mine and support steel',(.28,.31,.30),.6,.53);brass=g.material('Research used waste-ore bronze',(.38,.24,.10),.55,.58);dark=g.material('Research grime at powerplant joints',(.035,.035,.028),.35,.68)
for mat in [tan,metal,brass,dark]:
 for node in mat.node_tree.nodes:
  if node.type=='BUMP':node.inputs['Distance'].default_value=.002;node.inputs['Strength'].default_value=.10
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=75
def add(ob,role='chassis'):ob.parent=root;meshes.append(ob);parts[role].append(ob);return ob
def tube(n,a,b,r,mat,role='chassis',r2=None):return add(g.tube(n,a,b,r,mat,r2),role)
def lathe(n,profile,mat,role):
 N=32;v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in profile for i in range(N)];f=[tuple(reversed(range(N)))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(profile)-1) for i in range(N)]+[tuple((len(profile)-1)*N+i for i in range(N))];data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for p in data.polygons:p.use_smooth=True
 return add(ob,role)
for i in range(6):
 a=i*math.tau/6;x=.68*math.cos(a);y=.68*math.sin(a)
 tube('Research fusion cell lower socket',(x,y,1.02),(x,y,1.09),.14,metal,'six-fusion-reactor-cells')
 add(g.box('Research fusion cell top service hatch',(x,y,1.60),(.10,.10,.025),metal,.005),'six-fusion-reactor-cells')
role='control-computer-and-antennae';lathe('Research control computer tower',[(1.02,.20),(1.18,.22),(1.63,.22),(1.74,.15),(1.76,.05)],tan,role)
for i,(x,y,z) in enumerate([(-.08,0,2.10),(0,.02,2.22),(.08,0,2.02)]):
 tube('Research communications antenna '+str(i),(x,y,1.74),(x,y,z),.007,metal,role)
 add(g.uv('Research antenna terminal '+str(i),(x,y,z),(.014,.014,.014),metal),role)
for x in [-.63,.63]:
 for y in [-.63,.63]:tube('Research open-deck support',(x,y,.30),(x,y,.96),.025,metal)
role='asteros-mini-mining-facility';lathe('Research Asteros mini-mine central bore',[(.25,.20),(.38,.23),(.79,.23),(.93,.16)],metal,role)
for x in [-.40,.40]:
 for y in [-.35,.35]:
  add(g.uv('Research Asteros mini-mine reservoir',(x,y,.61),(.13,.13,.19),metal),role)
  tube('Research Asteros mini-mine feed',(x,y,.48),(x,y,.78),.035,brass,role)
# Four continuous hollow elbows, rather than the six straight bootstrap conduits.
pipe_lines=[]
for i in range(4):
 a=math.pi/4+i*math.pi/2;rad=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0));points=[rad*1.02+Vector((0,0,.40)),rad*1.24+Vector((0,0,.40)),rad*1.40+Vector((0,0,.37)),rad*1.50+Vector((0,0,.30)),rad*1.54+Vector((0,0,.20)),rad*1.54+Vector((0,0,.08))];N=12;R=len(points);v=[];outside=[]
 for layer,radius in enumerate([.085,.055]):
  for j,p in enumerate(points):
   tangent=(points[min(j+1,R-1)]-points[max(j-1,0)]).normalized();other=tangent.cross(side).normalized()
   ring=[p+side*(radius*math.cos(k*math.tau/N))+other*(radius*math.sin(k*math.tau/N)) for k in range(N)];v.extend(tuple(q) for q in ring)
   if layer==0:outside.append(ring)
 count=N*R;f=[]
 for layer in [0,1]:
  for j in range(R-1):
   for k in range(N):
    q=(layer*count+j*N+k,layer*count+j*N+(k+1)%N,layer*count+(j+1)*N+(k+1)%N,layer*count+(j+1)*N+k);f.append(q if layer==0 else tuple(reversed(q)))
 for j in [0,R-1]:
  for k in range(N):f.append((j*N+k,j*N+(k+1)%N,count+j*N+(k+1)%N,count+j*N+k))
 data=bpy.data.meshes.new('Research hollow waste ore elbow');data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(data);bm.free();ob=bpy.data.objects.new('Research waste-ore elbow '+str(i),data);s.collection.objects.link(ob);ob.data.materials.append(brass);add(ob,'four-waste-ore-pipes')
 for ring in outside:
  for k in range(N):pipe_lines.append((ring[k],ring[(k+1)%N]))
 for one,two in zip(outside,outside[1:]):pipe_lines.extend(zip(one,two))
bpy.context.view_layer.update();mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 def line(a,b):spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
 if role=='four-waste-ore-pipes':
  for a,b in pipe_lines:line(a,b)
 else:
  for ob in obs:
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
   for edge in bm.edges:
    if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
    a,b=[ob.matrix_basis@v.co for v in edge.verts];line(a,b)
   bm.free()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,1.02));g.camera.location=(4,-10,5.3);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.8;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'powerplant.blend'));export_solid(root,meshes,out/'powerplant.glb');s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(roles[1:]):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,0,1.60],[0,0,1.33],[0,0,.62],[1.05,1.05,.30]][i],closeup_rotation_euler=[[0,0,0],[math.pi/2,-math.pi/6,0],[0,0,0],[0,0,-math.pi/4]][i],ortho_scale=[2.20,2.35,1.85,1.35][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:powerplant',legacy_index=21,components={k:[o.name for o in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,1.0],whole_information_rotation_euler=[.12,0,.25],whole_information_ortho_scale=4.3,information_timeline_frames=564,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],limitations=['Nine selected original meshes retain geometry/UV/material slots; cell Z proportion and raised deck transform adapted in research variant. Mini-mine, controls and four hollow pipe elbows are authored interpretations.']),indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('POWERPLANT_VARIANTS_READY',len(meshes))
