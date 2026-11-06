"""Hi-Energy Power Stores: actual ST11 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# Inspected ST11.256, all colour-preview phases and green/red information
# phases: ribbed power cylinder, twin coolants, bent input arm and bottom terminals.
shell=g.material('Used grey power-store casing',(.30,.29,.26),.6,.43)
light=g.material('Worn pale metallic collars',(.56,.53,.44),.65,.38)
dark=g.material('Dirt inside service seams',(.026,.022,.016),.2,.65)
blue=g.material('Blue emergency coolant cylinders',(.035,.15,.35),.35,.38)
brass=g.material('Aged brass heat-transfer ribs',(.48,.36,.08),.65,.4)
for mat in [shell,light,brass]:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=120
        if n.type=='BUMP':n.inputs['Strength'].default_value=.08;n.inputs['Distance'].default_value=.003
parts={k:[] for k in ['chassis','cooling-cylinders','probe-input-arms','power-terminals']};role='chassis'
def mark(o):parts[role].append(o);return o
def box(n,p,d,m=shell,b=.015):return mark(g.box(n,p,d,m,b))
def tube(n,a,b,r,m,r2=None):return mark(g.tube(n,a,b,r,m,r2))
tube('Lower cylindrical power chamber',(0,0,.34),(0,0,1.54),.61,shell)
tube('Upper cylindrical power chamber',(0,0,1.58),(0,0,2.72),.61,shell)
for z in [.34,.45,1.52,1.59,2.65,2.73]:tube('Used collar and recessed seam',(0,0,z),(0,0,z+.028),.625,dark if z in [1.52,1.59] else light)
cap=mark(g.uv('Convex power-store top',(0,0,2.74),(.60,.60,.15),shell))
box('Top service handle',(0,.11,2.90),(.12,.32,.17),shell)
for z0,z1 in [(.48,1.49),(1.65,2.62)]:
    for i in range(23):
        a=math.radians(-160+i*5);x=.62*math.cos(a);y=.62*math.sin(a)
        tube('Long vertical brass cooling rib',(x,y,z0),(x,y,z1),.023,brass)
for z in [.64,1.05,1.97]:
    box('Worn rear access panel',(0,.613,z),(.42,.032,.34),shell)
    for x in [-.17,.17]:tube('Recessed panel fixing',(x,.64,z-.12),(x,.65,z-.12),.013,dark)
box('Inset status display frame',(.06,-.598,2.22),(.42,.055,.42),light,.025)
box('Deep navy status glass',(.06,-.632,2.22),(.30,.025,.30),blue,.015)
for a,b in [((.08,-.65,2.34),(-.02,-.65,2.22)),((-.02,-.65,2.22),(.11,-.65,2.22)),((.11,-.65,2.22),(.01,-.65,2.10))]:tube('Pale power status mark',a,b,.012,light)
for obj in parts['chassis'][-5:]:obj.matrix_world=Matrix.Rotation(math.pi/2,4,'Z')@obj.matrix_world
role='cooling-cylinders'
for x in [-.14,.14]:
    tube('Twin blue emergency cooling cylinder',(x,.62,.88),(x,.62,1.44),.045,blue)
    tube('Coolant cylinder valve',(x,.62,1.44),(x,.62,1.53),.025,light,.018)
    tube('Coolant feed neck',(x,.62,1.53),(x,.53,1.57),.017,light)
role='probe-input-arms'
box('Probe input upper mounting',(.62,.05,1.50),(.17,.30,.17),light)
tube('Probe input descending arm',(.69,.05,1.47),(.69,.05,.93),.073,light)
tube('Probe input lower angled arm',(.69,.05,.93),(.89,-.08,.69),.073,light)
tube('Probe input terminal block',(.89,-.08,.69),(.94,-.15,.67),.10,shell)
for x in [.86,.95]:tube('Probe data pickup contact',(x,-.15,.66),(x,-.24,.62),.022,g.red)
role='power-terminals'
for x in [-.19,.19]:
    tube('Twin power terminal collar',(x,0,.34),(x,0,.23),.09,light)
    tube('Twin power terminal pin',(x,0,.23),(x,0,.06),.055,light)
root=bpy.data.objects.new('PowerStoreRotor',None);s.collection.objects.link(root)
component_names={k:[o.name for o in obs] for k,obs in parts.items()}
for group,objects in parts.items():
    for o in objects:o.parent=root;o['scitek_component']=group
root.rotation_euler.z=math.radians(-12)
def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.005;data.bevel_resolution=0
    for o in objects:
        if o.type!='MESH':continue
        # The original technical film shows a readable chamber cage, not every
        # small extruded heat-transfer fin. The solid model retains all ribs.
        if 'Long vertical brass cooling rib' in o.name:continue
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
g.camera.location=(5,-9,5);target=Vector((.25,0,1.4));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.2
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
render('solid.png')
# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(-12)+(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'hi-energy-power-stores.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,g.gold,g.red]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_format='GLB')
export('hi-energy-power-stores.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.8);target=Vector((.25,0,1.45));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.0
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('hi-energy-power-stores-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['cooling-cylinders','probe-input-arms','power-terminals']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    points=[o.matrix_world@v.co for o in parts[group] if o.type=='MESH' for v in o.data.vertices]
    centre=sum(points,Vector())/len(points);g.camera.location=(centre.x,-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=1.6 if group!='calibration-device' else 1.15
    render('highlight-'+group+'.png');export('hi-energy-power-stores-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='hi-energy-power-stores-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'hi-energy-power-stores.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'hi-energy-power-stores.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('hi-energy-power-stores-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'hi-energy-power-stores.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:hi-energy-power-stores',legacy_index=11,source='_MA/ST11.256 + ST11.VID; _SCITEK/ST11.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
