"""PB12/ST10 presentation variant with three open base sectors and four cardinal sensors."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='af79022662b034c6a9d917cc5722746d7f11d20cf40b82261829c1f7aa9efb34'
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=['Central segmented field orb']
orb=dst.objects[0];s.collection.objects.link(orb);root=bpy.data.objects.new('NullifierResearchRoot',None);s.collection.objects.link(root);orb.parent=root
parts={k:[] for k in ['chassis','central-gravitic-reactor','fixed-shaped-base','cardinal-orientation-sensors']};parts['central-gravitic-reactor'].append(orb)
navy=orb.data.materials[0].copy();navy.name='Research dark navy orb finish';navy.diffuse_color=(.065,.075,.12,1);bs=navy.node_tree.nodes.get('Principled BSDF')
if bs:
 for link in list(bs.inputs['Base Color'].links):navy.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=navy.diffuse_color
orb.data.materials[0]=navy
paint=g.material('Research mounting base weathered green',(.22,.26,.22),.6,.64);dark=g.material('Research dark shell joints',(.025,.028,.038),.55,.56);edge=g.material('Research base worn edge',(.14,.15,.19),.6,.54);gold=g.material('Research orientation sensor aged brass',(.40,.32,.07),.65,.55);red=g.material('Research red seam lights',(.4,.016,.008),.25,.4)
role='fixed-shaped-base'
def mark(ob):ob.parent=root;parts[role].append(ob);return ob
def tube(n,a,b,r,mat):return mark(g.tube(n,a,b,r,mat))
def mesh(n,verts,faces,mat):
 data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
N=96;profile=[(1.0,.10),(1.2,0),(1.2,.08),(1.0,.19)];verts=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for r,z in profile for i in range(N)];faces=[]
for j in range(4):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,((j+1)%4)*N+(i+1)%N,((j+1)%4)*N+i))
mesh('Research open mounting outer ring',verts,faces,paint)
for i in range(3):
 a=math.pi/2+i*math.tau/3;along=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0));verts=[]
 for r,z,w in [(0,.34,.23),(1.08,.16,.16)]:
  for dz in [-.08,0]:
   for sign in [-1,1]:verts.append(along*r+side*w*sign/2+Vector((0,0,z+dz)))
 mesh('Research open base spoke '+str(i),verts,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],paint)
tube('Research base central hub',(0,0,.20),(0,0,.38),.24,paint)
for i in range(12):
 a=i*math.tau/12;r=1.13;tube('Wear outer mounting scuff',(r*math.cos(a),r*math.sin(a),.12),(r*math.cos(a+.025),r*math.sin(a+.025),.12),.0025,edge if i%3 else dark)
role='chassis';tube('Research reactor mounting stem',(0,0,.32),(0,0,.55),.12,paint)
role='central-gravitic-reactor';verts=[];N=64
for side in [-1,1]:
 for i in range(N):
  a=i*math.tau/N;verts.append((side*.009,-.827*math.sin(a),1.35+.917*math.cos(a)))
faces=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)];ob=mesh('Research narrow vertical meridian',verts,faces,dark);mod=ob.modifiers.new('Finite meridian wall','SOLIDIFY');mod.thickness=.004;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
# A single lower latitude seam, rather than the old study's dense cage.
r=.82*math.sqrt(1-(.27/.91)**2)
for i in range(64):
 a=i*math.tau/64;b=(i+1)*math.tau/64;tube('Research lower latitude seam',(r*math.cos(a),r*math.sin(a),1.08),(r*math.cos(b),r*math.sin(b),1.08),.005,dark)
for dz in [-.10,-.35]:
 y=-.825*math.sqrt(1-(dz/.91)**2);mark(g.uv('Research red orb signal',(0,y,1.35+dz),(.012,.012,.012),red))
role='cardinal-orientation-sensors'
for i in range(4):
 a=i*math.tau/4;x=1.10*math.cos(a);y=1.10*math.sin(a);mark(g.uv('Research cardinal sensor '+str(i),(x,y,.15),(.055,.055,.020),gold))
 # Small material-appropriate rim wear remains readable in the solid views.
 tube('Wear sensor contact '+str(i),(x-.02,y,.155),(x+.02,y,.155),.002,edge)
# Four portable technical groups. The orb uses an analytic sparse grid;
# non-orb construction curves come from the authored meshes.
green=bpy.data.materials.new('Technical green');green.use_nodes=True;nt=green.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);wires={}
for group,obs in parts.items():
 data=bpy.data.curves.new(group+' technical wire','CURVE');data.dimensions='3D';data.bevel_depth=.0006 if group=='cardinal-orientation-sensors' else .004;data.bevel_resolution=0
 def line(points):
  spl=data.splines.new('POLY');spl.points.add(len(points)-1)
  for p,v in zip(spl.points,points):p.co=(*v,1)
 for ob in obs:
  if ob==orb or ob.name.startswith('Research cardinal sensor '):
   centre=orb.location if ob==orb else ob.location;radius=Vector((.82,.82,.91)) if ob==orb else Vector((.055,.055,.020))
   for mode in ['meridian','parallel']:
    for j in range(16 if mode=='meridian' else 11):
     points=[]
     for k in range(65):
      a=k*math.tau/64;b=j*math.tau/16 if mode=='meridian' else (j+1)*math.pi/12
      p=centre+Vector((radius.x*math.sin(a)*math.cos(b),radius.y*math.sin(a)*math.sin(b),radius.z*math.cos(a))) if mode=='meridian' else centre+Vector((radius.x*math.sin(b)*math.cos(a),radius.y*math.sin(b)*math.sin(a),radius.z*math.cos(b)));points.append(p)
     line(points)
   continue
  if 'Wear' in ob.name or 'signal' in ob.name or 'latitude seam' in ob.name:continue
  for e in ob.data.edges:
   a,b=[ob.matrix_basis@ob.data.vertices[i].co for i in e.vertices]
   if 'outer ring' in ob.name and abs(a.z-b.z)>1e-6 and round(math.atan2(a.y,a.x)/math.tau*96)%4:continue
   line([a,b])
 ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wires[group]=ob
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,1.1));g.camera.location=(0,-8,5.6);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.6;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'gravity-nullifier.blend'));saved=[]
for mat in [paint,dark,edge,gold,red]:
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color
 for slot in ['Base Color','Normal']:
  for link in list(bs.inputs[slot].links):saved.append((mat.node_tree,link.from_socket,link.to_socket));mat.node_tree.links.remove(link)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for obs in parts.values():
 for ob in obs:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'gravity-nullifier.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
for nt,a,b in saved:nt.links.new(a,b)
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,0)
for obs in parts.values():
 for ob in obs:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,group in enumerate(['central-gravitic-reactor','fixed-shaped-base','cardinal-orientation-sensors']):phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,0,1.35],[0,0,.12],[0,-1.1,.15]][i],closeup_rotation_euler=[[0,0,0],[math.pi/2,0,0],[math.pi/2,0,0]][i],ortho_scale=[2.4,3.2,.25][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:gravity-nullifier',legacy_index=10,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,1.1],whole_information_rotation_euler=[.48,0,0],whole_information_ortho_scale=4.3,information_timeline_frames=423,base_source_sha256=digest,reused_mesh='Central segmented field orb',sensor_count=4,open_base_sectors=3,limitations=['Original source model unchanged. Orb geometry reused with a navy colour variant; new base, joints and sensors approximate actual PB12/ST10. Authored camera and wire topology.']),indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(base.read_bytes()).hexdigest()==digest;print('NULLIFIER_VARIANTS_READY')
