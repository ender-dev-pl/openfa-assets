"""Editable multi-scene reconstruction of original intro frames 0..412.
A: ship/galaxy. B: asteroid field. C: surface and mechanical boots. D: vector end-card.
"""
import bpy,math,json,random,hashlib,shutil
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.noise import fractal,noise_vector
p=Path(__file__).resolve().parent;rng=random.Random(412);A=bpy.context.scene;A.name='A — Ship and galaxy';A.frame_end=329
oldroot=next(o for o in A.objects if o.name.startswith('SHIP —'));A.frame_set(302);lastloc=oldroot.location.copy();lastq=oldroot.rotation_quaternion.copy();camq=A.camera.matrix_world.to_quaternion()
for f in range(303,330):
 t=(f-302)/27;oldroot.location=lastloc+camq@Vector((t*1.4,t*.2,-t*3.5));oldroot.rotation_quaternion=lastq;oldroot.keyframe_insert('location',frame=f);oldroot.keyframe_insert('rotation_quaternion',frame=f)
for fc in oldroot.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
next(o for o in A.objects if o.name.startswith('Next dissolve —')).hide_render=True
vis=next(o for o in A.objects if o.name.startswith('Spiral galaxy —')).active_material.node_tree.nodes['Shot dissolve']
# Keep the old scene fully visible through the actual A/B dissolve, rather than fading a placeholder cloud.
nt=vis.id_data
if nt.animation_data:
 for fc in list(nt.animation_data.action.fcurves):
  if fc.data_path==vis.outputs[0].path_from_id('default_value'):
   for idx in range(len(fc.keyframe_points)-1,-1,-1):
    if fc.keyframe_points[idx].co.x>=289:fc.keyframe_points.remove(fc.keyframe_points[idx])
for f,v in [(289,1),(329,1)]:vis.outputs[0].default_value=v;vis.outputs[0].keyframe_insert('default_value',frame=f)
A['role']='Outgoing ship/galaxy shot; dissolve to independent asteroid scene at frames 289..329.'

def activate(s):bpy.context.window.scene=s

def coll(s,name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);return c

def move(obj,c):
 for old in list(obj.users_collection):old.objects.unlink(obj)
 c.objects.link(obj);return obj

def empty(c,name):
 o=bpy.data.objects.new(name,None);c.objects.link(o);return o

def mesh(c,name,verts,faces,mat=None):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);c.objects.link(o)
 if mat:o.data.materials.append(mat)
 return o

