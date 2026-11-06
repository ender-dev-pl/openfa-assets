"""Private PB22/ST04 shape review; final wire/animation delivery is separate."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='b642cd0e3381d54deb774f14cbd11eafede84c9e5eae5e1be28559237d3fdf16'
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=['Central segmented field orb','Peripheral field orb','Foundation drum']
for ob in dst.objects:s.collection.objects.link(ob)
bpy.context.view_layer.update();central,template,old_base=dst.objects
old_base_material=old_base.data.materials[0];bpy.data.objects.remove(old_base,do_unlink=True)
root=bpy.data.objects.new('AsteroidEngineRotor',None);s.collection.objects.link(root)
parts={k:[] for k in ['chassis','central-gravitic-reactor','opposing-generator-pairs','fixed-asteroid-mount']}
central.location=(0,0,1.15);central.scale=tuple(v*.68 for v in central.scale);central.parent=root;parts['central-gravitic-reactor'].append(central)
peripherals=[]
for i in range(4):
 ob=template if i==0 else template.copy()
 if i:ob.data=template.data.copy();s.collection.objects.link(ob)
 angle=math.pi/4+i*math.tau/4;x=.85*math.cos(angle);y=.85*math.sin(angle)
 ob.name='Research opposing generator '+str(i);ob.location=(x,y,.65);ob.rotation_euler=Vector((-x*.40,-y*.40,1)).to_track_quat('Z','Y').to_euler();ob.parent=root;peripherals.append(ob);parts['opposing-generator-pairs'].append(ob)
sphere_material=central.data.materials[0].copy();sphere_material.name='ST04 reference-calibrated dark navy sphere';sphere_material.diffuse_color=(.065,.075,.12,1)
bs=sphere_material.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=sphere_material.diffuse_color
for ob in [central]+peripherals:ob.data.materials[0]=sphere_material
new_base=g.material('ST04 worn green mounting cone',(.22,.26,.22),.6,.64)
for node in new_base.node_tree.nodes:
 if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=80
 if node.type=='BUMP':node.inputs['Distance'].default_value=.002
 if node.type=='VALTORGB':node.color_ramp.elements[0].color=(.22*.65,.26*.65,.22*.65,1)
dark=g.material('ST04 spherical housing dark split',(.025,.028,.038),.55,.56)
light=g.material('ST04 worn seam edge',(.14,.15,.19),.6,.54)
red=g.material('ST04 recessed red seam indicator',(.40,.016,.008),.25,.4)
role='fixed-asteroid-mount'
def mark(ob):ob.parent=root;parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def lathe(n,profile,mat,N=64):
 verts=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in profile for i in range(N)]
 faces=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
lathe('Research flared asteroid mounting cone',[(0,1.35),(.06,1.35),(.24,1.0),(.31,.75)],new_base)
for i in range(12):
 a=i*math.tau/12;r=1.25;z=.105
 tube('Wear mounting perimeter scrape',(r*math.cos(a),r*math.sin(a),z),(r*math.cos(a+.035),r*math.sin(a+.035),z+.005),.003,light if i%3 else dark)
role='chassis';tube('Central reactor mounting stem',(0,0,.27),(0,0,.62),.15,new_base)
for z in [.32,.55]:tube('Wear mounting stem contact',(0,0,z),(0,0,z+.008),.152,dark)
def band(n,centre,radii,mat,axis,role_name):
 global role
 role=role_name;verts=[];faces=[];N=64
 # A closed narrow strip follows the ellipsoid meridian.
 for side in [-1,1]:
  for i in range(N):
   t=i*math.tau/N;local=Vector((radii[0]*math.sin(t),side*.013,radii[2]*math.cos(t)))
   verts.append(Vector(centre)+axis@local)
 for i in range(N):faces.append((i,(i+1)%N,N+(i+1)%N,N+i))
 # Solidify gives the authored band finite thickness for reliable GLB export.
 data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);ob.data.materials.append(mat);mark(ob)
 mod=ob.modifiers.new('Solid housing band thickness','SOLIDIFY');mod.thickness=.006;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
 return ob
bpy.context.view_layer.update()
from mathutils import Matrix
band('Central sphere narrow meridian',(0,0,1.15),(.82*.68+.006,0,.91*.68+.006),dark,Matrix.Rotation(math.pi/2,3,'Z'),'central-gravitic-reactor')
role='central-gravitic-reactor'
for dz in [-.12,-.42]:
 y=-(.82*.68+.010)*math.sqrt(1-(dz/(.91*.68))**2)
 mark(g.uv('Central red seam signal',(0,y,1.15+dz),(.011,.011,.011),red))
for i,ob in enumerate(peripherals):
 axis=ob.rotation_euler.to_matrix()@Matrix.Rotation(math.pi/2,3,'Z');band('Generator narrow meridian '+str(i),ob.location,(.43+.006,0,.46+.006),dark,axis,'opposing-generator-pairs')
 # Tiny paired red source-visible seam signals, mounted on the front meridian.
 role='opposing-generator-pairs'
 for t in [-math.pi*.60,-math.pi*.72]:
  p=ob.location+axis@Vector((.438*math.sin(t),0,.468*math.cos(t)))
  mark(g.uv('Generator red seam signal',p,(.012,.012,.012),red))
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,.90));g.camera.location=(0,-8,5.6);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.5
s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True

component_names={k:[o.name for o in v] for k,v in parts.items()}
green=bpy.data.materials.new('Technical green');green.use_nodes=True
nt=green.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs['Surface'])
wire={}
for group,obs in parts.items():
 data=bpy.data.curves.new(group+' technical wire','CURVE');data.dimensions='3D';data.bevel_depth=.004;data.bevel_resolution=0;data.resolution_u=1
 for ob in obs:
  if 'signal' in ob.name.lower() or 'Wear' in ob.name:continue
  mesh=ob.data
  # Keep construction lines sparse enough to read the round housings.
  if 'orb' in ob.name.lower() or 'opposing generator' in ob.name.lower():
   coords=[ob.matrix_basis@v.co for v in mesh.vertices];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));centre=(lo+hi)/2;r=(hi-lo)/2
   for mode in ['meridian','parallel']:
    for j in range(16 if mode=='meridian' else 11):
     points=[]
     for k in range(65):
      a=k*math.tau/64;b=j*math.tau/16 if mode=='meridian' else (j+1)*math.pi/12
      p=Vector((r.x*math.sin(a)*math.cos(b),r.y*math.sin(a)*math.sin(b),r.z*math.cos(a))) if mode=='meridian' else Vector((r.x*math.sin(b)*math.cos(a),r.y*math.sin(b)*math.sin(a),r.z*math.cos(b)))
      points.append(centre+p)
     spl=data.splines.new('POLY');spl.points.add(len(points)-1)
     for p,v in zip(spl.points,points):p.co=(*v,1)
  else:
   for edge in mesh.edges:
    a,b=[mesh.vertices[i].co for i in edge.vertices]
    if len(mesh.vertices)>100 and abs(a.z-b.z)>1e-5 and edge.index%8:continue
    spl=data.splines.new('POLY');spl.points.add(1)
    for p,v in zip(spl.points,[a,b]):p.co=(*(ob.matrix_basis@v),1)
 o=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(o);o.parent=root;o.data.materials.append(green);o.hide_render=True;wire[group]=o
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'asteroid-engines.blend'))
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in objects:o.select_set(True)
 temporary=[]
 for ob in objects:
  for mat in ob.data.materials:
   if not mat.use_nodes:continue
   nt=mat.node_tree;em=nt.nodes.get('Emission');output=nt.nodes.get('Material Output')
   if not em:continue
   rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=em.inputs['Color'].default_value;nt.links.new(rgb.outputs[0],output.inputs['Surface']);temporary.append((nt,em,output,rgb))
 bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
 for nt,em,output,rgb in temporary:nt.links.new(em.outputs[0],output.inputs['Surface']);nt.nodes.remove(rgb)

saved_links=[]
for mat in {m for obs in parts.values() for ob in obs for m in ob.data.materials if m and m.use_nodes}:
 nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
 if not bs:continue
 bs.inputs['Base Color'].default_value=mat.diffuse_color
 for slot in ['Base Color','Normal','Metallic','Roughness']:
  for link in list(bs.inputs[slot].links):saved_links.append((nt,link.from_socket,link.to_socket));nt.links.remove(link)
export('asteroid-engines.glb',[o for obs in parts.values() for o in obs])
for nt,a,b in saved_links:nt.links.new(a,b)

s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,0)
for obs in parts.values():
 for o in obs:o.hide_render=True
for o in wire.values():o.hide_render=False
s.view_settings.view_transform='Standard';s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=8
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
export('asteroid-engines-wireframe.glb',list(wire.values()))
phases=[]
for i,group in enumerate(['central-gravitic-reactor','opposing-generator-pairs','fixed-asteroid-mount']):
 phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[0,0,[1.15,.65,.8][i]],closeup_rotation_euler=[[0,0,0],[math.pi/2,0,.4],[.48,0,-.25]][i],ortho_scale=[1.65,3.1,3.8][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:asteroid-engines',legacy_index=4,components=component_names,phases=phases,whole_information_local_target=[0,0,.9],whole_information_rotation_euler=[.48,0,0],whole_information_ortho_scale=4.0,information_timeline_frames=425,source_base_sha256=digest,opposing_pairs=[[0,2],[1,3]],acceptance='Approximately 80% visual correspondence; authored camera and topology'),indent=2)+'\n',encoding='utf-8')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('ENGINE_VARIANTS_READY')
