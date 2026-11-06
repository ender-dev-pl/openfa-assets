"""Mk2 Mine: actual ST00 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# Actual ST00 sprite and colour film; caption anchors84/225/366 establish
# slurry ports, four bottom drill assemblies and upper coolant connectors.
shell=g.material('Used pale mining alloy',(.43,.43,.37),.55,.45)
light=g.material('Worn silver collars',(.62,.60,.49),.60,.40)
dark=g.material('Grime in drill joints',(.025,.024,.019),.3,.65)
blue=g.material('Recessed graphite carbon cutting face',(.13,.13,.14),.2,.55)
brass=g.material('Used olive mining casing',(.25,.26,.13),.35,.50)
markpaint=g.material('Oxidised coolant socket interior',(.13,.055,.035),.25,.65)
for mat in [shell,light,brass,markpaint]:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=85
        if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.004
parts={k:[] for k in ['chassis','slurry-recovery-ports','drill-assemblies','coolant-connectors']};role='chassis'
def mark(o):parts[role].append(o);return o
def tube(n,a,b,r,m,r2=None):return mark(g.tube(n,a,b,r,m,r2))
def lathe(n,profile,mat,xy=(0,0),segments=32):
    # Closed radial shell with explicit horizontal contour rings for technical views.
    import bmesh
    verts=[(xy[0]+r*math.cos(i*math.tau/segments),xy[1]+r*math.sin(i*math.tau/segments),z) for z,r in profile for i in range(segments)]
    faces=[tuple(reversed(range(segments))),tuple(range((len(profile)-1)*segments,len(profile)*segments))]
    for j in range(len(profile)-1):
        for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    data=bpy.data.meshes.new(n);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(n,data);s.collection.objects.link(obj);g.finish(obj,mat,n);return mark(obj)
lathe('Upper coolant casing',[(3.61,.43),(3.78,.46),(4.02,.45),(4.27,.41),(4.43,.32),(4.53,.20)],shell)
for z,r in [(3.66,.45),(3.79,.465),(4.24,.42),(4.47,.28)]:lathe('Upper casing horizontal band',[(z-.014,r),(z+.014,r)],light)
lathe('Upper cap service boss',[(4.53,.18),(4.59,.18),(4.60,.14),(4.65,.14)],light)
lathe('Equatorial pale clamp collar',[(3.42,.52),(3.62,.52)],light)
for i in range(16):
    a=i*math.tau/16;tube('Collar worn fastener',(.522*math.cos(a),.522*math.sin(a),3.47),(.524*math.cos(a),.524*math.sin(a),3.56),.018,dark)
lathe('Olive slurry pressure chamber',[(2.50,.27),(2.62,.42),(2.85,.55),(3.12,.62),(3.37,.56),(3.42,.48)],brass)
for i in range(6):
    a=i*math.tau/6
    ob=mark(g.uv('Pale pressure chamber brace',(.54*math.cos(a),.54*math.sin(a),2.90),(.10,.065,.34),light));ob.rotation_euler.z=a-math.pi/2
lathe('Long alloy drill drive barrel',[(.83,.19),(1.02,.30),(1.28,.34),(2.45,.34),(2.65,.28)],shell)
for z in [1.12,1.31,2.40]:lathe('Drive barrel circumferential seam',[(z-.014,.345),(z+.014,.345)],dark)
for i in range(12):
    a=i*math.tau/12;tube('Long drill drive barrel rib',(.345*math.cos(a),.345*math.sin(a),1.30),(.345*math.cos(a),.345*math.sin(a),2.39),.022,light)
# Four independent shafts are visible below the pressure chamber and terminate
# in four separate multi-headed olive/carbon cutting assemblies.
for i in range(4):
    a=i*math.tau/4+math.pi/4;xy=(.34*math.cos(a),.34*math.sin(a))
    tube('Independent drill drive shaft',(xy[0],xy[1],.64),(xy[0],xy[1],1.04),.065,dark)
role='slurry-recovery-ports'
for sign in [-1,1]:
    tube('Slurry recovery flared manifold',(sign*.44,0,3.26),(sign*.73,0,3.28),.21,brass,.13)
    tube('Slurry recovery port rim',(sign*.73,0,3.28),(sign*.83,0,3.28),.14,light)
    tube('Slurry recovery dark port mouth',(sign*.831,0,3.28),(sign*.84,0,3.28),.10,dark)
role='drill-assemblies'
for i in range(4):
    a=i*math.tau/4+math.pi/4;xy=(.34*math.cos(a),.34*math.sin(a))
    lathe('Independent multi-head drill '+str(i),[(.10,.07),(.25,.21),(.46,.285),(.65,.24),(.76,.13)],brass,xy,24)
    lathe('Carbon cutting crown '+str(i),[(.045,.025),(.12,.10),(.28,.23),(.38,.27)],blue,xy,24)
    for tooth in range(4):
        b=tooth*math.tau/4
        x=xy[0]+.17*math.cos(b);y=xy[1]+.17*math.sin(b)
        lathe('Carbon drill cutting tip',[(.09,.015),(.20,.075),(.30,.065)],blue,(x,y),12)
role='coolant-connectors'
for i,a in enumerate([-math.pi/2-.45,math.pi/2-.45]):
    z=4.06;v=Vector((math.cos(a),math.sin(a),0));centre=Vector((v.x*.471,v.y*.471,z))
    # Recessed socket with a metal annulus and dark oxidised open centre.
    data=bpy.data.curves.new('Coolant connector annulus','CURVE');data.dimensions='3D';data.bevel_depth=.018;data.bevel_resolution=2;sp=data.splines.new('POLY');sp.points.add(47);sp.use_cyclic_u=True
    tangent=Vector((-v.y,v.x,0))
    for j,p in enumerate(sp.points):
        b=j*math.tau/48;p.co=(*(centre+tangent*(.13*math.cos(b))+Vector((0,0,.13*math.sin(b)))),1)
    ob=bpy.data.objects.new('Coolant through-connector annulus '+str(i),data);s.collection.objects.link(ob);g.finish(ob,light,ob.name);mark(ob)
    tube('Coolant through-connector recessed bore',centre-v*.008,centre+v*.002,.105,markpaint)
root=bpy.data.objects.new('MineRotor',None);s.collection.objects.link(root)
component_names={k:[o.name for o in obs] for k,obs in parts.items()}
for group,objects in parts.items():
    for o in objects:o.parent=root;o['scitek_component']=group
root.rotation_euler.z=0
root.scale.x=1.06

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
g.camera.location=(5,-10,5);target=Vector((0,0,2.4));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.5
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
bpy.ops.wm.save_as_mainfile(filepath=str(out/'mk2-mine.blend'))
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
export('mk2-mine.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,3.5);target=Vector((0,0,2.4));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.5
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('mk2-mine-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['slurry-recovery-ports','drill-assemblies','coolant-connectors']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle={'slurry-recovery-ports':-25,'drill-assemblies':25,'coolant-connectors':0}[group]
    local_target=Vector({'slurry-recovery-ports':(.58,0,3.35),'drill-assemblies':(0,0,.44),'coolant-connectors':(0,0,4.06)}[group])
    root.rotation_euler=(math.radians(-30) if group=='coolant-connectors' else 0,math.radians(10) if group=='coolant-connectors' else 0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'slurry-recovery-ports':1.65,'drill-assemblies':1.75,'coolant-connectors':1.20}[group]
    render('highlight-'+group+'.png');export('mk2-mine-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='mk2-mine-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'mk2-mine.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'mk2-mine.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('mk2-mine-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'mk2-mine.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:mk2-mine',legacy_index=0,source='_MA/ST00.256 + ST00.VID; _SCITEK/ST00.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