def mat(name,color,metal=0,rough=.8,worn=True,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if emission:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
 if worn:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=8;tex.inputs['Detail'].default_value=3
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.26;ramp.color_ramp.elements[0].color=(*[v*.18 for v in color],1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(*[min(1,v*1.65) for v in color],1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
  fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=55;fine.inputs['Detail'].default_value=2;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.36;bump.inputs['Distance'].default_value=.07;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
 return m

def scene(name,start,end):
 s=bpy.data.scenes.new(name);s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.10;s.cycles.adaptive_min_samples=4;s.cycles.use_denoising=True;s.render.fps=24;s.frame_start=start;s.frame_end=end;s.render.resolution_x=640;s.render.resolution_y=262;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world=bpy.data.worlds.new(name+' / space');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.003,.006,.009,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.08;activate(s);return s

def camera(s,c,loc,target,lens=45):
 data=bpy.data.cameras.new(s.name+' lens');data.lens=lens;data.sensor_fit='HORIZONTAL';data.clip_end=2500;o=bpy.data.objects.new(s.name+' camera',data);c.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o;bpy.context.view_layer.update();return o

def light(c,name,loc,power,color,size=10,kind='AREA'):
 d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
 if kind=='AREA':d.shape='DISK';d.size=size
 if kind=='SUN':d.angle=.12
 o=bpy.data.objects.new(name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler();return o

def stars(s,c,cam):
 seed=random.Random(163);verts=[];faces=[]
 for i in range(150):
  x=seed.uniform(-390,390);y=seed.uniform(-160,160);z=-1000;rad=seed.uniform(.18,.8)*(2 if i%31==0 else 1);base=len(verts)
  for dx,dy in [(-rad,-rad),(rad,-rad),(rad,rad),(-rad,rad)]:verts.append(cam.matrix_world@Vector((x+dx,y+dy,z)))
  faces.append((base,base+1,base+2,base+3))
 m=mat(s.name+' / distant stars',(.30,.40,.48),worn=False,emission=1.8);mesh(c,'Distant star field / independent geometry',verts,faces,m)

def cube(c,name,loc,scale,material,bevel=.05,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=2,location=loc);o=move(bpy.context.object,c);o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if material:o.data.materials.append(material)
 if bevel:mod=o.modifiers.new('Worn rounded edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if parent:o.parent=parent
 return o

def cylinder(c,name,loc,radius,depth,material,parent=None,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=move(bpy.context.object,c);o.name=name;o.data.materials.append(material)
 for face in o.data.polygons:face.use_smooth=True
 if parent:o.parent=parent
 return o

B=scene('B — Independent asteroid field',289,429);bc=coll(B,'B / rocks, ship and cold starlight');bcam=camera(B,bc,(0,-60,12),(0,0,12));light(bc,'Asteroid cold key',(-25,-35,55),3.0,(.31,.67,.83),kind='SUN');light(bc,'Asteroid soft fill',(0,-58,18),300,(.10,.30,.42),20);stars(B,bc,bcam)
rockmat=mat('Asteroids / fractured cyan-black stone',(.08,.19,.23),.12,.91)
ramp=next(n for n in rockmat.node_tree.nodes if n.type=='VALTORGB');ramp.color_ramp.elements[0].position=.42;ramp.color_ramp.elements[0].color=(.002,.009,.012,1);ramp.color_ramp.elements[1].position=.57;ramp.color_ramp.elements[1].color=(.11,.28,.34,1)
for n in rockmat.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Strength'].default_value=.85;n.inputs['Distance'].default_value=.22
rockdata=[]
for j in range(12):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1);o=move(bpy.context.object,bc);o.name=f'Craggy asteroid prototype {j:02d}'
 for v in o.data.vertices:
  vec=v.co.copy();warp=noise_vector(vec*3+Vector((j*1.7,0,0)));v.co=vec*(1+.24*warp.x+.10*warp.y);v.co.z*=.75
 o.data.materials.append(rockmat);rockdata.append(o.data);bpy.data.objects.remove(o,do_unlink=True)
for i in range(65):
 depth=rng.uniform(25,150);o=bpy.data.objects.new(f'Asteroid {i:03d}',rockdata[i%12]);bc.objects.link(o);o.location=(rng.uniform(-.38,.38)*depth,depth-60,12+rng.uniform(-.15,.15)*depth);radius=rng.uniform(.12,.65)*(depth/60)**.6;o.scale=(radius,radius*rng.uniform(.8,1.4),radius*rng.uniform(.6,1.0));o.rotation_euler=[rng.uniform(0,6.28) for _ in range(3)]
for i,loc,scale in [(0,(2.5,-37,7.6),(5.5,4.5,2.6)),(1,(-8,-40,9.1),(3.7,3.6,2.2))]:
 o=bpy.data.objects.new('Foreground hero asteroid '+str(i),rockdata[i]);bc.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler=(.2,.3,.4+i)
# Independent copy of the editable ship, distant in this shot. Display-basis correction
# applies only to this inherited model; newly modelled rock geometry uses physical proportions.
basis=empty(bc,'B / inherited ship display basis');basis.parent=bcam;basis.scale=(1,262/560,1);copies={};A.frame_set(302)
for o in [oldroot]+[o for o in A.objects if o.parent==oldroot]:
 q=o.copy();bc.objects.link(q);copies[o]=q
for old,q in copies.items():q.parent=copies.get(old.parent,basis)
ship=copies[oldroot];ship.name='B / distant twin-engine ship';ship.animation_data_clear();ship.rotation_mode='QUATERNION';last=json.loads((p.parent/'first-scene-v7-steady-flight/steady-poses.json').read_text())['poses'][-1];x,y,z,w=last['rotation'];ship.rotation_quaternion=Quaternion((w,x,y,z));mean=ship.rotation_quaternion@Vector((0,-2.78*.78,0))
for n,u,v,depth in [(144,264,185,58),(164,266,185,63),(184,272,184,77),(202,282,184,91),(214,330,184,110)]:
 tx=(u-160)/400*depth;ty=-(v-140)/400*depth;ship.location=(tx-mean.x,ty-mean.y,-depth-mean.z);ship.keyframe_insert('location',frame=n*2+1)
for fc in ship.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
B['role']='Independent static asteroid-field shot with small receding ship. Outgoing to surface flight around original frames 198..214.'

C=scene('C — Surface flight and mechanical footprint',397,777);cc=coll(C,'C / eroded terrain, machinery and boots');ccam=camera(C,cc,(0,-65,22),(0,0,8));light(cc,'Surface raking cold sunlight',(-30,-35,55),3.1,(.63,.79,.84),kind='SUN');light(cc,'Surface dim sky fill',(0,-10,30),650,(.14,.29,.36),25);stars(C,cc,ccam)
terrainmat=mat('Terrain / worn fractured pale basalt',(.23,.34,.36),.04,.96)
# High contrast ridge/grain shading reconstructed from the legacy blue-white landscape.
nt=terrainmat.node_tree;n=nt.nodes;l=nt.links;bs=n.get('Principled BSDF');coord=n.new('ShaderNodeTexNoise');coord.inputs['Scale'].default_value=5.5;coord.inputs['Detail'].default_value=5;coord.inputs['Roughness'].default_value=.8;ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.44;ramp.color_ramp.elements[0].color=(.006,.012,.016,1);ramp.color_ramp.elements[1].position=.57;ramp.color_ramp.elements[1].color=(.48,.61,.63,1);l.new(coord.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
geom=n.new('ShaderNodeNewGeometry')
for node in n:
 if node.type=='TEX_NOISE':l.new(geom.outputs['Position'],node.inputs['Vector'])
coord.inputs['Scale'].default_value=2.5
def height(x,y):
 f=fractal(Vector((x*.13,y*.13,3.8)),.78,2.05,4);small=fractal(Vector((x*.55,y*.55,8.2)),.8,2,3);r=math.sqrt(x*x+y*y);h=1.9*f+.25*small+2.6*math.exp(-((r-7.5)/1.7)**2)-1.3*math.exp(-(r/5.5)**4);flat=math.exp(-(r/3.7)**8);return h*(1-flat)-1.12*flat
verts=[];faces=[];N=220;M=240
for j in range(M+1):
 y=-30+j*85/M
 for i in range(N+1):
  x=-42+i*84/N;verts.append((x,y,height(x,y)))
for j in range(M):
 for i in range(N):
  a=j*(N+1)+i;faces.extend([(a,a+1,a+N+2),(a,a+N+2,a+N+1)])
terrain=mesh(cc,'Actual displaced basalt surface / editable mesh',verts,faces,terrainmat)
for face in terrain.data.polygons:face.use_smooth=True
rust=mat('Distant warm machinery / oxidised copper',(.24,.095,.047),.62,.48);cap=mat('Warm machinery cap lights',(.7,.26,.10),worn=False,emission=2)
cube(cc,'Distant machinery base',(5.7,10.3,.4),(1.2,.8,.3),rust)
for i in range(3):
 cylinder(cc,'Distant glowing column '+str(i),(5+i*.65,10.3,1.7+i*.12),.22,2.8,rust);cylinder(cc,'Column worn light cap '+str(i),(5+i*.65,10.3,3.15+i*.12),.24,.15,cap)
steel=mat('Footprint / battered pale alloy',(.24,.32,.34),.46,.64);ink=mat('Recessed brand outlines',(.012,.020,.022),.5,.48);stripe=mat('Sole grooves / dark worn alloy',(.035,.055,.06),.65,.57)
# The static sole-shaped imprint remains when the mechanical feet lift out of shot.
outline=[(-1.5,-2.0),(-2.0,-1.45),(-2.2,-.4),(-2.25,.9),(-1.7,1.9),(-.9,2.2),(.9,2.2),(1.7,1.9),(2.25,.9),(2.2,-.4),(2,-1.45),(1.5,-2.0)]
plate=mesh(cc,'Sole-shaped embossed Tetra Corp imprint',[(x,y,-1.08) for x,y in outline],[tuple(reversed(range(len(outline))))],steel);solid=plate.modifiers.new('Stamp depth','SOLIDIFY');solid.thickness=.12;bevel=plate.modifiers.new('Rounded worn imprint edge','BEVEL');bevel.width=.08;bevel.segments=2
for y in [-1.75,-1.55,1.4,1.6,1.8]:cube(cc,'Imprint transverse tread groove',(0,y,-1.0),(1.70,.022,.014),stripe,.008)
logo=json.loads((p/'tetra-outline.json').read_text());cx=(logo['bbox'][0]+logo['bbox'][2])/2;cy=(logo['bbox'][1]+logo['bbox'][3])/2

def logo_curve(c,name,material,scale=1,z=0):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='2D';curve.resolution_u=2;curve.fill_mode='BOTH';curve.extrude=.006;curve.bevel_depth=.002;curve.bevel_resolution=1
 for loop in logo['loops']:
  spline=curve.splines.new('POLY');spline.points.add(len(loop)-1)
  for point,(x,y) in zip(spline.points,loop):point.co=((x-cx)/30*scale,(cy-y)*(262/560)/30*scale,0,1)
  spline.use_cyclic_u=True
 for rx,ry in [(.34,.37),(.12,.37)]:
  for sign,delta in [(1,0),(-1,-.018)]:
   spline=curve.splines.new('POLY');spline.points.add(63)
   for j,point in enumerate(spline.points):
    angle=sign*j*2*math.pi/64;point.co=((1.5+(rx+delta)*math.cos(angle))*scale,(.765+(ry+delta)*math.sin(angle))*scale,0,1)
   spline.use_cyclic_u=True
 obj=bpy.data.objects.new(name,curve);c.objects.link(obj);obj.location.z=z;curve.materials.append(material);return obj
emboss=logo_curve(cc,'Editable traced brand / engraved imprint',ink,.92,-.982);emboss.location.y=.0
bootmat=mat('Mechanical boots / dirty grey armour',(.14,.20,.23),.63,.43);joint=mat('Boot soles / worn black metal',(.012,.021,.025),.55,.52);trim=mat('Boot edge seams / pale metal',(.29,.38,.40),.70,.44)
boots=[]
for side in [-1,1]:
 root=empty(cc,'Mechanical '+('left' if side<0 else 'right')+' boot / separate rig');boots.append(root)
 foot=cube(cc,'Heavy black toe and sole',(0,0,0),(1.1,1.85,.52),joint,.22,root)
 cylinder(cc,'Lower mechanical shin',(0,-.35,3.4),.68,5.4,bootmat,root);cylinder(cc,'Worn ankle cuff',(0,-.35,1.0),.84,.5,trim,root)
 cube(cc,'Ankle rear armour',(0,-.8,1.45),(.77,.55,.64),bootmat,.22,root)
 for x in [-.65,.65]:cube(cc,'Shin vertical seam',(x,-.48,3.35),(.025,.035,2.4),joint,.005,root)
 for f,loc,rot in [(553,(side*3.8,2.5,12),0),(581,(side*2.0,.7,5),.07*side),(609,(side*1.6,.1,.65),0),(633,(side*1.6,.1,-.6),0),(649,(side*1.6,.1,-.6),0),(677,(side*3.5,2.3,8),-.15*side),(701,(side*7,6,18),-.2*side)]:
  # A short offset between the two feet gives a deliberate weight-bearing step.
  frame=f+(10 if side<0 else 0);root.location=loc;root.rotation_euler=(rot,.04*side,0);root.keyframe_insert('location',frame=frame);root.keyframe_insert('rotation_euler',frame=frame)
 for fc in root.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
# Camera flies above the surface, then looks down onto the stamped logo.
for n,loc,target in [(198,(0,-65,22),(0,0,8)),(212,(0,-45,14),(0,0,3)),(228,(0,-32,10),(0,2,0)),(250,(0,-20,9),(0,16,2)),(275,(0,-13,7),(0,12,1.5)),(290,(0,-9,6),(0,8,1)),(320,(0,-6.5,8),(0,0,-.8)),(350,(0,-3,13),(0,0,-1)),(370,(0,-1.4,13.7),(0,0,-1)),(388,(0,-1.1,13.7),(0,0,-1))]:
 ccam.location=loc;ccam.rotation_euler=(Vector(target)-ccam.location).to_track_quat('-Z','Y').to_euler();ccam.keyframe_insert('location',frame=n*2+1);ccam.keyframe_insert('rotation_euler',frame=n*2+1)
for fc in ccam.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
C['role']='Reference-guided approximation of terrain flight, large mechanical feet and embossed sole logo. Separate editable geometry, no background video projection.'

D=scene('D — Tetra Corp copper outline and fade',737,826);dc=coll(D,'D / traced vector logo');dcam=camera(D,dc,(0,0,10),(0,0,0));dcam.data.type='ORTHO';dcam.data.ortho_scale=10.8;D.world.node_tree.nodes['Background'].inputs[0].default_value=(.0008,.00005,.00003,1);D.world.node_tree.nodes['Background'].inputs[1].default_value=1
copper=bpy.data.materials.new('Copper outline / controlled final fade');copper.use_nodes=True;cn=copper.node_tree.nodes;cl=copper.node_tree.links;cn.clear();em=cn.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.20,.055,.008,1);out=cn.new('ShaderNodeOutputMaterial');cl.new(em.outputs[0],out.inputs['Surface'])
for f,v in [(737,.8),(801,.8),(809,.7),(817,.30),(825,0),(826,0)]:em.inputs['Strength'].default_value=v;em.inputs['Strength'].keyframe_insert('default_value',frame=f)
endlogo=logo_curve(dc,'Tetra Corp / editable outlined lettering',copper,1,0);endlogo.location.x=-.236;endlogo.location.y=-.49
for f,v in [(737,1),(809,1),(825,0),(826,0)]:D.world.node_tree.nodes['Background'].inputs[1].default_value=v;D.world.node_tree.nodes['Background'].inputs[1].keyframe_insert('default_value',frame=f)
D.use_nodes=True;dn=D.node_tree.nodes;dl=D.node_tree.links;rl=dn.get('Render Layers');co=dn.get('Composite');gl=dn.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='MEDIUM';gl.threshold=.15;gl.size=6;dl.new(rl.outputs['Image'],gl.inputs['Image']);dl.new(gl.outputs['Image'],co.inputs['Image'])
D['role']='Editable legacy-traced copper outline logo, fading to black at original frame 412.'

# A native Blender video-sequencer master provides genuine scene-to-scene cross dissolves.
master=bpy.data.scenes.new('MASTER — First sequence through original frame 412');master.render.engine='CYCLES';master.render.fps=24;master.render.resolution_x=640;master.render.resolution_y=480;master.render.resolution_percentage=100;master.render.image_settings.file_format='PNG';master.frame_start=1;master.frame_end=826;master.render.use_sequencer=True;master.view_settings.view_transform='AgX';master.view_settings.look='AgX - Medium High Contrast';activate(master);ed=master.sequence_editor_create();seq=ed.strips if hasattr(ed,'strips') else ed.sequences
strips=[]
for name,s,channel,start in [('A / outgoing ship',A,1,1),('B / incoming asteroid field',B,2,289),('C / surface approach',C,4,397),('D / final copper logo',D,6,737)]:
 strip=seq.new_scene(name,s,channel,start);strip.scene_input='CAMERA';strips.append(strip)
# Scene strips can have different native image heights. Letterbox them by fitting width, never stretching Y.
for name,start,end,channel,a,b in [('A to B / original 144..164',289,330,3,strips[0],strips[1]),('B to C / original 198..214',397,430,5,strips[1],strips[2]),('C to D / original 368..388',737,778,7,strips[2],strips[3])]:
 effect=seq.new_effect(name=name,type='CROSS',channel=channel,frame_start=start,frame_end=end,input1=a,input2=b)
master['source_range_zero_based_inclusive']='0..412';master['transitions']='Independent scene dissolves: A/B 144..164, B/C 198..214, C/D 368..388 source frames.';master['reconstruction_limits']='Later terrain, asteroid placement and mechanical feet inferred from observed frames; traced vector logo is reference-derived. No legacy video used as a rendered background.'
master.frame_set(329);bpy.ops.wm.save_as_mainfile(filepath=str(p/'first-sequence-to-412.blend'))
manifest=dict(fps=24,frames=826,duration_seconds=826/24,source_range_inclusive=[0,412],scenes=[dict(name=s.name,start=s.frame_start,end=s.frame_end,resolution=[s.render.resolution_x,s.render.resolution_y]) for s in [A,B,C,D]],transitions=[dict(start=289,end=329,outgoing=A.name,incoming=B.name),dict(start=397,end=429,outgoing=B.name,incoming=C.name),dict(start=737,end=777,outgoing=C.name,incoming=D.name)])
(p/'sequence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Native scene previews (later assembled into 4:3 letterbox by MASTER).
(p/'preview').mkdir(exist_ok=True)
for s,n in [(B,176),(C,224),(C,272),(C,308),(C,350),(D,400)]:
 activate(s);s.frame_set(n*2+1);s.cycles.samples=8;s.render.filepath=str(p/'preview'/f'frame-{n:03d}.png');bpy.ops.render.render(write_still=True)
print('MULTI_SCENE_BUILD_FINISHED',flush=True)
