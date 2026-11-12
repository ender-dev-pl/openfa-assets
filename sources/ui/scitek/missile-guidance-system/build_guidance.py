"""Missile Guidance System: actual ST15 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST15: violet holographic globe, an open arched I/O strap and an armoured cup.
shell=g.material('Used green-grey guidance armour',(.30,.32,.23),.35,.61)
light=g.material('Worn pale guidance interface alloy',(.47,.47,.30),.45,.51)
dark=g.material('Accumulated grime in guidance joints',(.035,.034,.025),.15,.75)
blue=g.material('Translucent violet guidance glass',(.10,.065,.40),.05,.27)
brass=g.material('Faded guidance service markings',(.27,.23,.13),.3,.63)
markpaint=g.material('Faded red interface indicators',(.37,.09,.055),.1,.64)
for mat in [shell,light,brass]:
 for node in mat.node_tree.nodes:
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=90
  if node.type=='BUMP':node.inputs['Strength'].default_value=.10;node.inputs['Distance'].default_value=.003
blue.diffuse_color=(.10,.065,.40,.72);bs=blue.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.72;bs.inputs['Transmission Weight'].default_value=.18;bs.inputs['IOR'].default_value=1.35
parts={k:[] for k in ['chassis','holographic-sphere','targeting-io','armoured-computer-casing']};role='chassis'
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def box(n,loc,size,mat,b=.006):return mark(g.box(n,loc,size,mat,b))
def mesh(n,v,f,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def ring(n,z0,z1,rin,rout,mat,N=48):
 v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in [(z0,rout),(z1,rout),(z0,rin),(z1,rin)] for i in range(N)];f=[]
 for i in range(N):
  j=(i+1)%N;f.extend([(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(N+i,N+j,3*N+j,3*N+i),(j,i,2*N+i,2*N+j)])
 return mesh(n,v,f,mat)
ring('Bottom computer mounting plinth',.02,.18,.62,.84,shell)
ring('Base grime seam',.04,.075,.78,.845,dark)
role='armoured-computer-casing'
# Opposed skirts both have pointed faces (source updates0 and30). The raised
# side boundary creates the arch seen at quarter turns. Hidden seams are authored.
for front in [True,False]:
 N=32;v=[]
 for inner in [False,True]:
  radius=.89 if not inner else .81
  for upper in [False,True]:
   for i in range(N+1):
    a=(-math.pi if front else 0)+i*math.pi/N;low=.13+.43*abs(math.cos(a));v.append((radius*math.cos(a),radius*math.sin(a),1.10 if upper else low))
 stride=N+1;f=[]
 for i in range(N):f.extend([(i,i+1,stride+i+1,stride+i),(2*stride+i,3*stride+i,3*stride+i+1,2*stride+i+1),(stride+i,stride+i+1,3*stride+i+1,3*stride+i),(i,2*stride+i,2*stride+i+1,i+1)])
 f.extend([(0,stride,3*stride,2*stride),(N,2*stride+N,3*stride+N,stride+N)])
 mesh('Pointed front armour skirt' if front else 'Pointed rear armour skirt',v,f,shell)
ring('Computer upper armoured collar',.99,1.15,.75,.92,shell)
for i in range(12):
 a=i*math.tau/12;rad=Vector((math.cos(a),math.sin(a),0));tube('Case plate seam',tuple(rad*.897+Vector((0,0,.58))),tuple(rad*.897+Vector((0,0,.98))),.004,dark)
role='holographic-sphere'
globe=mark(g.uv('Translucent holographic sphere',(0,0,1.47),(.96,.96,.96),blue))
coremat=g.material('Holographic map muted violet',(.115,.075,.34),.02,.73)
core=mark(g.uv('Holographic map core',(0,0,1.47),(.925,.925,.925),coremat));map_materials=[coremat]
for i in range(5):
 mat=g.material('Holographic map region '+str(i),(.09+.009*i,.06+.007*i,.26+.021*i),.02,.73);map_materials.append(mat);core.data.materials.append(mat)
for face in core.data.polygons:
 p=face.center;face.material_index=(int((math.sin(p.x*8+p.z*4)+math.sin(p.y*7-p.z*5)+2)*1.45))%6
role='targeting-io'
ring('Broad guidance interface belt',1.10,1.58,.94,1.075,light)
ring('Belt dark lower joint',1.09,1.12,.95,1.08,dark)
# Curved strap has a true round through-hole, rather than a blue painted spot.
N=32;v=[]
for r in [1.005,1.045]:
 for side in [-1,1]:
  x=side*.14;reach=math.sqrt(r*r-x*x)
  for i in range(N+1):
   t=-math.pi/2+i*math.pi/N;v.append((x,reach*math.sin(t),1.47+reach*math.cos(t)))
stride=N+1;f=[]
for i in range(N):f.extend([(i,i+1,stride+i+1,stride+i),(2*stride+i,3*stride+i,3*stride+i+1,2*stride+i+1),(i,2*stride+i,2*stride+i+1,i+1),(stride+i,stride+i+1,3*stride+i+1,3*stride+i)])
f.extend([(0,stride,3*stride,2*stride),(N,2*stride+N,3*stride+N,stride+N)])
strap=mesh('Arched targeting interface strap',v,f,light)
normal=Vector((0,-math.sin(.85),math.cos(.85)));centre=Vector((0,0,1.47))+normal*1.025
cutter=g.tube('Temporary strap aperture cutter',centre-normal*.25,centre+normal*.25,.102,dark)
bpy.context.view_layer.objects.active=strap;mod=strap.modifiers.new('Round optical aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
box('Targeting data slot recess',(0,-.916,.91),(.51,.028,.13),dark)
for i in range(8):box('Small data connector '+str(i),(-.19+i*.055,-.94,.90),(.018,.025,.045),brass,.001)
for i in range(3):
 a=math.radians(-68);rad=Vector((math.cos(a),math.sin(a),0));z=1.23+i*.115;tube('Red I O status indicator',tuple(rad*1.077+Vector((0,0,z))),tuple(rad*1.092+Vector((0,0,z))),.023,markpaint)
# Explicit tiny scuffs and tarnish survive the portable PBR export. They are
# omitted from technical-display wire LOD, which describes construction only.
for i in range(28):
 a=i*2.399963;rad=Vector((math.cos(a),math.sin(a),0));z=1.16+(i%7)*.05;tangent=Vector((-rad.y,rad.x,0));centre=rad*1.079+Vector((0,0,z));tube('Wear belt edge scratch',tuple(centre-tangent*(.012+.003*(i%3))),tuple(centre+tangent*(.012+.003*(i%3))),.0025,dark if i%3 else brass)
role='armoured-computer-casing'
for i in range(12):
 a=i*2.399963;rad=Vector((math.cos(a),math.sin(a),0));z=.65+(i%4)*.05;centre=rad*.895+Vector((0,0,z));tube('Wear armour scuff',tuple(centre),tuple(centre+Vector((.014,-.008,.006))),.002,dark)
root=bpy.data.objects.new('GuidanceRotor',None);s.collection.objects.link(root)
component_names={k:[ob.name for ob in objects] for k,objects in parts.items()}
for group,objects in parts.items():
 for ob in objects:ob.parent=root;ob['scitek_component']=group
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
        if o.name.startswith(('Wear ','Holographic map core')):continue
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
                    if ring%2:continue
                else:
                    step=int(round(math.atan2(va.y,va.x)/(math.tau/48)))%48
                    if step%2:continue
            spline=data.splines.new('POLY');spline.points.add(1)
            for p,i in zip(spline.points,edge.vertices):p.co=(*(o.matrix_basis@o.data.vertices[i].co),1)
    ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wire[group]=ob
g.camera.location=(-4,-10,3.8);target=Vector((0,0,1.25));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=2.95
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
bpy.ops.wm.save_as_mainfile(filepath=str(out/'missile-guidance-system.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint,g.gold,g.red]+map_materials:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('missile-guidance-system.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.0);target=Vector((0,0,1.25));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=2.95
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('missile-guidance-system-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['holographic-sphere','targeting-io','armoured-computer-casing']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle=0
    local_target=Vector({'holographic-sphere':(0,0,1.45),'targeting-io':(0,0,1.45),'armoured-computer-casing':(0,-.1,.65)}[group])
    root.rotation_euler=(math.radians(90) if group=='holographic-sphere' else math.radians(35) if group=='targeting-io' else 0,0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'holographic-sphere':2.95,'targeting-io':2.95,'armoured-computer-casing':2.65}[group]
    render('highlight-'+group+'.png');export('missile-guidance-system-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='missile-guidance-system-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'missile-guidance-system.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'missile-guidance-system.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('missile-guidance-system-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'missile-guidance-system.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:missile-guidance-system',legacy_index=15,source='_MA/ST15.256 + ST15.VID; _SCITEK/ST15.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
