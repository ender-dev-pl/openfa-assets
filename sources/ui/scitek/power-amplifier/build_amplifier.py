"""Power Amplifier: actual ST20 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST20: three collars, an actual U-ended upper opening, generator controls,
# top reflector and two oval lower optical couplings. No source pixel textures.
shell=g.material('Used warm amplifier casing',(.31,.265,.20),.43,.59)
light=g.material('Worn warm amplifier collar alloy',(.45,.385,.29),.5,.49)
dark=g.material('Amplifier recess grime',(.024,.021,.020),.15,.74)
blue=g.material('Dark vapour generator control blocks',(.085,.09,.10),.25,.58)
brass=g.material('Faded amplifier service inlay',(.25,.18,.115),.4,.61)
markpaint=g.material('Dark red optical lens',(.37,.08,.057),.18,.42)
reflector_mat=g.material('Tarnished distorted optical reflector',(.28,.255,.23),.80,.30)
for mat in [shell,light,brass]:
 for node in mat.node_tree.nodes:
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=100
  if node.type=='BUMP':node.inputs['Strength'].default_value=.10;node.inputs['Distance'].default_value=.002
parts={k:[] for k in ['chassis','ethereal-vapour-generator','distorted-reflector','optical-coupling-ports']};role='chassis'
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def box(n,loc,size,mat,b=.004):return mark(g.box(n,loc,size,mat,b))
def mesh(n,v,f,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def ring(n,z0,z1,rin,rout,mat,N=48):
 v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in [(z0,rout),(z1,rout),(z0,rin),(z1,rin)] for i in range(N)];f=[]
 for i in range(N):
  j=(i+1)%N;f.extend([(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(N+i,N+j,3*N+j,3*N+i),(j,i,2*N+i,2*N+j)])
 return mesh(n,v,f,mat)
for name,z0,z1 in [('Bottom',.02,.19),('Middle',1.30,1.47),('Top',2.58,2.73)]:
 ring(name+' amplifier collar',z0,z1,.335,.46,light)
 ring(name+' collar recessed seam',z0+.025,z0+.04,.444,.463,dark)
upper=ring('Upper central chamber shell',1.43,2.62,.315,.37,shell)
ring('Lower central chamber shell',.15,1.34,.315,.37,shell)
# A single closed extruded U-shaped cutter makes a real upper front opening.
outline=[(-.17,2.54),(.17,2.54),(.17,2.12)]+[(.17*math.cos(i*math.pi/20),2.12-.17*math.sin(i*math.pi/20)) for i in range(1,21)]
v=[(x,y,z) for y in [-.65,-.18] for x,z in outline];N=len(outline);f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
cutter=mesh('Temporary U opening cutter',v,f,dark);parts['chassis'].remove(cutter)
bpy.context.view_layer.objects.active=upper;mod=upper.modifiers.new('U ended service opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
box('Dark generator panel backing',(0,-.225,2.255),(.30,.02,.50),dark)
for i in range(12):
 a=i*math.tau/12;rad=Vector((math.cos(a),math.sin(a),0))
 for z in [.20,1.50]:tube('Long casing assembly joint',tuple(rad*.372+Vector((0,0,z))),tuple(rad*.372+Vector((0,0,z+1.0))),.0028,dark)
 for z in [.12,1.385,2.65]:tube('Small casing rivet',tuple(rad*.462+Vector((0,0,z))),tuple(rad*.468+Vector((0,0,z))),.008,brass)
for i in range(18):
 a=i*2.399963;rad=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-rad.y,rad.x,0));centre=rad*.374+Vector((0,0,.24+(i%7)*.14));tube('Wear short casing scrape',tuple(centre-tangent*.012),tuple(centre+tangent*.010+Vector((0,0,.008))),.0018,brass if i%3 else dark)
for i in range(9):
 a=i*2.399963;rad=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-rad.y,rad.x,0));centre=rad*.464+Vector((0,0,[.09,1.37,2.64][i%3]));tube('Wear collar abrasion',tuple(centre-tangent*.018),tuple(centre+tangent*.017),.0025,dark)
role='ethereal-vapour-generator'
for x in [-.09,.09]:tube('Upper vapour generator indicator',(x,-.44,2.64),(x,-.469,2.64),.025,markpaint)
for row in range(3):
 for col in range(2):box('Vapour generator vertical control',(-.10+col*.075,-.25,2.42-row*.105),(.028,.025,.073),blue,.002)
tube('Large vapour generator dial',(.09,-.25,2.29),(.09,-.28,2.29),.034,brass)
for x,z in [(.05,2.15),(.11,2.15),(.02,2.39)]:tube('Small generator status light',(x,-.25,z),(x,-.28,z),.014,markpaint)
for x in [-.11,-.035,.04,.115]:box('Lower generator control slit',(x,-.25,2.04),(.019,.025,.065),brass,.001)
role='distorted-reflector'
profile=[(2.64,.355),(2.705,.355),(2.69,.25),(2.70,.08)];N=48
v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z+(.006*math.sin(3*i*math.tau/N) if j>0 else 0)) for j,(z,r) in enumerate(profile) for i in range(N)]
f=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
for j in range(len(profile)-1):
 for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
mesh('Distorted top reflector',v,f,reflector_mat)
role='chassis'
for i in range(4):
 a=i*math.pi/2;rad=Vector((math.cos(a),math.sin(a),0));tube('Reflector retaining tab',tuple(rad*.35+Vector((0,0,2.635))),tuple(rad*.43+Vector((0,0,2.635))),.012,light)
role='optical-coupling-ports'
for i,z in enumerate([.90,.37]):
 gasket=mark(g.uv('Optical coupling oval gasket '+str(i),(0,-.385,z),(.069,.023,.105),dark))
 mark(g.uv('Optical coupling red lens '+str(i),(0,-.405,z),(.055,.025,.09),markpaint))
root=bpy.data.objects.new('AmplifierRotor',None);s.collection.objects.link(root);root.scale.x=1.04
component_names={k:[ob.name for ob in objects] for k,objects in parts.items()}
for group,objects in parts.items():
 for ob in objects:ob.parent=root;ob.matrix_basis=Matrix.Rotation(math.radians(-30),4,'Z')@ob.matrix_basis;ob['scitek_component']=group
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
        if o.type!='MESH':continue
        # The original technical film shows a readable chamber cage, not every
        # small extruded heat-transfer fin. The solid model retains all ribs.
        if o.name.startswith(('Wear ','Small casing rivet')):continue
        for edge in o.data.edges:
            va,vb=[o.data.vertices[i].co for i in edge.vertices]
            if o.name in ['Upper central chamber shell','Lower central chamber shell'] and abs(va.z-vb.z)>1e-6:
                step=math.atan2(va.y,va.x)/(math.tau/48)
                if abs(step-round(step))<1e-4 and int(round(step))%4:continue
            if o.name=='Distorted top reflector' and edge.vertices[0]//48!=edge.vertices[1]//48 and edge.vertices[0]%48%12:continue
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
g.camera.location=(3,-10,3.9);target=Vector((0,0,1.36));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.05
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
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
bpy.ops.wm.save_as_mainfile(filepath=str(out/'power-amplifier.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint,g.gold,g.red,reflector_mat]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('power-amplifier.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,1.55);target=Vector((0,0,1.36));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.05
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('power-amplifier-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['ethereal-vapour-generator','distorted-reflector','optical-coupling-ports']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle=0 if group=='distorted-reflector' else 30
    local_target=Vector({'ethereal-vapour-generator':(-.15,-.259808,2.28),'distorted-reflector':(0,0,2.69),'optical-coupling-ports':(-.195,-.33775,.635)}[group])
    root.rotation_euler=(math.radians(90) if group=='distorted-reflector' else 0,0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'ethereal-vapour-generator':1.15,'distorted-reflector':1.15,'optical-coupling-ports':1.05}[group]
    render('highlight-'+group+'.png');export('power-amplifier-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='power-amplifier-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'power-amplifier.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'power-amplifier.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('power-amplifier-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'power-amplifier.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:power-amplifier',legacy_index=20,source='_MA/ST20.256 + ST20.VID; _SCITEK/ST20.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
