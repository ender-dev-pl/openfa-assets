"""Building Armour: actual ST06 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST06: portable armour field device, four ionisers, two rear thermal panels,
# front damage-control interface, dark side handles and solid-only blue fields.
shell=g.material('Worn grey armour casing',(.29,.28,.23),.5,.50)
light=g.material('Handled pale brass armour rim',(.57,.49,.27),.6,.43)
dark=g.material('Grime in armour grips and recesses',(.025,.030,.026),.25,.66)
blue=g.material('Dark green control surface',(.045,.065,.055),.2,.55)
brass=g.material('Used olive armour housing',(.22,.24,.10),.35,.50)
markpaint=g.material('Faded caution yellow',(.56,.40,.065),.25,.60)
for mat in [shell,light,brass,markpaint]:
 for node in mat.node_tree.nodes:
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=90
  if node.type=='BUMP':node.inputs['Strength'].default_value=.11;node.inputs['Distance'].default_value=.004
parts={k:[] for k in ['chassis','ionisers','thermal-transducers','damage-monitor']};role='chassis';effects=[]
def mark(ob):parts[role].append(ob);return ob
def box(n,p,d,mat,bevel=.01):return mark(g.box(n,p,d,mat,bevel))
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def mesh(n,verts,faces,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def disk(n,profile,a,b,mat):
 count=48;v=[(a*r*math.cos(i*math.tau/count),y,2+b*r*math.sin(i*math.tau/count)) for y,r in profile for i in range(count)];f=[tuple(reversed(range(count))),tuple(range((len(profile)-1)*count,len(profile)*count))]
 for j in range(len(profile)-1):
  for i in range(count):f.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
 return mesh(n,v,f,mat)
mark(g.uv('Oval armour main casing',(0,0,2),(.85,.25,.64),brass))
disk('Front pale armour bezel',[(-.19,.94),(-.25,1),(-.32,1),(-.34,.92)],.75,.58,light)
for sign in [-1,1]:
 v=[];N=64;K=12
 def rail(t):return Vector((sign*1.10+.32*math.copysign(abs(math.cos(t))**.5,math.cos(t)),0,2+.39*math.copysign(abs(math.sin(t))**.5,math.sin(t))))
 for i in range(N):
  t=(i+.25)*math.tau/N;centre=rail(t);tangent=(rail(t+.001)-rail(t-.001)).normalized();normal=Vector((-tangent.z,0,tangent.x))
  for j in range(K):
   a=j*math.tau/K;v.append(centre+normal*(.12*math.cos(a))+Vector((0,.14*math.sin(a),0)))
 f=[]
 for i in range(N):
  for j in range(K):f.append((i*K+j,((i+1)%N)*K+j,((i+1)%N)*K+(j+1)%K,i*K+(j+1)%K))
 mesh('Rounded side carry handle',v,f,shell)
 mark(g.uv('Red grip coupling pad',(sign*.91,-.14,2),(.09,.035,.20),g.red))
for z in [1.39,2.61]:
 box('Rear rim bridge',(0,.06,z),(.48,.18,.09),brass)
 for i in range(5):box('Rim service lug',(-.16+i*.08,-.03,z),(.035,.19,.08),light,.004)
for xsign in [-1,1]:
 for zsign in [-1,1]:
  tube('Ioniser olive mounting bracket',(xsign*.48,0,2+zsign*.43),(xsign*.61,0,2+zsign*.55),.09,brass)
  tube('Ioniser metal collar',(xsign*.61,0,2+zsign*.55),(xsign*.69,0,2+zsign*.63),.075,light)
role='ionisers'
for xsign in [-1,1]:
 for zsign in [-1,1]:
  direction=Vector((xsign,0,zsign));ob=mark(g.uv('Armour ioniser capsule',(xsign*.79,0,2+zsign*.70),(.06,.06,.175),shell));ob.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
role='thermal-transducers'
for z in [1.71,2.29]:
 box('Rear thermal transducer panel',(0,.265,z),(1.05,.055,.44),light)
 for i in range(13):
  ob=box('Thermal panel grille slat',(-.47+i*.078,.303,z),(.018,.015,.38),dark,.002);ob['technical_omit']=True
role='damage-monitor'
disk('Damage control monitoring face',[(-.345,.95),(-.365,.99),(-.385,.80),(-.402,.50),(-.410,.15),(-.411,.01)],.69,.53,blue)
ob=box('Central monitoring keypad',(0,-.423,2),(.25,.025,.85),light,.004);ob['technical_omit']=True
for i in range(9):
 ob=box('Keypad marking',(-.01,-.44,1.65+i*.083),(.18,.008,.018),dark,.001);ob['technical_omit']=True
for i in range(3):
 ob=box('Diagonal caution stripe',(.34,-.414,1.83+i*.14),(.075,.015,.30),markpaint,.003);ob.rotation_euler.y=math.radians(42);ob['technical_omit']=True
mark(g.uv('Red status indicator',(-.34,-.414,2.19),(.055,.020,.055),g.red))['technical_omit']=True
for i in range(5):box('Left control marking',(-.33,-.416,1.87+i*.045),(.19,.012,.012),light,.002)['technical_omit']=True
def raymat(n,c):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*(x*.25 for x in c),1);bs.inputs['Emission Color'].default_value=(*c,1);bs.inputs['Emission Strength'].default_value=.5;bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0;return m
raymats=[raymat('Cobalt ionisation field',(.005,.025,.9)),raymat('Blue plasma strand',(.008,.14,.85)),raymat('Bright cyan plasma core',(.025,.42,1))]
for xs in [-1,1]:
 for zs in [-1,1]:
  for strand in range(3):
   data=bpy.data.curves.new('Authored ionisation field','CURVE');data.dimensions='3D';data.bevel_depth=[.019,.012,.006][strand];data.bevel_resolution=2;data.use_fill_caps=True;sp=data.splines.new('POLY');sp.points.add(23)
   for j,p in enumerate(sp.points):
    t=j/23;jag=math.sin(j*2.1+strand*1.7)*.026*math.sin(t*math.pi);p.co=(xs*(.91+1.09*t+jag),.015+strand*.012,2+zs*(.82+1.48*t-jag),1);p.radius=.4+.6*math.sin(math.pi*t)**.5
   ob=bpy.data.objects.new('Solid only blue ionisation field',data);s.collection.objects.link(ob);g.finish(ob,raymats[strand],ob.name);ob['scitek_solid_only_effect']=True;effects.append(ob)
root=bpy.data.objects.new('ArmourRotor',None);s.collection.objects.link(root);component_names={k:[ob.name for ob in obs] for k,obs in parts.items()}
for group,obs in parts.items():
 for ob in obs:ob.parent=root;ob['scitek_component']=group
for ob in effects:ob.parent=root
effect_names=[ob.name for ob in effects]
root.rotation_euler.z=0

def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.005;data.bevel_resolution=0
    for o in objects:
        if o.type=='CURVE':
            for old in o.data.splines:
                sp=data.splines.new('POLY');sp.points.add(len(old.points)-1);sp.use_cyclic_u=old.use_cyclic_u
                for p,q in zip(sp.points,old.points):p.co=(*(o.matrix_basis@Vector(q.co[:3])),1)
            continue
        if o.get('technical_omit'):continue
        if o.type!='MESH':continue
        # The original technical film shows a readable chamber cage, not every
        # small extruded heat-transfer fin. The solid model retains all ribs.
        if 'Carbon drill cutting tip' in o.name or 'Collar worn fastener' in o.name:continue
        for edge in o.data.edges:
            va,vb=[o.data.vertices[i].co for i in edge.vertices]
            # Forty longitudinal lines on every tiny rib hide the highlighted
            # coolant pair. Keep smooth end rings but four/eight structural
            # meridians, as an explicit technical-display representation.
            if len(o.data.vertices)==80 and abs(va.z-vb.z)>1e-6:
                angle=math.atan2(va.y,va.x);step=int(round(angle/(math.tau/40)))%40
                stride=10 if 'rib' in o.name.lower() else 5
                if step%stride:continue
            if len(o.data.vertices)>1000:
                # The convex UV cap retains six parallels and twelve meridians.
                if abs(va.z-vb.z)<1e-6:
                    ring=round(math.acos(max(-1,min(1,va.z)))*24/math.pi)
                    if ring%4:continue
                else:
                    step=int(round(math.atan2(va.y,va.x)/(math.tau/48)))%48
                    if step%4:continue
            spline=data.splines.new('POLY');spline.points.add(1)
            for p,i in zip(spline.points,edge.vertices):p.co=(*(o.matrix_basis@o.data.vertices[i].co),1)
    ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wire[group]=ob
g.camera.location=(0,-10,2);target=Vector((0,0,2));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.65
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for ob in effects:ob.hide_render=mode!='solid'
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
render('solid.png')
# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(0)-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'building-armour.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint,g.gold,g.red]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_format='GLB')
export('building-armour.glb',[o for obs in parts.values() for o in obs]+effects)
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.15);target=Vector((0,0,2));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.2
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('building-armour-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['ionisers','thermal-transducers','damage-monitor']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle={'ionisers':0,'thermal-transducers':180,'damage-monitor':0}[group]
    local_target=Vector({'ionisers':(.79,0,2.70),'thermal-transducers':(0,.27,2),'damage-monitor':(0,-.34,2)}[group])
    root.rotation_euler=(0,0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'ionisers':.72,'thermal-transducers':1.95,'damage-monitor':2.25}[group]
    render('highlight-'+group+'.png');export('building-armour-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='building-armour-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'building-armour.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'building-armour.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('building-armour-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'building-armour.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:building-armour',legacy_index=6,source='_MA/ST06.256 + ST06.VID; _SCITEK/ST06.VID',components=component_names,solid_only_effect_nodes=effect_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
