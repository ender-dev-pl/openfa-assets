"""Reference-guided B/C/D refining. Existing A and later shots remain untouched."""
import bpy,math,random,json,argparse,sys,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.noise import fractal,noise_vector
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--stage',choices=['asteroids','surface'],required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(a.input));bpy.context.preferences.filepaths.save_version=0
B=bpy.data.scenes['B — Independent asteroid field'];C=bpy.data.scenes['C — Surface flight and mechanical footprint'];D=bpy.data.scenes['D — Tetra Corp copper outline and fade'];rnd=random.Random(212)
def activate(s):bpy.context.window.scene=s

def material(name,color,metal=.1,rough=.8):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=26;t.inputs['Detail'].default_value=3;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.18;b.inputs['Distance'].default_value=.015;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal']);return m

def cube(name,loc,scale,mat,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=2);o=bpy.context.object;o.name=name;o.location=loc;o.scale=scale;o.data.materials.append(mat)
 if parent:o.parent=parent
 q=o.modifiers.new('Small worn edges','BEVEL');q.width=.035;q.segments=2;return o

def cylinder(name,loc,r,depth,mat,parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth);o=bpy.context.object;o.name=name;o.location=loc;o.data.materials.append(mat)
 if parent:o.parent=parent
 return o

def line(name,p,q,r,mat,parent=None):
 p,q=Vector(p),Vector(q);o=cylinder(name,(p+q)*.5,r,(q-p).length,mat,parent);o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler();return o
if a.stage=='asteroids':
 activate(B);B.frame_set(353);bpy.context.view_layer.update();cam=B.camera;rocks=[o for o in B.objects if o.type=='MESH' and o.name.startswith(('Asteroid ','Foreground hero asteroid'))];data={o.data for o in rocks}
 for j,d in enumerate(sorted(data,key=lambda d:d.name)):
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=1,use_grid_fill=True);bm.to_mesh(d);bm.free()
  for v in d.vertices:
   co=v.co.copy();n=co.normalized();f=fractal(co*9+Vector((j,2,5)),.75,2.1,4);v.co=co+n*(.08*f+.025*math.sin(co.z*24+co.x*7))
  for p in d.polygons:p.use_smooth=False
 # Screen anchors are measured in the corrected 640x262 active image at original frame 176.
 anchors=[(400,251,28,105),(-17,251,25,84),(501,35,90,17),(310,78,95,7),(286,157,73,10),(276,212,85,7),(185,153,120,4),(289,127,85,4),(173,67,100,5),(203,194,100,4),(250,17,110,4),(630,141,90,8),(342,164,100,6),(363,88,110,4),(153,213,100,7),(83,111,95,4),(53,29,100,5),(432,109,110,4),(570,73,120,4),(372,211,100,4),(47,180,110,5),(242,117,100,3),(139,101,100,3),(418,26,110,3),(602,215,100,5),(480,141,120,4),(117,161,100,3)]
 rocks=sorted(rocks,key=lambda o:o.name)
 for i,o in enumerate(rocks):
  o.hide_render=i>=len(anchors)
  if i>=len(anchors):continue
  u,v,depth,r=anchors[i];o.location=cam.matrix_basis@Vector(((u-320)*depth/800,-(v-131)*depth/800,-depth));s=r*depth/800;o.scale=(s,s*.95,s*1.05);o.rotation_euler=(rnd.random()*3,rnd.random()*3,rnd.random()*3)
 m=bpy.data.materials['Asteroids / fractured cyan-black stone'];ns=m.node_tree.nodes;ls=m.node_tree.links;bs=ns.get('Principled BSDF');noise=next(n for n in ns if n.type=='TEX_NOISE');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=5;r=next(n for n in ns if n.type=='VALTORGB');r.color_ramp.elements[0].position=.36;r.color_ramp.elements[0].color=(.002,.008,.01,1);r.color_ramp.elements[1].position=.68;r.color_ramp.elements[1].color=(.085,.22,.25,1)
 for n in ns:
  if n.type=='BUMP':n.inputs['Strength'].default_value=.65;n.inputs['Distance'].default_value=.1
 for m in bpy.data.materials:
  if m.name.startswith('B — Independent asteroid field / distant stars'):m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.12
 B['refining']='Screen-anchored rocky silhouettes, fractured mesh relief and dim cold starfield; reference frame 176.'
