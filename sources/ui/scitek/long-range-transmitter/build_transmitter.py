"""Long Range Transmitter: actual ST34 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST34 enclosed faceted terminal, cartridge modules and right-side encryption.
shell=g.material('Worn transmitter tan alloy',(.40,.32,.225),.38,.60)
light=g.material('Used pale transmitter frame',(.54,.44,.31),.42,.53)
dark=g.material('Transmitter recess grime',(.022,.025,.027),.18,.74)
blue=g.material('Muted blue end marking and button',(.035,.10,.21),.10,.64)
brass=g.material('Faded transmitter edge alloy',(.29,.21,.13),.45,.63)
markpaint=g.material('Worn red transmitter button',(.47,.045,.025),.15,.59)
button_green=g.material('Worn green transmitter button',(.025,.31,.035),.15,.59)
screenmat=g.material('Dark navy console glass',(.012,.020,.035),.12,.38)
for mat in [shell,light,brass]:
 for n in mat.node_tree.nodes:
  if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=90
  if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.002
parts={k:[] for k in ['chassis','audio-visual-console','data-cartridge-drives','data-encryption-device']};role='chassis'
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def box(n,loc,size,mat,b=.006):return mark(g.box(n,loc,size,mat,b))
def mesh(n,v,f,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
cross=[(-.50,-.32),(-.34,-.48),(.33,-.48),(.50,-.30),(.50,.30),(.33,.48),(-.34,.48),(-.50,.30)]
def housing(n,x0,x1,scale,mat,stations=10):
 profile=[]
 for a,b in zip(cross,cross[1:]+cross[:1]):profile.extend((a[0]+(b[0]-a[0])*i/4,a[1]+(b[1]-a[1])*i/4) for i in range(4))
 N=len(profile);v=[(x0+(x1-x0)*j/stations,y*scale,z*scale) for j in range(stations+1) for y,z in profile];f=[tuple(reversed(range(N))),tuple(range(stations*N,(stations+1)*N))]
 for j in range(stations):
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 return mesh(n,v,f,mat)
body=housing('Main faceted transmitter enclosure',-1.30,1.30,1,shell)
housing('Left octagonal end cover',-1.52,-1.28,1.07,light,2)
right_cover=housing('Right encryption end cover',1.27,1.61,1.12,shell,3)
def subtract(ob,n,loc,size):
 tool=g.box(n,loc,size,dark,0);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new(n,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
subtract(body,'Console recess cutter',(-.10,-.56,.01),(1.58,.43,.69))
for z in [-.20,0,.20]:subtract(right_cover,'Rear end vent cutter',(1.51,.50,z),(.42,.17,.065))
def fp(x,z,offset=0):return (x,-.52+.25*z+offset,z)
def frontbox(n,x,z,w,h,depth,mat,offset=0,b=.004):
 ob=box(n,fp(x,z,offset),(w,depth,h*math.sqrt(1.0625)),mat,b);ob.rotation_euler.x=-math.atan(.25);return ob
for x in [-.83,.63]:frontbox('Console side bezel',x,.02,.08,.60,.10,light)
frontbox('Console upper bezel',-.10,.32,1.52,.08,.10,light)
frontbox('Console lower control shelf',-.10,-.34,1.62,.14,.17,light,-.015)
for x in [-1.18,1.18]:
 for z in [-.30,.30]:tube('Small casing fastener',(x,-.51,z),(x,-.525,z),.010,brass)
def path(n,points,r,mat,closed=False):
 data=bpy.data.curves.new(n,'CURVE');data.dimensions='3D';data.bevel_depth=r;data.bevel_resolution=1;data.use_fill_caps=True;sp=data.splines.new('POLY');sp.points.add(len(points)-1);sp.use_cyclic_u=closed
 for p,v in zip(sp.points,points):p.co=(*v,1)
 ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
for cy,cz,ry,rz in [(-.18,.23,.095,.10),(-.14,-.17,.15,.18),(.20,-.10,.08,.14)]:path('Left end service engraving',[(-1.524,cy+ry*math.cos(i*math.tau/12),cz+rz*math.sin(i*math.tau/12)) for i in range(12)],.003,brass,True)
# Source end marking is reproduced as a geometric motif; its lettering/meaning
# has not been established. It is intentionally absent from technical wire LOD.
box('Solid-only blue end emblem',(1.614,0,-.13),(.006,.18,.26),blue,.001)
path('Solid-only emblem upper loop',[(1.619,-.045,.01),(1.619,-.045,.13),(1.619,.045,.13),(1.619,.045,.01)],.011,blue)
for cy,cz in [(0,-.09),(-.037,-.17),(.037,-.17)]:path('Solid-only emblem interior motif',[(1.620,cy+.025*math.cos(i*math.tau/20),cz+.025*math.sin(i*math.tau/20)) for i in range(20)],.004,light,True)
for i,mat in enumerate([markpaint,button_green,blue]):
 path('Front coloured service loop',[(.58+.40*j/32,-.64-.005*i,-.31-.21*math.sin(j*math.pi/32)) for j in range(33)],.006,mat)
for i in range(16):
 x=-1.05+(i%8)*.27;z=.41 if i<8 else -.40;tube('Wear transmitter edge scrape',(x,-.35,z),(x+.035,-.35,z+.006),.002,brass if i%3 else dark)
for x in [-.8,.75]:
 for z in [-.36,.38]:frontbox('Wear bezel contact stain',x,z,.06,.015,.005,dark,-.052,.001)
role='audio-visual-console'
frontbox('Audio visual display glass',-.10,.03,1.30,.48,.014,screenmat,0,.005)
for x,mat in [(-.36,markpaint),(-.12,button_green),(.12,blue)]:frontbox('Console RGB control button',x,-.31,.17,.055,.027,mat,-.11,.003)
# Independent authored green packet glyphs, not a transcription of source text.
led=bpy.data.materials.new('Authored green console packet display');led.diffuse_color=(.005,.60,.006,1);led.use_nodes=True;nt=led.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.005,.60,.006,1);em.inputs['Strength'].default_value=.85;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
glyphs=[[2,5,7,5,5],[7,4,6,4,7],[7,1,3,1,7],[5,5,7,1,1],[7,5,5,5,7]];vv=[];ff=[]
for row in range(2):
 for col in range(12):
  glyph=glyphs[(col*3+row)%len(glyphs)]
  for r,bits in enumerate(glyph):
   for c in range(3):
    if not bits&(1<<(2-c)):continue
    x=-.68+col*.096+c*.023;z=.215-row*.135-r*.017;base=len(vv)
    for yy in [-.012,-.010]:
     vv.extend(fp(x+dx,z+dz,yy) for dx,dz in [(-.009,-.006),(.009,-.006),(.009,.006),(-.009,.006)])
    ff.extend(tuple(base+j for j in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
mesh('Solid-only green packet glyphs',vv,ff,led)
role='data-cartridge-drives'
for x in [-1.00,.84]:
 frontbox('Data cartridge drive casing',x,.035,.24,.75,.14,light,-.015,.014)
 frontbox('Cartridge dark entry slot',x,.035,.070,.53,.014,dark,-.096,.003)
 frontbox('Cartridge front door',x+.035,.035,.11,.50,.020,shell,-.102,.004)
 for z in [-.285,.325]:tube('Cartridge status point',fp(x,z,-.102),fp(x,z,-.116),.018,markpaint)
role='data-encryption-device'
box('Internal variable encryption core',(1.29,-.17,.025),(.28,.39,.36),shell,.005)
box('Nested encryption encoder block',(1.29,-.12,.305),(.23,.27,.20),light,.005)
box('Encryption front black panel',(1.33,-.567,-.015),(.17,.016,.40),dark,.003)
for x,z,mat in [(1.29,.13,markpaint),(1.36,.13,button_green),(1.29,.05,brass),(1.36,.05,markpaint)]:tube('Encryption status indicator',(x,-.576,z),(x,-.588,z),.012,mat)
box('Encryption lower grey control',(1.33,-.583,-.12),(.09,.018,.08),light,.002)
for z in [-.22,-.285,-.35,-.415]:box('Encryption lower plate',(1.29,-.19,z),(.25,.37,.018),shell,.003)
path('Variable encryption adjustment ring',[(1.40+.065*math.cos(i*math.tau/32),-.43,-.105+.065*math.sin(i*math.tau/32)) for i in range(32)],.009,brass,True)
root=bpy.data.objects.new('TransmitterRotor',None);s.collection.objects.link(root)
component_names={k:[ob.name for ob in objects] for k,objects in parts.items()}
for group,objects in parts.items():
 for ob in objects:ob.parent=root;ob['scitek_component']=group
root.rotation_euler.z=0

def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.0025;data.bevel_resolution=0
    for o in objects:
        if o.name.startswith('Solid-only '):continue
        if o.type=='CURVE':
            for old in o.data.splines:
                sp=data.splines.new('POLY');sp.points.add(len(old.points)-1);sp.use_cyclic_u=old.use_cyclic_u
                for p,q in zip(sp.points,old.points):p.co=(*(o.matrix_basis@Vector(q.co[:3])),1)
            continue
        if o.type!='MESH':continue
        # The original technical film shows a readable chamber cage, not every
        # small extruded heat-transfer fin. The solid model retains all ribs.
        if o.name.startswith(('Wear ','Solid-only ','Small casing fastener')):continue
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
g.camera.location=(-5,-10,7.5);target=Vector((0,0,0));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.8
s.render.resolution_x=576;s.render.resolution_y=640
cm=g.camera.rotation_euler.to_matrix();info_cm=(Vector((0,0,0))-Vector((9,-10,9))).to_track_quat('-Z','Y').to_matrix();whole_info_euler=list(Matrix((info_cm.col[0],-info_cm.col[2],info_cm.col[1])).to_euler('XYZ'))
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
# Source tile occupancy with a common safe camera for all60 solid poses.
right=cm.col[0];up=cm.col[1];aspect=s.render.resolution_x/s.render.resolution_y;projected=[];extent=0.0
for frame in range(60):
    root.rotation_euler.z=-frame*math.tau/60;bpy.context.view_layer.update()
    points=[ob.matrix_world@v.co for objects in parts.values() for ob in objects if ob.type=='MESH' for v in ob.data.vertices]
    xs=[(p-g.camera.location).dot(right) for p in points];ys=[(p-g.camera.location).dot(up) for p in points];projected.append((min(xs),min(ys),max(xs),max(ys)))
a,b,c,d=projected[0];cx=(a+c)/2;cy=(b+d)/2;source_scale=max((c-a)/(133/144*aspect),(d-b)/(82/160))
dx=cx-(71.5/144-.5)*source_scale*aspect;dy=cy-(1-82/160-.5)*source_scale
for a,b,c,d in projected:extent=max(extent,2*max(abs(a-dx),abs(c-dx))/aspect,2*max(abs(b-dy),abs(d-dy)))
g.camera_data.ortho_scale=max(source_scale,math.ceil(extent*1.06*100)/100);g.camera.location+=right*dx+up*dy
framing=dict(frame_count=60,method='Source occupied box and all solid vertices at all60 poses with minimum6 percent envelope margin',ortho_scale=g.camera_data.ortho_scale,source_occupancy_scale=source_scale,ndc_bounds=[[.5+(a-dx)/(g.camera_data.ortho_scale*aspect),.5+(b-dy)/g.camera_data.ortho_scale,.5+(c-dx)/(g.camera_data.ortho_scale*aspect),.5+(d-dy)/g.camera_data.ortho_scale] for a,b,c,d in projected])
root.rotation_euler.z=0;bpy.context.view_layer.update()
points=[ob.matrix_world@v.co for objects in parts.values() for ob in objects if ob.type=='MESH' for v in ob.data.vertices]
ir=info_cm.col[0];iu=info_cm.col[1];xs=[p.dot(ir) for p in points];ys=[p.dot(iu) for p in points]
whole_scale=max((max(xs)-min(xs))/(111/224),(max(ys)-min(ys))/(85/224))
whole_target=list(ir*((min(xs)+max(xs))/2-(110.5/224-.5)*whole_scale)+iu*((min(ys)+max(ys))/2-(1-111.5/224-.5)*whole_scale))
assert all(min(b)>0 and max(b)<1 for b in framing['ndc_bounds']);native_camera_matrix=g.camera.matrix_world.copy()
render('solid.png')

# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(0)-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'long-range-transmitter.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint,button_green,screenmat,g.gold,g.red]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('long-range-transmitter.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.matrix_world=native_camera_matrix;g.camera_data.ortho_scale=whole_scale
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('long-range-transmitter-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['audio-visual-console','data-cartridge-drives','data-encryption-device']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angles={'audio-visual-console':(0,0,0),'data-cartridge-drives':(-10,-65,-25),'data-encryption-device':(5,0,-15)}
    local_target=Vector({'audio-visual-console':(-.10,-.52,-.025),'data-cartridge-drives':(-.10,-.53,0),'data-encryption-device':(1.29,-.20,-.04)}[group])
    root.rotation_euler=[math.radians(a) for a in angles[group]];bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'audio-visual-console':1.63,'data-cartridge-drives':1.90,'data-encryption-device':.90}[group]
    render('highlight-'+group+'.png');export('long-range-transmitter-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='long-range-transmitter-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'long-range-transmitter.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'long-range-transmitter.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('long-range-transmitter-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'long-range-transmitter.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:long-range-transmitter',legacy_index=34,source='_MA/ST34.256 + ST34.VID; _SCITEK/ST34.VID',components=component_names,solid_framing=framing,whole_information_rotation_euler=whole_info_euler,whole_information_local_target=whole_target,whole_information_ortho_scale=whole_scale,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
