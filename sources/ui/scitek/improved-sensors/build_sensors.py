"""Improved Sensors: actual ST12 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# Actual ST12 preview and caption anchors84/225/366: central collector,
# two lateral shielding coils, upper calibration/indicator group.
shell=g.material('Used bronze-beige sensor shell',(.34,.27,.18),.45,.46)
light=g.material('Worn pale shielding and controls',(.65,.62,.50),.50,.36)
dark=g.material('Grime inside sensor seams',(.025,.020,.015),.25,.60)
blue=g.material('Dark signal indicator recess',(.018,.022,.026),.2,.55)
brass=g.material('Oxidised red collector traces',(.52,.040,.020),.45,.40)
markpaint=g.material('Faded reddish-brown case band',(.24,.09,.055),.2,.55)
for mat in [shell,light,brass,markpaint]:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=130
        if n.type=='BUMP':n.inputs['Strength'].default_value=.08;n.inputs['Distance'].default_value=.003
parts={k:[] for k in ['chassis','data-collector','shielding-coils','calibration-indicators']};role='chassis'
def mark(o):parts[role].append(o);return o
def box(n,p,d,m=shell,b=.018):return mark(g.box(n,p,d,m,b))
def tube(n,a,b,r,m,r2=None):return mark(g.tube(n,a,b,r,m,r2))
def mesh(n,verts,faces,mat):
    import bmesh
    data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(n,data);s.collection.objects.link(obj);g.finish(obj,mat,n);g.bevel(obj,.015);return mark(obj)
profile=[(-1,1.25),(-1,1.65),(-.95,1.95),(-.82,2.30),(-.62,2.60),(-.35,2.83),(.35,2.83),(.62,2.60),(.82,2.30),(.95,1.95),(1,1.65),(1,1.25)]
def hood(n,y0,y1):
    v=[(x,y,z) for y in [y0,y1] for x,z in profile];count=len(profile);f=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];return mesh(n,v,f,shell)
for i,(y0,y1) in enumerate([(-.69,-.235),(-.22,.22),(.235,.69)]):hood('Arched sensor casing panel '+str(i),y0,y1)
box('Lower sensor cabinet',(0,.05,.67),(1.25,1.1,1.25))
box('Faded lower cabinet band',(0,.05,.16),(1.27,1.12,.055),markpaint,.005)
for x in [-.53,.53]:box('Lower cabinet vertical seam',(x,-.511,.65),(.018,.018,.90),dark,.003)
box('Small top case fixing',(0,.06,2.87),(.07,.12,.08),light,.01)
role='data-collector'
box('Central data collector pedestal',(0,-.68,.66),(.60,.31,1.25))
# Wedge-shaped integrator panel slopes into the arched upper enclosure.
section=[(-.84,1.22),(-.84,1.50),(-.70,2.02),(-.60,2.02),(-.60,1.22)]
count=len(section);v=[(x,y,z) for x in [-.30,.30] for y,z in section];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];mesh('Sloped collector and integrator housing',v,faces,shell)
for x in [-.18,-.06,.06,.18]:
    for a,b in [((x,-.715,2.02),(x,-.77,1.77)),((x,-.77,1.77),(x,-.86,1.51))]:tube('Red data collector conductor',a,b,.017,brass)
    for y,z in [(-.715,2.02),(-.77,1.77),(-.86,1.51)]:mark(g.uv('Collector trace terminal',(x,y-.012,z),(.027,.018,.027),brass))
box('Collector faded lower marking',(0,-.846,.20),(.53,.015,.055),markpaint,.004)
role='shielding-coils'
for x in [-.43,.43]:
    data=bpy.data.curves.new('Lateral shielding coil','CURVE');data.dimensions='3D';data.bevel_depth=.010;data.bevel_resolution=3;sp=data.splines.new('POLY');sp.points.add(95);sp.use_cyclic_u=True
    # Rounded capsule winding: tube radius stays below bend radius, avoiding
    # the pinched/self-intersecting ends of a very narrow thick ellipse.
    for i,p in enumerate(sp.points):
        a=(i%48)*math.pi/47+(math.pi if i>=48 else 0);zc=1.65+(.258 if i<48 else -.258);p.co=(x+.022*math.cos(a),-.745,zc+.022*math.sin(a),1)
    obj=bpy.data.objects.new('Left shielding coil' if x<0 else 'Right shielding coil',data);s.collection.objects.link(obj);g.finish(obj,light,obj.name);mark(obj)
role='calibration-indicators'
box('Calibration control and output plate',(0,-.711,2.43),(.56,.040,.55),shell,.01)
for i in range(7):box('Pale vertical signal control',(-.18+i*.06,-.741,2.43),(.020,.018,.48),light,.003)
for sign in [-1,1]:
    for dx,z in [(0,2.16),(0,2.05),(.12,2.05),(0,1.94),(.12,1.94)]:mark(g.uv('Pale signal strength indicator',(sign*(.46+dx),-.715,z),(.018,.012,.018),light))
root=bpy.data.objects.new('SensorsRotor',None);s.collection.objects.link(root)
component_names={k:[o.name for o in obs] for k,obs in parts.items()}
for group,objects in parts.items():
    for o in objects:o.parent=root;o['scitek_component']=group
root.rotation_euler.z=math.radians(12)
root.scale.x=1.035
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
    if group=='chassis':
        # The source technical film presents a coarse surface grid, not a solid
        # flat face. These contours are display tessellation, not hidden hardware.
        def segment(a,b):
            sp=data.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
        for z in [1.40,1.65,1.95,2.20,2.45,2.65]:
            positive=sorted([(zz,xx) for xx,zz in profile if xx>=0])
            width=next((x0+(x1-x0)*(z-z0)/(z1-z0) for (z0,x0),(z1,x1) in zip(positive,positive[1:]) if z0<=z<=z1 and z1>z0),1.0)
            segment((-width,-.705,z),(width,-.705,z))
        for x,z in [(-.8,2.32),(-.4,2.78),(0,2.83),(.4,2.78),(.8,2.32)]:segment((x,-.705,1.25),(x,-.705,z))
    ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wire[group]=ob
g.camera.location=(-5,-9,5);target=Vector((0,0,1.4));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.55
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
render('solid.png')
# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(12)-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'improved-sensors.blend'))
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
export('improved-sensors.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.8);target=Vector((0,0,1.45));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.0
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('improved-sensors-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['data-collector','shielding-coils','calibration-indicators']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle={'data-collector':0,'shielding-coils':50,'calibration-indicators':0}[group]
    local_target=Vector({'data-collector':(0,-.74,1.07),'shielding-coils':(0,-.745,1.65),'calibration-indicators':(.06,-.72,2.30)}[group])
    root.rotation_euler=(0,0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'data-collector':2.25,'shielding-coils':1.15,'calibration-indicators':1.65}[group]
    render('highlight-'+group+'.png');export('improved-sensors-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='improved-sensors-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'improved-sensors.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'improved-sensors.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('improved-sensors-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'improved-sensors.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:improved-sensors',legacy_index=12,source='_MA/ST12.256 + ST12.VID; _SCITEK/ST12.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