else:
 activate(C)
 terrain=next(o for o in C.objects if o.name.startswith('Actual displaced basalt'))
 for v in terrain.data.vertices:
  x,y=v.co.x,v.co.y;r=math.hypot(x,y);co=Vector((x*.11,y*.11,3.8));f=fractal(co,.78,2.0,4);ridge=2.4*math.exp(-((y-14-2*math.sin(x*.22))/3)**2);rim=2.2*math.exp(-((r-7.5)/1.6)**2);basin=-1.2*math.exp(-(r/5.5)**4);basecut=math.exp(-(((x-5.7)/2.5)**2+((y-10.3)/2.8)**2));flat=math.exp(-(r/3.6)**8);h=1.3*f+ridge+rim+basin;h=h*(1-basecut)+.2*basecut;v.co.z=h*(1-flat)-1.12*flat
 m=terrain.active_material;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');geom=next(x for x in n if x.type=='NEW_GEOMETRY');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=4;mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,.7,.35);l.new(geom.outputs['Position'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.34;ramp.color_ramp.elements[0].color=(.015,.027,.032,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(.25,.34,.36,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
 for node in n:
  if node.type=='BUMP':node.inputs['Strength'].default_value=.3;node.inputs['Distance'].default_value=.035
 # Model the warm industrial landmark as three separate finned towers on a landing slab.
 for o in C.objects:
  if o.name.startswith(('Distant machinery','Distant glowing column','Column worn light cap')):o.hide_render=True
 rust=material('Refined base / stained copper',(.24,.105,.065),.65,.5);steel=material('Refined base / dark structure',(.028,.035,.035),.6,.7);pad=material('Refined base / dusty apron',(.12,.17,.18),.2,.9);window=material('Refined base / warm lamps',(.85,.45,.36),.1,.4);bs=window.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.9,.4,.28,1);bs.inputs['Emission Strength'].default_value=2
 cube('Base / inset landing apron',(5.7,10.3,.1),(2.6,2.1,.15),pad)
 for i in range(3):
  root=bpy.data.objects.new('Base / tower '+str(i),None);C.collection.objects.link(root);root.location=(4.8+i*.85,10.3,.2);root.rotation_euler.y=-.13
  cube('Base / tower housing',(0,0,1.4),(.30,.38,1.4),rust,root)
  for side in [-1,1]:
   for z in [.5,.85,1.2,1.55,1.9]:cube('Base / radiator fin',(side*.34,0,z),(.10,.47,.035),steel,root)
   for z in [.55,1.35,2.25]:cube('Base / recessed service panel',(side*.15,-.39,z),(.09,.012,.21),steel,root)
  cube('Base / cap light',(0,-.02,2.83),(.24,.28,.04),window,root)
  for z in [1.2,2.4]:cube('Base / indicator',(0,-.405,z),(.075,.012,.055),window,root)
 for i in range(2):line('Base / overhead connecting pipe',(4.8+i*.85,10.5,1.8),(5.65+i*.85,10.5,1.8),.09,steel)
 # Carved sole silhouette: broad rounded toe, narrow heel, recessed lettering and raised bevels.
 plate=next(o for o in C.objects if o.name.startswith('Sole-shaped embossed'));outline=[(-1.2,-2.4),(-1.45,-1.5),(-1.9,-.4),(-2.1,.8),(-1.95,1.65),(-1.3,2.25),(0,2.5),(1.3,2.25),(1.95,1.65),(2.1,.8),(1.9,-.4),(1.45,-1.5),(1.2,-2.4)]
 d=bpy.data.meshes.new('Refined tapered sole relief');d.from_pydata([(x,y,-1.08) for x,y in outline],[],[tuple(reversed(range(len(outline))))]);d.materials.append(plate.active_material);plate.data=d
 for o in C.objects:
  if o.name.startswith('Imprint transverse'):o.scale.x*=.8
 logo=next(o for o in C.objects if o.name.startswith('Editable traced brand'));logo.data=logo.data.copy();logo.data.extrude=.024;logo.data.bevel_depth=.012;logo.data.bevel_resolution=2;logo.location.z=-.94
 raised=logo.copy();raised.data=logo.data.copy();C.collection.objects.link(raised);raised.name='Footprint / pale raised letter bevel';raised.data.materials.clear();raised.data.materials.append(plate.active_material);raised.data.bevel_depth=.004;raised.location.z=-.912
 for o in C.objects:
  if o.name.startswith(('Sole-shaped','Imprint transverse','Editable traced brand','Footprint / pale')):
   o.hide_render=True;o.keyframe_insert('hide_render',frame=625);o.hide_render=False;o.keyframe_insert('hide_render',frame=633)
 # Dirt-darkened shin panels and scratched toe caps remain independently editable.
 boot=material('Boot / worn panel steel',(.16,.22,.24),.45,.65);dark=material('Boot / dust in panel seams',(.012,.019,.021),.3,.85)
 for root in [o for o in C.objects if o.name.startswith('Mechanical ') and o.type=='EMPTY']:
  cube('Boot / raised front shin panel',(0,-1.04,3.4),(.46,.065,1.6),boot,root)
  for x in [-.43,.43]:
   for z in [2.1,3.5,4.7]:cylinder('Boot / panel rivet',(x,-1.12,z),.045,.035,dark,root).rotation_euler.x=math.pi/2
  for z in [2.4,4.2]:cube('Boot / scuffed panel seam',(0,-1.12,z),(.32,.01,.015),dark,root)
 C['refining']='Layered basalt ridges, inset warm industrial base, panelled machinery and tapered embossed footprint.'
a.out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(a.out));print('REFINED_STAGE_SAVED',a.stage)
