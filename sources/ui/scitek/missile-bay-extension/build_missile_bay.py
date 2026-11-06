"""Missile Bay Extension: actual ST01 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST14: fixed annular base and tall launcher mast; internal lifting carriage.
# Proportions/part ownership are interpreted from the actual colour and wire films.
shell=g.material('Used olive-grey launcher alloy',(.34,.33,.23),.45,.57)
light=g.material('Worn warm metal edge strips',(.52,.48,.31),.5,.48)
dark=g.material('Recess grime and blast lining',(.045,.038,.032),.25,.66)
blue=g.material('Faded blue-green control glass',(.12,.26,.24),.2,.36)
brass=g.material('Brown hydraulic carriage',(.23,.15,.10),.4,.55)
markpaint=g.material('Faded red missile caps',(.38,.075,.052),.25,.58)
for mat in [shell,light,brass]:
 for node in mat.node_tree.nodes:
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=78
  if node.type=='BUMP':node.inputs['Strength'].default_value=.10;node.inputs['Distance'].default_value=.004
parts={k:[] for k in ['chassis','revolving-storage-rack','missile-loading-assembly','targeting-control']};role='chassis'
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def mesh(n,v,f,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def lathe(n,profile,mat,N=48):
 v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in profile for i in range(N)];f=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 return mesh(n,v,f,mat)
def ring(n,z0,z1,rin,rout,mat,N=48,taper=0):
 # Closed annulus with actual hollow centre, not a painted disc.
 v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in [(z0,rout-taper),(z1,rout),(z0,rin-taper),(z1,rin)] for i in range(N)];f=[]
 for i in range(N):
  j=(i+1)%N
  f.extend([(i,j,N+j,N+i),(2*N+j,2*N+i,3*N+i,3*N+j),(N+i,N+j,3*N+j,3*N+i),(j,i,2*N+i,2*N+j)])
 return mesh(n,v,f,mat)
def box(n,loc,size,mat,b=.012):return mark(g.box(n,loc,size,mat,b))
role='revolving-storage-rack'
ring('Annular revolving magazine',.05,.43,.68,1.02,shell)
ring('Upper magazine lip',.40,.46,.68,1.035,light)
ring('Lower magazine seam',.06,.09,.68,1.03,dark)
for i in range(20):
 a=i*math.tau/20;rad=Vector((math.cos(a),math.sin(a),0));loc=rad*.845
 tube('Stored missile body',(*loc[:2],.20),(*loc[:2],.435),.055,light)
 tube('Stored missile red cap',(*loc[:2],.435),(*loc[:2],.47),.054,markpaint,.035)
 # Vertical panel seams/handling scratches break the broad outer wall.
 tube('Magazine panel seam',tuple(rad*1.024+Vector((0,0,.12))),tuple(rad*1.024+Vector((0,0,.36))),.006,dark)
role='chassis'
lathe('Tall missile launcher mast',[(.34,.25),(2.93,.25),(3.01,.17),(3.68,.17)],shell)
for z in [.46,1.05,2.55]:ring('Launcher mast service collar',z,z+.045,.17,.265,light,32)
ring('Top stalk flush service band',3.48,3.54,.165,.181,light,32)
ring('Open upper blast guard',2.95,3.16,.64,.70,shell,40,taper=.15)
for a in [0,math.pi/2,math.pi,math.pi*1.5]:
 rad=Vector((math.cos(a),math.sin(a),0));tube('Upper guard radial strut',tuple(rad*.22+Vector((0,0,2.96))),tuple(rad*.66+Vector((0,0,2.96))),.035,light)
for side in [-1,1]:
 x=side*.48
 # Tapered plate braces, matching the sloping structural cheeks in ST14.
 v=[(x+dx,y,z) for dx in [-.07,.07] for y,z in [(-.19,.39),(.18,.39),(.06,1.61),(-.11,1.79)]]
 mesh('Tapered lateral launcher brace',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],shell)
 tube('Pale outer hydraulic rail',(side*.38,-.08,.44),(side*.25,-.08,2.52),.022,light)
role='targeting-control'
for sign in [-1,1]:
 panel=box('Sloped targeting computer', (sign*.55,-.08,1.05),(.16,.40,.72),shell)
 panel.rotation_euler.y=sign*math.radians(-18)
 glass=box('Faded targeting screen',(sign*.65,-.11,1.18),(.018,.23,.30),blue,.004);glass.rotation_euler.y=sign*math.radians(-18)
 for z in [.66,.77,.88]:tube('Targeting computer round control',(sign*.63,-.30,z),(sign*.63,-.32,z),.022,light)
role='missile-loading-assembly'
for x in [-.17,.17]:tube('Vertical missile transfer guide',(x,-.285,.50),(x,-.285,2.60),.026,light)
for x in [-.125,.125]:
 ob=box('Split lower blast door',(x,-.38,.87),(.21,.08,.81),brass);ob.rotation_euler.x=math.radians(-12)
box('Hydraulic transport lower bed',(0,-.39,.47),(.34,.35,.12),shell)
moving=[]
def moving_box(n,loc,size,mat):ob=box(n,loc,size,mat);moving.append(ob);return ob
moving_box('Moving missile transfer carriage',(0,-.32,2.06),(.35,.18,.48),light)
for x in [-.09,.09]:
 ob=tube('Carriage red service light',(x,-.43,1.99),(x,-.45,1.99),.033,markpaint);moving.append(ob)
ob=tube('Lifted missile body',(.10,-.38,.62),(.10,-.38,1.22),.04,blue);moving.append(ob)
ob=tube('Lifted missile nose',(.10,-.38,1.22),(.10,-.38,1.34),.04,markpaint,.002);moving.append(ob)
root=bpy.data.objects.new('MissileBayRig',None);s.collection.objects.link(root)
root.scale.x=1.18
carriage=bpy.data.objects.new('HydraulicTransferCarriage',None);s.collection.objects.link(carriage);carriage.parent=root
missile=bpy.data.objects.new('MissileTransferPivot',None);s.collection.objects.link(missile);missile.parent=root
for group,objects in parts.items():
 for ob in objects:ob.parent=missile if ob.name.startswith('Lifted missile') else carriage if ob in moving else root;ob['scitek_component']=group
for frame,offset in [(1,0),(31,0),(61,-.18),(91,-.18),(121,-.03),(151,-.62),(166,-.62),(181,0)]:
 carriage.location.z=offset;carriage.keyframe_insert('location',frame=frame)
for fc in carriage.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
for frame,position in [(1,(0,.13,0)),(31,(0,.13,0)),(46,(.24,-.06,0)),(76,(.24,-.06,0)),(106,(.05,-.06,.20)),(121,(-.10,.13,.65)),(151,(-.10,.13,.65)),(166,(0,.13,0)),(181,(0,.13,0))]:
 missile.location=position;missile.keyframe_insert('location',frame=frame)
for fc in missile.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_start=1;s.frame_end=181;s.render.fps=15
rig_frames=[]
for f in range(1,181):
 s.frame_set(f);bpy.context.view_layer.update();rig_frames.append(dict(frame=f-1,mesh_root_matrices={ob.name:[v for row in (root.matrix_world.inverted()@ob.matrix_world) for v in row] for ob in moving}))
(out/'solid-animation-timeline.json').write_text(json.dumps(dict(frame_count=180,fps=15,root=root.name,body_turntable=False,format='Absolute row-major4x4 matrices, Blender column-vector math/Z-up; GLB hierarchy authoritative.',animated_mesh_nodes=[ob.name for ob in moving],bind_root_matrices=rig_frames[0]['mesh_root_matrices'],timeline=rig_frames),separators=(',',':'))+'\n')
s.frame_set(1);bpy.context.view_layer.update();component_names={k:[ob.name for ob in objects] for k,objects in parts.items()}

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
            if o.name=='Tall missile launcher mast' and abs(va.z-vb.z)>1e-6 and edge.vertices[0]%48%6:continue
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
g.camera.location=(4,-10,5.3);target=Vector((0,0,1.84));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.2
s.render.resolution_x=576;s.render.resolution_y=640
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
render('solid.png')
# Stationary body, local loading carriage cycle, 180 source preview updates.
s.frame_start=1;s.frame_end=181;s.render.fps=15;s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'missile-bay-extension.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint,g.gold,g.red]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('missile-bay-extension.glb',[o for obs in parts.values() for o in obs]+[carriage,missile])
rig_path=out/'solid-animation-timeline.json';rig=json.loads(rig_path.read_text());rig['source_blend_sha256']=hashlib.sha256((out/'missile-bay-extension.blend').read_bytes()).hexdigest();rig['source_glb_sha256']=hashlib.sha256((out/'missile-bay-extension.glb').read_bytes()).hexdigest();rig_path.write_text(json.dumps(rig,separators=(',',':'))+'\n')
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(0,-12,2.0);target=Vector((0,0,1.8));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=4.2
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('missile-bay-extension-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['revolving-storage-rack','missile-loading-assembly','targeting-control']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angle={'revolving-storage-rack':0,'missile-loading-assembly':0,'targeting-control':30}[group]
    local_target=Vector({'revolving-storage-rack':(0,0,.25),'missile-loading-assembly':(0,-.23,1.28),'targeting-control':(-.4,0,.95)}[group])
    root.rotation_euler=(math.radians(90) if group=='revolving-storage-rack' else 0,0,math.radians(angle));bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'revolving-storage-rack':2.55,'missile-loading-assembly':2.30,'targeting-control':1.25}[group]
    render('highlight-'+group+'.png');export('missile-bay-extension-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='missile-bay-extension-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'missile-bay-extension.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'missile-bay-extension.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('missile-bay-extension-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'missile-bay-extension.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:missile-bay-extension',legacy_index=14,source='_MA/ST14.256 + ST14.VID; _SCITEK/ST14.VID',components=component_names,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
