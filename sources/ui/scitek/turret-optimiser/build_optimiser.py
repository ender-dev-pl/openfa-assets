"""Turret Optimiser: actual ST31 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST31 open cage with paired capsules, side manual control and stepped output.
shell=g.material('Worn optimiser cast alloy',(.34,.35,.27),.45,.58)
light=g.material('Used optimiser ivory steel',(.59,.60,.50),.48,.44)
dark=g.material('Optimiser joint grime',(.028,.025,.024),.25,.72)
blue=g.material('Faded green energy output casing',(.15,.20,.17),.35,.51)
brass=g.material('Used manual control bronze',(.40,.25,.115),.55,.55)
markpaint=g.material('Worn maroon capacitor covers',(.24,.125,.105),.35,.62)
for mat in [shell,light,brass,markpaint]:
 for n in mat.node_tree.nodes:
  if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=95
  if n.type=='BUMP':n.inputs['Strength'].default_value=.10;n.inputs['Distance'].default_value=.002
parts={k:[] for k in ['chassis','stored-energy-output','manual-pulse-control','flux-capacitor-system']};role='chassis'
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def box(n,loc,size,mat,b=.006):return mark(g.box(n,loc,size,mat,b))
def mesh(n,v,f,mat):
 import bmesh
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
def axial(n,profile,mat,x=0,z=0,origin_y=0,axis=-1,N=48):
 v=[(x+r*math.cos(i*math.tau/N),origin_y+axis*y,z+r*math.sin(i*math.tau/N)) for y,r in profile for i in range(N)];f=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 ob=mesh(n,v,f,mat)
 for polygon in ob.data.polygons:polygon.use_smooth=len(polygon.vertices)==4
 return ob
def plate(n,y,scale):
 poly=[(-.36,.22),(-.36,-.13),(-.13,-.33),(.16,-.34),(.39,-.10),(.36,.20),(.15,.34),(-.14,.34)]
 v=[(x*scale,yy,z*scale) for yy in [y-.045,y+.045] for x,z in poly];N=len(poly);f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 ob=mesh(n,v,f,shell);g.bevel(ob,.025);return ob
plate('Optimiser front shield plate',-.50,1.08);plate('Optimiser rear shield plate',.68,.98)
for x in [-.29,.29]:
 for z in [-.21,.21]:tube('Silver longitudinal cage rail',(x,-.48,z),(x,.66,z),.024,light)
for z in [-.26,.26]:tube('Chamber central service brace',(0,-.47,z),(0,.66,z),.015,shell)
box('Maroon protective control cover',(.17,.08,.22),(.28,.56,.14),markpaint,.012)
for y in [-.07,.035,.14]:box('Cover recessed vent',(.17,y,.295),(.12,.018,.008),dark,.001)
for x in [.065,.275]:
 for y in [-.13,.29]:tube('Small cover fastener',(x,y,.292),(x,y,.302),.009,brass)
for radius in [.275,.20,.09]:
 data=bpy.data.curves.new('Rear engraved contour','CURVE');data.dimensions='3D';data.bevel_depth=.003;data.bevel_resolution=1;sp=data.splines.new('POLY');sp.points.add(63);sp.use_cyclic_u=True
 for i,p in enumerate(sp.points):p.co=(radius*math.cos(i*math.tau/64),.728,radius*.94*math.sin(i*math.tau/64),1)
 ob=bpy.data.objects.new('Rear plate concentric engraving',data);s.collection.objects.link(ob);g.finish(ob,dark,ob.name);mark(ob)
for i in range(10):
 y=-.25+(i%5)*.18;x=(-.30 if i%2 else .30);z=.22;tube('Wear cage contact scuff',(x-.012,y,z),(x+.012,y+.012,z),.002,dark)
for i in range(6):
 x=-.20+i*.075;tube('Wear front plate scratch',(x,-.547,.23),(x+.025,-.547,.24),.002,brass)
role='flux-capacitor-system'
for side in [-1,1]:
 radius=.13 if side<0 else .16
 length=.78 if side<0 else .94
 profile=[(y*length/.88,r) for y,r in [(0,radius*.48),(.04,radius*.85),(.11,radius),(.75,radius),(.83,radius*.82),(.88,radius*.35)]]
 axial('Internal flux capacitor '+str(side),profile,markpaint,side*.17,0,.50,-1)
for y in [-.22,.02,.26]:tube('Visible capacitor coupling',(-.17,y,.115),(.17,y,.14),.013,brass)
box('Capacitor common connecting yoke',(0,-.32,-.035),(.55,.07,.12),markpaint,.009)
role='manual-pulse-control'
tube('Manual bronze pulse rod',(.38,-.50,.03),(.38,.63,.03),.045,brass)
mark(g.uv('Manual pulse control rounded end',(.38,-.55,.03),(.07,.085,.07),brass))
for y in [-.47,.59]:tube('Manual rod bearing',(.38,y-.018,.03),(.38,y+.018,.03),.060,shell)
role='stored-energy-output'
axial('Stored energy output mounting bulb',[(0,.20),(.08,.19),(.13,.13),(.17,.12)],blue,-.08,-.06,-.55,-1)
axial('Stored energy output middle bulb',[(.17,.12),(.22,.15),(.31,.14),(.36,.08)],light,-.08,-.06,-.55,-1)
axial('Output neck double ring',[(.35,.085),(.36,.10),(.38,.10),(.395,.08)],shell,-.08,-.06,-.55,-1)
axial('Stored energy terminal bulb',[(.39,.08),(.42,.105),(.48,.095),(.53,.05),(.57,.012)],light,-.08,-.06,-.55,-1)
root=bpy.data.objects.new('OptimiserRotor',None);s.collection.objects.link(root)
component_names={k:[ob.name for ob in objects] for k,objects in parts.items()}
for group,objects in parts.items():
 for ob in objects:ob.parent=root;ob['scitek_component']=group
root.rotation_euler.z=0

def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.0018;data.bevel_resolution=0
    for o in objects:
        if o.type=='CURVE':
            for old in o.data.splines:
                sp=data.splines.new('POLY');sp.points.add(len(old.points)-1);sp.use_cyclic_u=old.use_cyclic_u
                for p,q in zip(sp.points,old.points):p.co=(*(o.matrix_basis@Vector(q.co[:3])),1)
            continue
        if o.type!='MESH':continue
        # The original technical film shows a readable chamber cage, not every
        # small extruded heat-transfer fin. The solid model retains all ribs.
        if o.name.startswith(('Wear ','Small cover fastener')):continue
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
g.camera.location=(-3,-10,7);target=Vector((0,-.15,0));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=3.3
s.render.resolution_x=576;s.render.resolution_y=640
cm=g.camera.rotation_euler.to_matrix();whole_info_euler=list(Matrix((cm.col[0],-cm.col[2],cm.col[1])).to_euler('XYZ'))
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
# Match the occupied source tile box while containing every rotation pose.
right=cm.col[0];up=cm.col[1];aspect=s.render.resolution_x/s.render.resolution_y
projected=[];extent=0.0
for frame in range(60):
    root.rotation_euler.z=-frame*math.tau/60;bpy.context.view_layer.update()
    points=[ob.matrix_world@v.co for objects in parts.values() for ob in objects if ob.type=='MESH' for v in ob.data.vertices]
    xs=[(p-g.camera.location).dot(right) for p in points];ys=[(p-g.camera.location).dot(up) for p in points]
    projected.append((min(xs),min(ys),max(xs),max(ys)))
a,b,c,d=projected[0];cx=(a+c)/2;cy=(b+d)/2
whole_scale=max((c-a)/(67/224),(d-b)/(82/224))
whole_target=list(target+right*(cx-(110.5/224-.5)*whole_scale)+up*(cy-(1-114/224-.5)*whole_scale))
source_scale=max((c-a)/(68/144*aspect),(d-b)/(82/160))
dx=cx-(75/144-.5)*source_scale*aspect;dy=cy-(1-82/160-.5)*source_scale
for a,b,c,d in projected:extent=max(extent,2*max(abs(a-dx),abs(c-dx))/aspect,2*max(abs(b-dy),abs(d-dy)))
g.camera_data.ortho_scale=max(source_scale,math.ceil(extent*1.06*100)/100)
g.camera.location+=right*dx+up*dy
framing=dict(frame_count=60,method='Source tile occupancy and all solid vertices across60 poses, minimum6 percent rotational envelope margin',ortho_scale=g.camera_data.ortho_scale,source_occupancy_scale=source_scale,ndc_bounds=[[.5+(a-dx)/(g.camera_data.ortho_scale*aspect),.5+(b-dy)/g.camera_data.ortho_scale,.5+(c-dx)/(g.camera_data.ortho_scale*aspect),.5+(d-dy)/g.camera_data.ortho_scale] for a,b,c,d in projected])
assert all(min(b)>0 and max(b)<1 for b in framing['ndc_bounds'])
root.rotation_euler.z=0;bpy.context.view_layer.update();native_camera_matrix=g.camera.matrix_world.copy()
render('solid.png')

# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(0)-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'turret-optimiser.blend'))
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
export('turret-optimiser.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.matrix_world=native_camera_matrix;g.camera_data.ortho_scale=whole_scale
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('turret-optimiser-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['stored-energy-output','manual-pulse-control','flux-capacitor-system']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angles={'stored-energy-output':(-90,0,0),'manual-pulse-control':(-90,0,0),'flux-capacitor-system':(-90,0,0)}
    local_target=Vector({'stored-energy-output':(-.08,-.835,-.06),'manual-pulse-control':(.38,-.125,.03),'flux-capacitor-system':(0,.03,0)}[group])
    root.rotation_euler=[math.radians(a) for a in angles[group]];bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'stored-energy-output':.60,'manual-pulse-control':1.0,'flux-capacitor-system':.85}[group]
    render('highlight-'+group+'.png');export('turret-optimiser-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='turret-optimiser-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'turret-optimiser.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'turret-optimiser.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('turret-optimiser-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'turret-optimiser.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:turret-optimiser',legacy_index=31,source='_MA/ST31.256 + ST31.VID; _SCITEK/ST31.VID',components=component_names,solid_framing=framing,whole_information_rotation_euler=whole_info_euler,whole_information_local_target=whole_target,whole_information_ortho_scale=whole_scale,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
