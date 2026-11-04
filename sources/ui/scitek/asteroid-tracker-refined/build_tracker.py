"""Asteroid Tracker: solid device and caption-bound wireframe/zoom variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# Referenced ST05 beige equipment stack: upper overhang, side CRT, two fans,
# left upper data bank and top calibration screw. No reference pixels are textures.
shell=g.material('Used beige computer casing',(.38,.29,.19),.35,.46)
light=g.material('Worn ivory controls',(.70,.63,.48),.25,.4)
dark=g.material('Recessed dark bronze grille',(.027,.023,.019),.3,.6)
blue=g.material('Aged navy fan and signal recess',(.015,.028,.070),.4,.4)
for mat in [shell,light]:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=95
        if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.003
parts={k:[] for k in ['chassis','user-interface','cooling-fans','data-storage','calibration-device']};role='chassis'
def mark(o):parts[role].append(o);return o
def box(n,p,d,m= shell,b=.025):return mark(g.box(n,p,d,m,b))
def tube(n,a,b,r,m,r2=None):return mark(g.tube(n,a,b,r,m,r2))
def screw(x,y,z):tube('Recessed case screw',(x,y+.012,z),(x,y-.012,z),.017,dark)
box('Lower calibration chassis',(0,0,.38),(1.65,1.10,.70))
box('Dark service separation',(0,0,.80),(1.70,1.13,.10),dark,.008)
box('Main storage and cooling cabinet',(0,0,1.58),(1.65,1.10,1.45))
box('Upper main electronics case',(.10,0,2.47),(1.45,1.12,.52))
role='data-storage'
box('Left upper data-bank module',(-.875,0,2.47),(.50,1.12,.52))
role='chassis'
for z in [.19,.60,1.0,2.20,2.64]:
    for x in [-.74,.74]:screw(x,-.563,z)
for j in range(9):box('Top cooling grille',(-.72+j*.16,0,2.738),(.055,.75,.012),dark,.003)
for x in [-.78,.78]:box('Long side service seam',(x,.15,1.60),(.014,.78,.80),dark,.003)
box('Rear service panel',(0,.565,1.65),(1.33,.023,1.0),light,.012)
for j in range(7):box('Rear exhaust grille',(0,.583,2.18-j*.05),(1.10,.012,.018),dark,.003)
role='user-interface'
box('CRT monitor side neck',(.88,-.03,2.35),(.37,.60,.34),shell)
box('CRT deep monitor housing',(1.14,-.12,2.35),(.65,.77,.61),light,.045)
box('CRT black recessed aperture',(1.14,-.519,2.35),(.47,.028,.42),dark,.022)
screen=box('Rounded rectangular dark CRT screen',(1.14,-.545,2.35),(.42,.028,.36),blue,.035)
for z in [2.22,2.31,2.39]:box('CRT faint trace',(1.12,-.567,z),(.27,.006,.008),g.gold,.002)
for j in range(4):box('CRT adjustment key',(1.43,-.30,2.18+j*.10),(.016,.05,.025),dark,.002)
role='chassis'
for j in range(3):box('Upper interface indicator',(.20+j*.13,-.575,2.48),(.035,.02,.20),light,.006)
for z in [2.0,2.18]:
    box('Front horizontal service recess',(0,-.575,z),(1.1,.04,.10),dark,.006)
    box('Pale bar inside recess',(-.10,-.606,z),(.78,.025,.035),light,.004)
box('Front activity light',(.61,-.58,2.0),(.04,.015,.04),g.red,.004)
role='cooling-fans'
for x in [.15,.57]:
    tube('Twin fan dark intake',(x,-.57,1.38),(x,-.60,1.38),.17,dark)
    tube('Twin fan navy rotor',(x,-.61,1.38),(x,-.625,1.38),.13,blue)
    tube('Fan central spindle',(x,-.63,1.38),(x,-.65,1.38),.035,light)
    for j in range(8):
        a=j*math.tau/8;v=(math.cos(a),math.sin(a));tube('Fan grille bar',(x+v[0]*.03,-.657,1.38+v[1]*.03),(x+v[0]*.13,-.657,1.38+v[1]*.13),.008,light)
    for z in [1.195,1.565]:box('Square fan intake frame',(x,-.656,z),(.37,.018,.012),dark,.003)
    for xx in [x-.185,x+.185]:box('Square fan intake frame',(xx,-.656,1.38),(.012,.018,.37),dark,.003)
role='chassis'
for z in [.24,.46]:
    box('Lower calibration slot',(-.36,-.575,z),(.63,.035,.075),dark,.006)
    for x in [.29,.48,.67]:box('Ivory calibration push key',(x,-.587,z),(.105,.04,.12),light,.014)
for x in [-.60,-.43]:
    for z in [1.15,1.31,1.47]:box('Status indicator',(x,-.58,z),(.04,.018,.04),light,.004)
# The final information close-up identifies a force-feedback calibration screw.
role='calibration-device'
tube('Countersunk calibration screw head',(0,0,2.70),(0,0,2.83),.04,light,.12)
tube('Calibration screw shaft',(0,0,2.22),(0,0,2.78),.037,light)
tube('Pointed calibration screw tip',(0,0,2.22),(0,0,2.12),.037,light,0)
thread=bpy.data.curves.new('Coarse calibration screw thread','CURVE');thread.dimensions='3D';thread.bevel_depth=.012;thread.bevel_resolution=2
spl=thread.splines.new('POLY');spl.points.add(216)
for i,p in enumerate(spl.points):
    a=i*math.tau*9/216;p.co=(.052*math.cos(a),.052*math.sin(a),2.24+.50*i/216,1)
ob=bpy.data.objects.new('Helical calibration screw thread',thread);s.collection.objects.link(ob);g.finish(ob,light,ob.name);mark(ob)
root=bpy.data.objects.new('TrackerRotor',None);s.collection.objects.link(root)
component_names={k:[o.name for o in obs] for k,obs in parts.items()}
for group,objects in parts.items():
    for o in objects:o.parent=root;o['scitek_component']=group
root.rotation_euler.z=math.radians(-12)
# ST05 static and preview images have a squat 104x101 silhouette.
root.scale.z=.72
# Shorten the cabinet, not the circular fan geometry or CRT proportions.
# Compensate these assemblies around their original mounting heights.
for objects,height in [(parts['cooling-fans'],1.38),([o for o in parts['user-interface'] if o.name.startswith('CRT') or o.name.startswith('Rounded rectangular dark CRT')],2.35)]:
    stretch=Matrix.Translation((0,0,height))@Matrix.Diagonal((1,1,1/.72,1))@Matrix.Translation((0,0,-height))
    for obj in objects:obj.data.transform(obj.matrix_basis.inverted()@stretch@obj.matrix_basis)
def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.005;data.bevel_resolution=0
    for o in objects:
        if o.type=='CURVE':
            for old in o.data.splines:
                spline=data.splines.new('POLY');spline.points.add(len(old.points)-1)
                for p,q in zip(spline.points,old.points):p.co=(*(o.matrix_basis@Vector(q.co[:3])),1)
            continue
        if o.type!='MESH':continue
        for edge in o.data.edges:
            if group=='calibration-device' and len(o.data.vertices) in [80,41]:
                a,b=[o.data.vertices[i].co for i in edge.vertices]
                if abs(a.z-b.z)>1e-6:
                    p=a if math.hypot(a.x,a.y)>1e-6 else b
                    meridian=int(round(math.atan2(p.y,p.x)/(math.tau/40)))%40
                    if meridian%5:continue
            spline=data.splines.new('POLY');spline.points.add(1)
            for p,i in zip(spline.points,edge.vertices):p.co=(*(o.matrix_basis@o.data.vertices[i].co),1)
    ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wire[group]=ob
g.camera.location=(5,-9,4.2);target=Vector((.25,0,1.1));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.2
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for role,obs in parts.items():
        for o in obs:o.hide_render=mode!='solid' or role=='calibration-device'
    for name,o in wire.items():o.hide_render=mode=='solid' or name=='calibration-device'
visibility('solid');render('solid.png')
# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(-12)+(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'asteroid-tracker.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,g.gold,g.red]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_format='GLB')
export('asteroid-tracker.glb',[o for role,obs in parts.items() if role!='calibration-device' for o in obs])
visibility('wire');s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.8);target=Vector((.25,0,1.05));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.0
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('asteroid-tracker-wireframe.glb',[o for name,o in wire.items() if name!='calibration-device'])
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['user-interface','cooling-fans','data-storage','calibration-device']):
    for name,o in wire.items():
        o.data.materials[0]=red if name==group else green
        o.hide_render=(name!=group) if group=='calibration-device' else name=='calibration-device'
    points=[o.matrix_world@v.co for o in parts[group] if o.type=='MESH' for v in o.data.vertices]
    centre=sum(points,Vector())/len(points);g.camera.location=(centre.x,-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=1.6 if group!='calibration-device' else .72
    render('highlight-'+group+'.png');export('asteroid-tracker-highlight-'+group+'.glb',[wire[group]] if group=='calibration-device' else [o for name,o in wire.items() if name!='calibration-device'])
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='asteroid-tracker-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),ortho_scale=g.camera_data.ortho_scale,isolated_detail=group=='calibration-device',placement_status='Authored schematic staging; original cabinet mounting position is unresolved' if group=='calibration-device' else 'Observed external component region'))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'asteroid-tracker.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'asteroid-tracker.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('asteroid-tracker-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'asteroid-tracker.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:asteroid-tracker',legacy_index=5,source='_MA/ST05.256 + ST05.VID; _SCITEK/ST05.VID',components=component_names,information_timeline_frames=564,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
