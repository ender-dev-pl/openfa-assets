"""Mk2 Deep Bore Mine: actual ST01 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST01: mushroom head, collar connector rows, one highlighted side probe,
# hanging cable loops and four bottom multi-headed drills.
shell=g.material('Used grey deep-bore alloy',(.38,.38,.32),.55,.48)
light=g.material('Worn pale gold deep-bore fittings',(.57,.54,.38),.6,.43)
dark=g.material('Deep bore grime and cable insulation',(.026,.025,.019),.25,.66)
blue=g.material('Graphite carbon drill crowns',(.13,.13,.14),.2,.55)
brass=g.material('Used olive deep-bore casing',(.25,.26,.13),.35,.50)
markpaint=g.material('Darkened connector interior',(.11,.09,.055),.25,.65)
for mat in [shell,light,brass,markpaint]:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=85
        if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.004
parts={k:[] for k in ['chassis','radio-seismic-probe','drill-assemblies','coolant-connectors']};role='chassis'
def mark(o):parts[role].append(o);return o
def tube(n,a,b,r,m,r2=None):return mark(g.tube(n,a,b,r,m,r2))
def lathe(n,profile,mat,xy=(0,0),segments=32):
    import bmesh
    # Offset the round hood's display meridians from the eight connector rays:
    # otherwise coincident green curves hide selected red lines from above.
    phase=.5 if n.startswith(('Broad mushroom','Mushroom head')) else 0
    vertices=[(xy[0]+r*math.cos((i+phase)*math.tau/segments),xy[1]+r*math.sin((i+phase)*math.tau/segments),z) for z,r in profile for i in range(segments)]
    faces=[tuple(reversed(range(segments))),tuple(range((len(profile)-1)*segments,len(profile)*segments))]
    for j in range(len(profile)-1):
        for i in range(segments):faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    data=bpy.data.meshes.new(n);data.from_pydata(vertices,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def path(n,points,r,mat,closed=False):
    data=bpy.data.curves.new(n,'CURVE');data.dimensions='3D';data.bevel_depth=r;data.bevel_resolution=2;sp=data.splines.new('POLY');sp.points.add(len(points)-1);sp.use_cyclic_u=closed
    for p,v in zip(sp.points,points):p.co=(*v,1)
    ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def socket(n,a,z,radius,role_material):
    radial=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-radial.y,radial.x,0));coolant=n.startswith('Upper collar coolant');centre=radial*(.56 if coolant else .505)+Vector((0,0,z))
    if coolant:tube(n+' connector sleeve',radial*.49+Vector((0,0,z)),radial*.56+Vector((0,0,z)),radius*.95,role_material)
    path(n+' annulus',[centre+tangent*(radius*math.cos(i*math.tau/40))+Vector((0,0,radius*math.sin(i*math.tau/40))) for i in range(40)],.018,role_material,True)
    tube(n+' dark bore',centre-radial*.005,centre+radial*.005,radius*.72,markpaint)
lathe('Broad mushroom drill head',[(3.87,.38),(4.00,.57),(4.15,.72),(4.29,.70),(4.43,.51),(4.56,.19)],shell)
lathe('Mushroom head equatorial band',[(4.13,.727),(4.20,.727)],light)
lathe('Top service cap',[(4.56,.14),(4.65,.14)],light)
lathe('Upper connector collar',[(3.40,.49),(3.90,.49)],shell)
for z in [3.40,3.87]:lathe('Upper collar pale band',[(z-.025,.515),(z+.025,.515)],light)
lathe('Lower connector collar',[(3.03,.47),(3.36,.47)],shell)
for z in [3.03,3.34]:lathe('Lower collar pale band',[(z-.025,.495),(z+.025,.495)],light)
for i in range(8):socket('Lower collar service socket',i*math.tau/8,3.19,.075,light)
lathe('Deep bore long drive barrel',[(.83,.19),(1.02,.30),(1.28,.34),(2.91,.34),(3.04,.39)],shell)
for z in [1.12,1.31,2.40,2.89]:lathe('Drive barrel dark seam',[(z-.012,.345),(z+.012,.345)],dark)
for i in range(8):
    a=i*math.tau/8;v=Vector((math.cos(a),math.sin(a),0))
    tube('Long drill drive barrel rib',v*.35+Vector((0,0,1.30)),v*.35+Vector((0,0,2.89)),.024,light)
# Two opposed maintenance strips and the small vertical service-plug row are
# part of the body; only the source-labelled probe is red in the first study.
for y in [-.355,.355]:
    ob=mark(g.box('Deep bore vertical service strip',(0,y,2.43),(.18,.035,.86),brass,.008))
    for z in [2.12,2.33,2.54,2.75]:
        path('Vertical strip service plug',[(.045*math.cos(i*math.tau/24),y+(-.025 if y<0 else .025),z+.045*math.sin(i*math.tau/24)) for i in range(24)],.008,light,True)
for sign in [-1,1]:
    points=[]
    for i in range(33):
        t=i/32;points.append((sign*(.49*(1-t)+.35*t+.43*math.sin(t*math.pi)),.03,3.64-1.24*t))
    path('Hanging deep bore cable loop',points,.012,light)
    points=[(x,y+.045,z-.10) for x,y,z in points];path('Secondary hanging cable loop',points,.010,dark)
for i in range(4):
    a=i*math.tau/4+math.pi/4;xy=(.34*math.cos(a),.34*math.sin(a));tube('Independent drill drive shaft',(xy[0],xy[1],.64),(xy[0],xy[1],1.04),.065,dark)
role='radio-seismic-probe'
lathe('Radio seismic torpedo probe',[(2.81,.012),(2.91,.035),(3.08,.065),(3.20,.045),(3.52,.045),(3.62,.065),(3.78,.035),(3.85,.010)],light,(-.91,0),24)
role='chassis'
for z in [3.06,3.58]:tube('Probe support arm',(-.49,0,z),(-.85,0,z+.02),.018,light)
role='drill-assemblies'
for i in range(4):
    a=i*math.tau/4+math.pi/4;xy=(.34*math.cos(a),.34*math.sin(a))
    lathe('Independent multi-head drill '+str(i),[(.10,.07),(.25,.21),(.46,.285),(.65,.24),(.76,.13)],brass,xy,24)
    lathe('Carbon cutting crown '+str(i),[(.045,.025),(.12,.10),(.28,.23),(.38,.27)],blue,xy,24)
    for tooth in range(4):
        b=tooth*math.tau/4;x=xy[0]+.17*math.cos(b);y=xy[1]+.17*math.sin(b);lathe('Carbon drill cutting tip',[(.09,.015),(.20,.075),(.30,.065)],blue,(x,y),12)
role='coolant-connectors'
for i in range(8):socket('Upper collar coolant connector',i*math.tau/8,3.64,.10,light)
root=bpy.data.objects.new('DeepBoreRotor',None);s.collection.objects.link(root)
component_names={k:[o.name for o in objects] for k,objects in parts.items()}
for group,objects in parts.items():
    for ob in objects:ob.parent=root;ob['scitek_component']=group
root.rotation_euler.z=0;root.scale.x=1.11

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
bpy.ops.wm.save_as_mainfile(filepath=str(out/'mk2-deep-bore-mine.blend'))
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
export('mk2-deep-bore-mine.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,3.5);target=Vector((0,0,2.4));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.5
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('mk2-deep-bore-mine-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['radio-seismic-probe','drill-assemblies','coolant-connectors']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle={'radio-seismic-probe':180,'drill-assemblies':25,'coolant-connectors':0}[group]
    local_target=Vector({'radio-seismic-probe':(-.91,0,3.25),'drill-assemblies':(0,0,.44),'coolant-connectors':(0,0,3.55)}[group])
    root.rotation_euler=(math.radians(90) if group=='coolant-connectors' else 0,0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'radio-seismic-probe':1.15,'drill-assemblies':1.75,'coolant-connectors':1.95}[group]
    render('highlight-'+group+'.png');export('mk2-deep-bore-mine-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='mk2-deep-bore-mine-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'mk2-deep-bore-mine.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'mk2-deep-bore-mine.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('mk2-deep-bore-mine-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'mk2-deep-bore-mine.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:mk2-deep-bore-mine',legacy_index=1,source='_MA/ST01.256 + ST01.VID; _SCITEK/ST01.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
