"""Private ST02 review prototype; not a completed delivery or final camera."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'artifacts/issue-208-scitek/anti-missile-pod-prototype').resolve();out.mkdir(exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
relative_base='sources/docs/assets/bootstrap-3d/terran-refined/pb03/model.blend'
base=Path(sys.argv[sys.argv.index('--base-blend')+1]).resolve() if '--base-blend' in sys.argv else next(p/relative_base for p in Path(__file__).resolve().parents if (p/relative_base).is_file())
digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='35d1dca30489613d235c64cc9fbf40acfe124f655718eee81a4677108a438a01'
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=['Turret armoured pedestal','Armoured pedestal sectors','Pedestal foundation joint']
for ob in dst.objects:s.collection.objects.link(ob)
bpy.context.view_layer.update()
retained=[]
for ob in dst.objects:
 matrix=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=matrix;retained.append(ob)
base_root=bpy.data.objects.new('PodFixedBase',None);s.collection.objects.link(base_root);base_root.scale.z=.65/.9
head=bpy.data.objects.new('PodTrackingHead',None);s.collection.objects.link(head);head.location=(0,0,.65)
parts={k:[] for k in ['chassis','twin-tracking-dishes','alloy-plasma-barrel','armoured-plasma-base']}
parts['armoured-plasma-base']=retained
# The historical source is never edited; these are presentation copies.
# Eight radial lower notches approximate the repeated dark source silhouette.
pre_slot_geometry={ob.name:hashlib.sha256(json.dumps(dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(f.vertices) for f in ob.data.polygons])).encode()).hexdigest() for ob in retained}
for ob in retained:
 ob.parent=base_root
 for i in range(8):
  angle=i*math.tau/8
  cutter=g.box('Temporary radial slot cutter',(.96*math.cos(angle),.96*math.sin(angle),.09),(.36,.12,.38),g.dark,0)
  cutter.rotation_euler.z=angle
  # Boolean operates in world space, including the compressed base transform.
  bpy.context.view_layer.update();bpy.context.view_layer.objects.active=ob
  mod=ob.modifiers.new('Source-observed lower radial notch','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)

role='chassis'
copper=g.material('ST02 used copper research head',(.36,.155,.12),.62,.46)
for node in copper.node_tree.nodes:
 if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=120
 if node.type=='BUMP':node.inputs['Distance'].default_value=.003
 if node.type=='VALTORGB':node.color_ramp.elements[0].color=(.36*.72,.155*.72,.12*.72,1)
dark=g.material('ST02 sensor recess',(.025,.033,.032),.25,.52)
silver=g.material('ST02 tracking dish alloy',(.35,.39,.38),.72,.4)
wear=g.material('ST02 new head contact wear',(.21,.115,.075),.6,.6)
def mark(ob):
 parts[role].append(ob);ob.parent=head;ob.location.z-=.9;return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def lathe(n,profile,mat,origin=(0,0,0),axis=(0,0,1),N=48):
 q=Vector(axis).to_track_quat('Z','Y');origin=Vector(origin)
 verts=[origin+q@Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)) for z,r in profile for i in range(N)]
 faces=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
lathe('Research copper rounded head',[(.89,.63),(.94,.64),(1.05,.60),(1.20,.51),(1.35,.40),(1.48,.26),(1.55,.12),(1.57,.025)],copper)
role='alloy-plasma-barrel'
axis=Vector((0,-1,.40)).normalized();origin=Vector((0,-.24,1.40))
lathe('Slender stepped plasma barrel',[(0,.19),(.09,.18),(.20,.145),(.27,.13),(.50,.115),(.56,.09),(.76,.078),(.82,.075)],copper,origin,axis)
tube('Plasma muzzle recess',origin+axis*.82,origin+axis*.828,.038,dark)
for offset in [.22,.52,.73]:
 tube('Wear plasma barrel contact seam',origin+axis*offset,origin+axis*(offset+.008),.15 if offset<.3 else .118 if offset<.6 else .080,wear)
role='twin-tracking-dishes'
for side in [-1,1]:
 origin=Vector((side*.68,-.20,1.13));axis=Vector((side*.85,-.50,.05)).normalized()
 tube('Tracking dish mounting neck '+str(side),origin-axis*.20,origin+axis*.018,.065,copper)
 lathe('Twin tracking dish '+str(side),[(0,.09),(.015,.13),(.045,.17),(.065,.17),(.067,.14),(.041,.10),(.026,.025)],silver,origin,axis)
 tube('Tracking dish dark centre '+str(side),origin+axis*.027,origin+axis*.032,.085,dark)
 tube('Tracking dish receiver '+str(side),origin+axis*.032,origin+axis*.10,.014,silver)
 role='chassis';tube('Tracking rear antenna '+str(side),(side*.30,.30,1.19),(side*.30,.40,1.51),.006,copper,.002);role='twin-tracking-dishes'
 # Localised wear on newly authored dish only; retained base remains unchanged.
 tube('Wear tracking rim contact '+str(side),origin+axis*.066+Vector((0,0,.145)),origin+axis*.067+Vector((0,.025,.143)),.003,wear)
role='chassis'
for i in range(10):
 a=i*math.tau/10;r=.625;z=.96
 tube('Wear new head lower contact',(r*math.cos(a),r*math.sin(a),z),(r*math.cos(a+.025),r*math.sin(a+.025),z+.006),.003,wear)
head.rotation_mode='XYZ'
for frame in [1,16,31,46,61]:head.rotation_euler.z=-(frame-1)*math.tau/60;head.keyframe_insert(data_path='rotation_euler',frame=frame)
for fc in head.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_start=1;s.frame_end=61;s.render.fps=15;s.frame_set(1)
target=Vector((0,0,.675));g.camera.location=(-4,-7,3.075);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.05
s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
from mathutils import Matrix
root=bpy.data.objects.new('PodResearchRoot',None);s.collection.objects.link(root)
base_root.parent=root;head.parent=root
component_names={k:[ob.name for ob in v] for k,v in parts.items()}
for group,objects in parts.items():
 for ob in objects:ob['scitek_component']=group
bpy.context.view_layer.update()
def emit(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
green=emit('ST02 technical green',(0,.72,.005));red=emit('ST02 selected red',(.9,.003,.001));wires={}
for group,objects in parts.items():
 data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.002;data.bevel_resolution=0
 for ob in objects:
  if ob.name.startswith('Wear '):continue
  for edge in ob.data.edges:
   sp=data.splines.new('POLY');sp.points.add(1)
   for p,i in zip(sp.points,edge.vertices):p.co=(*(ob.matrix_world@ob.data.vertices[i].co),1)
 wire=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(wire);wire.parent=root;data.materials.append(green);wire.hide_render=True;wires[group]=wire
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
# All head poses are checked while the base remains fixed.
cm=g.camera.rotation_euler.to_matrix();right,up=cm.col[0],cm.col[1];aspect=.9;projected=[];extent=0
for frame in range(1,61):
 s.frame_set(frame);bpy.context.view_layer.update();pts=[ob.matrix_world@v.co for obs in parts.values() for ob in obs for v in ob.data.vertices]
 xs=[(p-g.camera.location).dot(right) for p in pts];ys=[(p-g.camera.location).dot(up) for p in pts]
 extent=max(extent,2*max(abs(min(xs)),abs(max(xs)))/aspect,2*max(abs(min(ys)),abs(max(ys))));projected.append([min(xs),min(ys),max(xs),max(ys)])
g.camera.data.ortho_scale=max(3.05,math.ceil(extent*1.06*100)/100)
framing=dict(frame_count=60,ortho_scale=g.camera.data.ortho_scale,method='All mesh vertices, fixed base and all sixty articulated head poses',ndc_bounds=[[.5+a/(g.camera.data.ortho_scale*aspect),.5+b/g.camera.data.ortho_scale,.5+c/(g.camera.data.ortho_scale*aspect),.5+d/g.camera.data.ortho_scale] for a,b,c,d in projected])
s.frame_set(1);render('solid.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'anti-missile-pod.blend'))
for mat in [copper,dark,silver,wear]:
 bs=mat.node_tree.nodes.get('Principled BSDF')
 for slot in ['Base Color','Normal','Metallic','Roughness']:
  for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for ob in objects:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('anti-missile-pod.glb',[base_root,head]+[ob for obs in parts.values() for ob in obs])
head.animation_data_clear();head.rotation_euler=(0,0,0)
for obs in parts.values():
 for ob in obs:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.resolution_x=896;s.render.resolution_y=896;s.cycles.samples=4;s.view_settings.view_transform='Standard'
info_cm=(Vector((0,0,.65))-Vector((5,-10,4))).to_track_quat('-Z','Y').to_matrix();whole_info_euler=list(Matrix((info_cm.col[0],-info_cm.col[2],info_cm.col[1])).to_euler('XYZ'))
g.camera.location=(5,-10,4);target=Vector((0,0,.65));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=4.3
render('wireframe.png');export('anti-missile-pod-wireframe.glb',list(wires.values()));wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera.data.ortho_scale)};phases=[]
angles={'twin-tracking-dishes':(0,0,55),'alloy-plasma-barrel':(0,0,35),'armoured-plasma-base':(-75,0,0)}
targets={'twin-tracking-dishes':(-.68,-.20,.88),'alloy-plasma-barrel':(0,-.65,1.30),'armoured-plasma-base':(0,0,.32)}
scales={'twin-tracking-dishes':.65,'alloy-plasma-barrel':1.45,'armoured-plasma-base':3.95}
for i,group in enumerate(list(parts)[1:]):
 for name,ob in wires.items():ob.data.materials[0]=red if name==group else green
 root.rotation_euler=[math.radians(a) for a in angles[group]];bpy.context.view_layer.update();local_target=Vector(targets[group]);target=root.matrix_world@local_target
 g.camera.location=(target.x,target.y-12,target.z+.15);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=scales[group]
 name='highlight-'+group;render(name+'.png');export('anti-missile-pod-'+name+'.glb',list(wires.values()));wire_cameras[name]=(g.camera.matrix_world.copy(),g.camera.data.ortho_scale)
 phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=scales[group],highlight_glb='anti-missile-pod-'+name+'.glb'))
bpy.ops.wm.open_mainfile(filepath=str(out/'anti-missile-pod.blend'));s=bpy.context.scene
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'anti-missile-pod.glb'));render('imported-solid.png')
for name,(camera,scale) in wire_cameras.items():
 for ob in list(s.objects):
  if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(out/('anti-missile-pod-'+name+'.glb')));s.camera.matrix_world=camera;s.camera.data.ortho_scale=scale;s.cycles.samples=4;s.view_settings.view_transform='Standard';s.render.resolution_x=896;s.render.resolution_y=896;render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'anti-missile-pod.blend'));s=bpy.context.scene;render('reload-solid.png')
model=dict(issue=208,id='scitek:anti-missile-pod',legacy_index=2,source='_MA/PB03.256 + PB03.VID; _SCITEK/ST02.VID',components=component_names,phases=phases,information_timeline_frames=423,solid_framing=framing,whole_information_rotation_euler=whole_info_euler,whole_information_local_target=[0,0,.65],whole_information_ortho_scale=4.3,base_source=dict(path=relative_base,sha256=digest,retained_objects=list(pre_slot_geometry),pre_slot_geometry=pre_slot_geometry,changes='Presentation copies compressed vertically and cut with eight approximate lower radial slots; original source unchanged'),solid_animation=dict(root='PodResearchRoot',moving_node='PodTrackingHead',fixed_node='PodFixedBase',frame_count=60,fps=15))
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n');(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('POD_VARIANTS_READY')
