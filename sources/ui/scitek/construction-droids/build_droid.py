"""Construction Droids: actual ST07 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST07: stationary umbrella body, articulated heavy/light manipulators,
# front optic, lower spot welder, two-prong precision tool and welding sparks.
from mathutils import Quaternion
shell=g.material('Worn graphite droid canopy',(.065,.051,.053),.30,.60)
light=g.material('Used pale precision manipulator',(.65,.61,.47),.48,.43)
dark=g.material('Grimy heavy manipulator alloy',(.045,.043,.047),.45,.55)
blue=g.material('Dark optical sensor glass',(.025,.030,.038),.25,.22)
brass=g.material('Faded lavender service casting',(.40,.32,.31),.50,.46)
markpaint=g.material('Used purple welding head',(.32,.20,.23),.45,.50)
roof_patch=g.material('Darker worn canopy sectors',(.045,.035,.038),.3,.6)
for mat in [shell,light,dark,brass,markpaint,roof_patch]:
 for n in mat.node_tree.nodes:
  if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=90
  if n.type=='BUMP':n.inputs['Strength'].default_value=.1;n.inputs['Distance'].default_value=.004
parts={k:[] for k in ['chassis','heavy-manipulator','optical-sensor','spot-welder','light-manipulator','laser-solder-tool']};role='chassis';effects=[];pivots=[]
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def mesh(n,v,f,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def lathe(n,profile,mat,N=40):
 v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in profile for i in range(N)];f=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 return mesh(n,v,f,mat)
roof=lathe('Segmented umbrella canopy',[(2.24,1.15),(2.30,1.24),(2.40,1.15),(2.60,.70),(2.74,.23),(2.77,.10)],shell,32)
roof.data.materials.append(roof_patch)
for poly in roof.data.polygons:
 if poly.index%7 in [0,1]:poly.material_index=1
lathe('Canopy lower dark rim',[(2.22,1.17),(2.27,1.20)],dark,32)
tube('Small top aerial',(0,0,2.76),(0,0,2.99),.019,light,.006);mark(g.uv('Aerial base',(0,0,2.78),(.065,.065,.055),light))
lathe('Tapered central service body',[(1.00,.19),(1.15,.25),(1.72,.35),(2.16,.43),(2.25,.44)],brass,12)
for x in [-.28,.28]:tube('Welder suspension strut',(x,0,1.10),(x*.5,-.20,.84),.025,light)
for sign in [-1,1]:
 mark(g.uv('Shoulder ball joint',(sign*.80,0,2.20),(.23,.23,.22),brass))
 tube('Shoulder service collar',(sign*.80,0,2.14),(sign*.88,-.10,1.97),.18,shell,.15)
tube('Heavy arm forearm',(-.88,-.10,1.98),(-.83,-.43,1.58),.155,brass,.12)
tube('Precision arm upper link',(.88,-.10,1.98),(.94,-.21,1.83),.11,light,.085)
role='heavy-manipulator'
heavy_centre=Vector((-.83,-.48,1.45));tube('Heavy gripper palm',heavy_centre+Vector((0,0,.15)),heavy_centre+Vector((0,0,-.02)),.15,dark,.20)
heavy_jaws=[]
for k in range(3):
 angle=k*math.tau/3;N=8;profile=[(.15,.10),(.02,.24),(-.18,.29),(-.31,.13)];v=[]
 for inner in [False,True]:
  for z,r in profile:
   r-=.055 if inner else 0
   for i in range(N):
    a=angle-.67+i*1.34/(N-1);v.append((r*math.cos(a),r*math.sin(a),z))
 count=len(profile)*N;f=[]
 for j in range(len(profile)-1):
  for i in range(N-1):
   q=j*N+i;f.extend([(q,q+1,q+N+1,q+N),(q+count,q+N+count,q+N+1+count,q+1+count)])
 for j in range(len(profile)-1):
  for i in [0,N-1]:q=j*N+i;f.append((q,q+N,q+N+count,q+count))
 for j in [0,len(profile)-1]:
  for i in range(N-1):q=j*N+i;f.append((q,q+count,q+1+count,q+1))
 ob=mesh('Heavy curved gripping jaw',v,f,dark);ob.location=heavy_centre;heavy_jaws.append((ob,angle))
role='optical-sensor'
tube('Optical sensor metal housing',(.24,-.30,1.76),(.24,-.43,1.76),.14,shell,.115)
mark(g.uv('High resolution optical lens',(.24,-.447,1.76),(.10,.035,.10),blue))
role='spot-welder'
welder_parts=[]
welder_parts.append(mark(g.uv('Purple spot welding head',(0,-.31,.80),(.31,.22,.12),markpaint)))
welder_parts.append(tube('Spot welding tapered nozzle',(0,-.35,.76),(.18,-.41,.58),.10,light,.025))
coil=bpy.data.curves.new('Coiled welder cable','CURVE');coil.dimensions='3D';coil.bevel_depth=.026;coil.bevel_resolution=2;sp=coil.splines.new('POLY');sp.points.add(159);coil.use_fill_caps=True
for i,p in enumerate(sp.points):
 t=i/159;a=t*math.tau*10;p.co=(-.24+.12*t+.055*math.cos(a),-.24+.055*math.sin(a),1.47-.63*t,1)
ob=bpy.data.objects.new('Coiled spot welder feed',coil);s.collection.objects.link(ob);g.finish(ob,g.red,ob.name);mark(ob)
role='light-manipulator';light_parts=[]
light_parts.append(tube('Precision lower forearm',(.94,-.21,1.83),(1.12,-.36,1.65),.075,light,.06))
light_parts.append(mark(g.uv('Light gripper wrist',(1.12,-.36,1.64),(.085,.085,.075),light)))
light_fingers=[]
for sign in [-1,1]:
 points=[]
 for i in range(18):
  a=.1+i*math.pi*.75/17;points.append((sign*(.04+.13*math.sin(a)),0,-.11+.13*math.cos(a)))
 # Closed curved finger volume around a small polyline.
 v=[]
 for i,p in enumerate(points):
  tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);normal=Vector((-tangent.z,0,tangent.x)).normalized()
  for j in range(8):a=j*math.tau/8;v.append(Vector(p)+normal*(.025*math.cos(a))+Vector((0,.025*math.sin(a),0)))
 f=[tuple(reversed(range(8))),tuple(range((len(points)-1)*8,len(points)*8))]
 for i in range(len(points)-1):
  for j in range(8):f.append((i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j))
 ob=mesh('Pale precision gripper finger',v,f,light);ob.location=(1.12,-.36,1.64);light_parts.append(ob);light_fingers.append((ob,sign))
role='laser-solder-tool'
tube('Laser solder tool socket',(.78,.26,2.12),(.91,.28,1.94),.085,brass,.06)
for sign in [-1,1]:tube('Precision laser solder needle',(.91+sign*.055,.28,1.94),(1.08+sign*.14,.29,1.32),.026,light,.004)
root=bpy.data.objects.new('ConstructionDroidRig',None);s.collection.objects.link(root)
for group,objects in parts.items():
 for ob in objects:ob.parent=root;ob['scitek_component']=group
def pivot(n,p):
 ob=bpy.data.objects.new(n,None);s.collection.objects.link(ob);ob.parent=root;ob.location=p;pivots.append(ob);return ob
heavy_pivot=pivot('HeavyGripPivot',heavy_centre);light_pivot=pivot('LightArmPivot',(.94,-.21,1.83));welder_pivot=pivot('WelderHeadPivot',(0,-.31,.80))
bpy.context.view_layer.update()
def parent_keep(ob,parent):ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
for ob in parts['heavy-manipulator']:parent_keep(ob,heavy_pivot)
for ob in light_parts:parent_keep(ob,light_pivot)
for ob in welder_parts:parent_keep(ob,welder_pivot)
sparkmat=bpy.data.materials.new('Warm welding sparks');sparkmat.use_nodes=True;sparkmat.diffuse_color=(1,.45,.025,1);bs=sparkmat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=sparkmat.diffuse_color;bs.inputs['Emission Color'].default_value=sparkmat.diffuse_color;bs.inputs['Emission Strength'].default_value=1;bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0
for i in range(32):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.015,location=(0,-.31,.80));ob=bpy.context.object;g.finish(ob,sparkmat,f'Welding spark {i:02}');ob.parent=root;ob['scitek_solid_only_effect']=True;effects.append(ob)
sparks=list(effects)
arcmat=bpy.data.materials.new('Transient hot welding arc');arcmat.use_nodes=True;arcmat.diffuse_color=(1,.85,.55,1);bs=arcmat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=arcmat.diffuse_color;bs.inputs['Emission Color'].default_value=arcmat.diffuse_color;bs.inputs['Emission Strength'].default_value=2;bs.inputs['Specular IOR Level'].default_value=0
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.065,location=(0,-.31,.80));arc=bpy.context.object;g.finish(arc,arcmat,'Spot welding arc');arc.parent=root;arc['scitek_solid_only_effect']=True;effects.append(arc)
for f in range(1,122):
 t=(f-1)/120;s.frame_set(f);heavy_pivot.rotation_euler.z=math.tau*t;heavy_pivot.keyframe_insert('rotation_euler',frame=f)
 light_pivot.rotation_euler=(0,math.radians(-35)*math.sin(t*math.tau*2),math.radians(45)*math.sin(t*math.tau));light_pivot.keyframe_insert('rotation_euler',frame=f)
 welder_pivot.rotation_euler=(0,math.radians(15)*math.sin(t*math.tau*3),math.radians(50)*math.sin(t*math.tau*2));welder_pivot.keyframe_insert('rotation_euler',frame=f)
 for ob,a in heavy_jaws:ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion(Vector((-math.sin(a),math.cos(a),0)),.16*(1-math.cos(t*math.tau)));ob.keyframe_insert('rotation_quaternion',frame=f)
 for ob,sign in light_fingers:ob.rotation_euler.y=sign*.32*(1-math.cos(t*math.tau*2));ob.keyframe_insert('rotation_euler',frame=f)
 for i,ob in enumerate(sparks):
  emission=59+(0 if i<20 else 1+i%3);age=f-1-emission;life=14+(i*7)%26;active=0<=age<life
  # Inactive particles retract inside the opaque welding-head casing at unit
  # scale, avoiding an ill-conditioned tiny-scale bind pose in other engines.
  weight=max(1e-5,(1-age/life)**1.4) if active else 1
  ob.location=(.18+math.sin(i*2.4)*(.12+age*.025),-.41+math.cos(i*1.7)*(.025+age*.013),.55-.02*(i%7)-(.009+.0005*(i%20))*age-.00015*age*age) if active else (0,-.31,.80);ob.scale=(weight,)*3;ob.keyframe_insert('location',frame=f);ob.keyframe_insert('scale',frame=f)
 active_arc=59<=f-1<71;weight=max(1e-5,(1-(f-1-59)/12)**.5) if active_arc else 1;arc.location=(0,-.54,.78) if active_arc else (0,-.31,.80);arc.scale=(weight,)*3;arc.keyframe_insert('location',frame=f);arc.keyframe_insert('scale',frame=f)
animated=pivots+[x for x,a in heavy_jaws]+[x for x,sign in light_fingers]+effects
for ob in animated:
 if ob.animation_data:
  for fc in ob.animation_data.action.fcurves:
   for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_start=1;s.frame_end=121;s.render.fps=15;s.frame_set(1);bpy.context.view_layer.update()
def driven(ob):
 while ob and ob!=root:
  if ob.animation_data:return True
  ob=ob.parent
 return False
driven_meshes=[ob for objects in parts.values() for ob in objects if driven(ob)]+effects
rig_frames=[]
for f in range(1,121):
 s.frame_set(f);bpy.context.view_layer.update();rig_frames.append(dict(frame=f-1,mesh_root_matrices={ob.name:[value for row in (root.matrix_world.inverted()@ob.matrix_world) for value in row] for ob in driven_meshes},visible_effects=[ob.name for ob in effects if ob.scale.x>.01 and ((ob.name.startswith('Welding spark ') and ob.location.z<.70) or (ob.name=='Spot welding arc' and ob.location.y<-.5))]))
(out/'solid-animation-timeline.json').write_text(json.dumps(dict(frame_count=120,fps=15,root=root.name,body_turntable=False,format='Absolute row-major4x4 mesh transforms relative to root, Blender Z-up; replace bind transforms or derive delta using bind_root_matrices. GLB contains the authoritative rigid node hierarchy and single animation clip.',animated_mesh_nodes=[ob.name for ob in driven_meshes],bind_root_matrices=rig_frames[0]['mesh_root_matrices'],timeline=rig_frames),separators=(',',':'))+'\n',newline='\n')
s.frame_set(1);bpy.context.view_layer.update();component_names={group:[ob.name for ob in objects] for group,objects in parts.items()};effect_names=[ob.name for ob in effects]
fill_data=bpy.data.lights.new('Under canopy service fill','AREA');fill_data.energy=140;fill_data.shape='DISK';fill_data.size=3;fill=bpy.data.objects.new(fill_data.name,fill_data);s.collection.objects.link(fill);fill.location=(0,-4,1.3);fill.rotation_euler=(Vector((0,0,1.5))-fill.location).to_track_quat('-Z','Y').to_euler()

def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
bpy.context.view_layer.update()
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.005;data.bevel_resolution=0
    for o in objects:
        if o.type=='CURVE':
            for old in o.data.splines:
                sp=data.splines.new('POLY');sp.points.add(len(old.points)-1);sp.use_cyclic_u=old.use_cyclic_u
                for p,q in zip(sp.points,old.points):p.co=(*((root.matrix_world.inverted()@o.matrix_world)@Vector(q.co[:3])),1)
            continue
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
            for p,i in zip(spline.points,edge.vertices):p.co=(*((root.matrix_world.inverted()@o.matrix_world)@o.data.vertices[i].co),1)
    ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wire[group]=ob
g.camera.location=(5.2,-10,4.17);target=Vector((.2,0,1.62));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.3
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for ob in effects:ob.hide_render=mode!='solid'
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
render('solid.png')
# The source preview has articulated tool motion, not a body turntable.
s.frame_start=1;s.frame_end=121;s.render.fps=15;s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'construction-droids.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint,g.gold,g.red,roof_patch,sparkmat,arcmat]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('construction-droids.glb',[o for obs in parts.values() for o in obs]+effects+pivots)
rig_path=out/'solid-animation-timeline.json';rig=json.loads(rig_path.read_text());rig['source_blend_sha256']=hashlib.sha256((out/'construction-droids.blend').read_bytes()).hexdigest();rig['source_glb_sha256']=hashlib.sha256((out/'construction-droids.glb').read_bytes()).hexdigest();rig_path.write_text(json.dumps(rig,separators=(',',':'))+'\n',newline='\n')
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.0);target=Vector((0,0,1.7));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.1
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('construction-droids-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['heavy-manipulator','optical-sensor','spot-welder','light-manipulator','laser-solder-tool']):
    for name,ob in wire.items():ob.data.materials[0]=red if name==group else green
    angles={'heavy-manipulator':(10,-10,15),'optical-sensor':(-15,-20,-20),'spot-welder':(0,-15,-25),'light-manipulator':(0,0,0),'laser-solder-tool':(0,-15,170)}
    local_target=Vector({'heavy-manipulator':(-.83,-.48,1.30),'optical-sensor':(.24,-.40,1.76),'spot-welder':(0,-.33,1.06),'light-manipulator':(1.12,-.35,1.64),'laser-solder-tool':(1.01,.28,1.70)}[group])
    root.rotation_euler=[math.radians(x) for x in angles[group]];bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'heavy-manipulator':1.25,'optical-sensor':.75,'spot-welder':1.45,'light-manipulator':1.10,'laser-solder-tool':1.30}[group]
    render('highlight-'+group+'.png');export('construction-droids-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='construction-droids-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'construction-droids.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'construction-droids.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('construction-droids-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'construction-droids.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:construction-droids',legacy_index=7,source='_MA/ST07.256 + ST07.VID; _SCITEK/ST07.VID',components=component_names,solid_only_effect_nodes=effect_names,solid_animation=dict(type='articulated-rigid-nodes',frame_count=120,fps=15,body_turntable=False,timeline='solid-animation-timeline.json'),information_timeline_frames=705,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
