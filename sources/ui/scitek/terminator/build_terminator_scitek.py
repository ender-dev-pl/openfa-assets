"""Terminator research variant: actual ST30 solid and technical presentation variants."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
import tempfile
texture_temp=out/'texture-export-temp';texture_temp.mkdir(exist_ok=True);tempfile.tempdir=str(texture_temp)
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
# ST30 derivative: retain the authored PS04 hull/engines/wear, prepare research
# appendages from the actual anterior/lateral engine information studies.
expected_base='b464ef0ec6556f632212335afccc8c9d9e1c42cb4248049f8b5e9f15ed4cb013'
relative_base='sources/docs/assets/reconstruction/ships/terran/terminator/model.blend'
if '--base-blend' in sys.argv:base=Path(sys.argv[sys.argv.index('--base-blend')+1]).resolve()
else:
 candidates=[p/rel for p in Path(__file__).resolve().parents for rel in [relative_base,relative_base.removeprefix('sources/')]]
 base=next((p for p in candidates if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==expected_base),None)
 if base is None:raise ValueError('Provide --base-blend pointing to the published authored Terminator source')
assert hashlib.sha256(base.read_bytes()).hexdigest()==expected_base
base_lineage=dict(id='openfa:terminator',path=relative_base,sha256=expected_base,status='Existing hull/wings/main engines/wear retained; research appendages authored separately')
def signature(ob):
 d=ob.data;record=dict(matrix=[v for row in ob.matrix_basis for v in row],vertices=[list(v.co) for v in d.vertices],faces=[list(f.vertices)+[f.material_index] for f in d.polygons],uv=[[list(x.uv) for x in layer.data] for layer in d.uv_layers],materials=[m.name for m in d.materials]);return hashlib.sha256(json.dumps(record,separators=(',',':')).encode()).hexdigest()
with bpy.data.libraries.load(str(base),link=False) as (source,destination):destination.objects=[n for n in source.objects if n.startswith('Terminator ')]
old=[]
for ob in destination.objects:
 if ob is None or ob.type!='MESH':continue
 s.collection.objects.link(ob);matrix=ob.matrix_basis.copy();ob.parent=None;ob.matrix_world=matrix
 if ob.name.startswith(('Terminator forward barrel','Terminator bow collar','Terminator bow probe')):bpy.data.objects.remove(ob,do_unlink=True)
 else:old.append(ob)
assert len(old)==45
base_signatures={ob.name:signature(ob) for ob in old}
base_images={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
assert len(base_images)==4
shell=g.material('Used research device graphite steel',(.19,.19,.22),.55,.58)
light=g.material('Worn anterior titanium',(.39,.37,.38),.6,.47)
dark=g.material('Research thruster soot recess',(.017,.016,.019),.3,.73)
blue=g.material('Used blue lateral thruster casing',(.15,.17,.26),.5,.58)
brass=g.material('Heat stained anterior brass',(.37,.24,.10),.7,.54)
markpaint=g.material('Faded device alignment marking',(.34,.085,.06),.3,.62)
parts={k:[] for k in ['chassis','anterior-device-assembly','lateral-manoeuvring-thrusters','twin-main-engine-thrusters']};role='chassis'
for ob in old:
 group='twin-main-engine-thrusters' if ob.name.startswith(('Terminator exhaust ','Terminator cooling rib ')) else 'chassis';parts[group].append(ob)
def mark(ob):parts[role].append(ob);return ob
def tube(n,a,b,r,mat,r2=None):return mark(g.tube(n,a,b,r,mat,r2))
def box(n,loc,size,mat,b=.006):return mark(g.box(n,loc,size,mat,b))
def lathe(n,profile,mat,origin,axis,N=32):
 import bmesh
 q=Vector(axis).to_track_quat('Z','Y');origin=Vector(origin)
 v=[origin+q@Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)) for z,r in profile for i in range(N)];f=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):f.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 data=bpy.data.meshes.new(n);data.from_pydata(v,[],f);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(n,data);s.collection.objects.link(ob);g.finish(ob,mat,n);return mark(ob)
box('Research anterior assembly mounting bracket',(0,-1.48,.035),(.56,.18,.14),shell)
role='anterior-device-assembly'
for side in [-1,1]:
 x=side*.22
 profile=[(0,.07),(.07,.095),(.20,.095),(.28,.065),(.43,.055),(.49,.032),(.55,.028)] if side<0 else [(0,.075),(.06,.115),(.17,.115),(.24,.08),(.48,.048),(.55,.025),(.59,.023)]
 lathe('Anterior sensor or communications housing '+str(side),profile,light,(x,-1.50,.025),(0,-1,0))
 tube('Anterior brass terminal collar '+str(side),(x,-2.00,.025),(x,-2.055,.025),.032,brass)
 tube('Anterior needle '+str(side),(x,-2.055,.025),(x,-2.15,.025),.009,shell,.003)
 # Surface-level dark service seam/abrasion, retained in portable geometry.
 tube('Wear anterior device seam '+str(side),(x-.045,-1.64,.104),(x+.045,-1.64,.104),.002,dark)
for x,length in [(-.055,.76),(.065,.58)]:tube('Anterior fine sensor antenna',(x,-1.48,.055),(x,-1.48-length,.055),.0045,brass,.0012)
mark(g.uv('Anterior rotary cannon rounded head',(0,-1.78,.025),(.095,.11,.095),shell))
for i in range(5):
 a=i*math.tau/5;x=.047*math.cos(a);z=.025+.047*math.sin(a);tube('Rotary cannon short barrel',(x,-1.82,z),(x,-1.96,z),.012,light)
tube('Rotary cannon dark muzzle',(0,-1.942,.025),(0,-1.952,.025),.068,dark)
role='lateral-manoeuvring-thrusters'
for side in [-1,1]:
 origin=(side*1.38,-.45,-.09);axis=(side,0,0)
 lathe('Lateral manoeuvring body '+str(side),[(0,.055),(.06,.09),(.16,.09),(.23,.075),(.27,.075),(.30,.041),(.38,.026)],blue,origin,axis)
 tube('Lateral thruster collar '+str(side),(side*1.625,-.45,-.09),(side*1.655,-.45,-.09),.078,brass)
 tube('Lateral thruster dark aperture '+str(side),(side*1.752,-.45,-.09),(side*1.762,-.45,-.09),.019,dark)
 tube('Wear lateral casing abrasion '+str(side),(side*1.47,-.48,-.005),(side*1.54,-.48,-.005),.002,light)
root=bpy.data.objects.new('TerminatorResearchRotor',None);s.collection.objects.link(root)
component_names={k:[ob.name for ob in objects] for k,objects in parts.items()}
for group,objects in parts.items():
 for ob in objects:ob.parent=root;ob['scitek_component']=group
root.rotation_euler.z=0

def emit(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);e.inputs['Strength'].default_value=1;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],output.inputs[0]);return m
green=emit('Legacy green technical wire',(.0,.72,.005));red=emit('Legacy red selected component',(.9,.003,.001))
wire={}
for group,objects in parts.items():
    data=bpy.data.curves.new(group+' wire edges','CURVE');data.dimensions='3D';data.bevel_depth=.0025;data.bevel_resolution=0
    if group=='chassis':
        data.bevel_depth=.004
        # Display-only retessellation of the retained bilinear wing planes.
        # This does not alter their authored vertices, bevels, UVs or textures.
        def wing_grid(side,u,t,bottom):
            inner=Vector((.48,-1.30,0)).lerp(Vector((.56,1.10,0)),t)
            outer=Vector((1.55,-.45,0)).lerp(Vector((2.10,1.65,0)),t)
            p=inner.lerp(outer,u);return (side*p.x,p.y,.09-.025*p.x-(.11 if bottom else 0))
        for side in [-1,1]:
            for bottom in [False,True]:
                for axis in [0,1]:
                    for i in range(19):
                        sp=data.splines.new('POLY');sp.points.add(18)
                        for j,p in enumerate(sp.points):
                            u,t=(i/18,j/18) if axis==0 else (j/18,i/18)
                            p.co=(*wing_grid(side,u,t,bottom),1)
    for o in objects:
        if o.type=='CURVE':
            for old in o.data.splines:
                sp=data.splines.new('POLY');sp.points.add(len(old.points)-1);sp.use_cyclic_u=old.use_cyclic_u
                for p,q in zip(sp.points,old.points):p.co=(*(o.matrix_basis@Vector(q.co[:3])),1)
            continue
        if o.type!='MESH':continue
        # The original technical film shows a readable chamber cage, not every
        # small extruded heat-transfer fin. The solid model retains all ribs.
        if o.name.startswith(('Terminator cooling rib','Terminator crown vent fin','Wear ')):continue
        for edge in o.data.edges:
            va,vb=[o.data.vertices[i].co for i in edge.vertices]
            ia,ib=edge.vertices
            if o.name.startswith('Terminator exhaust ') and not o.name.startswith('Terminator exhaust throat'):
                # Keep four axial rings and16 meridians on both closed walls.
                if ia//128==ib//128:
                    if ia//128%13 not in [0,4,8,12]:continue
                elif ia%128%8:continue
            if len(o.data.vertices)==80 and abs(va.z-vb.z)>1e-6:
                step=int(round(math.atan2(va.y,va.x)/(math.tau/40)))%40
                if step%5:continue
            if o.name.startswith('Anterior rotary cannon rounded head'):
                if abs(va.z-vb.z)<1e-6:
                    ring=round(math.acos(max(-1,min(1,va.z)))*24/math.pi)
                    if ring%4:continue
                elif int(round(math.atan2(va.y,va.x)/(math.tau/48)))%4:continue
            spline=data.splines.new('POLY');spline.points.add(1)
            for p,i in zip(spline.points,edge.vertices):p.co=(*(o.matrix_basis@o.data.vertices[i].co),1)
    ob=bpy.data.objects.new(group+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wire[group]=ob
g.camera.location=(-12,-4,9.6);target=Vector((0,-.10,.10));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.5
s.render.resolution_x=576;s.render.resolution_y=640
cm=g.camera.rotation_euler.to_matrix();whole_info_euler=list(Matrix((cm.col[0],-cm.col[2],cm.col[1])).to_euler('XYZ'))
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def visibility(mode):
    for obs in parts.values():
        for o in obs:o.hide_render=mode!='solid'
    for o in wire.values():o.hide_render=mode=='solid'
# Prove a common camera contains every whole-assembly preview pose.
right=cm.col[0];up=cm.col[1];aspect=s.render.resolution_x/s.render.resolution_y
projected=[];extent=0.0
for frame in range(60):
    root.rotation_euler.z=-frame*math.tau/60;bpy.context.view_layer.update()
    points=[ob.matrix_world@v.co for objects in parts.values() for ob in objects if ob.type=='MESH' for v in ob.data.vertices]
    xs=[(p-g.camera.location).dot(right) for p in points];ys=[(p-g.camera.location).dot(up) for p in points]
    extent=max(extent,2*max(abs(min(xs)),abs(max(xs)))/aspect,2*max(abs(min(ys)),abs(max(ys))))
    projected.append((min(xs),min(ys),max(xs),max(ys)))
g.camera_data.ortho_scale=math.ceil(extent*1.06*100)/100
framing=dict(frame_count=60,method='All retained/new solid mesh vertices across every preview pose; common fixed camera with6 percent envelope margin',ortho_scale=g.camera_data.ortho_scale,ndc_bounds=[[.5+a/(g.camera_data.ortho_scale*aspect),.5+b/g.camera_data.ortho_scale,.5+c/(g.camera_data.ortho_scale*aspect),.5+d/g.camera_data.ortho_scale] for a,b,c,d in projected])
assert all(min(b)>0 and max(b)<1 for b in framing['ndc_bounds'])
root.rotation_euler.z=0;bpy.context.view_layer.update()
render('solid.png')
# Real named node rotation, sixty authored preview poses.
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=math.radians(0)-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
if root.animation_data:
    for fc in root.animation_data.action.fcurves:
        for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'terminator.blend'))
# Explicit PBR export preserves named component ownership and rotation hierarchy.
for mat in [shell,light,dark,blue,brass,markpaint]:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for slot in ['Base Color','Normal','Metallic','Roughness']:
        for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=mat.diffuse_color
def export(name,objects):
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
export('terminator.glb',[o for obs in parts.values() for o in obs])
visibility('wire');s.cycles.samples=4;s.render.resolution_x=896;s.render.resolution_y=896
s.view_settings.view_transform='Standard'
g.camera.location=(-12,-4,9.6);target=Vector((0,-.10,.10));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale=5.5
root.animation_data_clear();root.rotation_euler=(0,0,0)
render('wireframe.png');export('terminator-wireframe.glb',list(wire.values()))
wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)}
phases=[]
for i,group in enumerate(['anterior-device-assembly','lateral-manoeuvring-thrusters','twin-main-engine-thrusters']):
    for name,o in wire.items():o.data.materials[0]=red if name==group else green
    angles={'anterior-device-assembly':(-90,0,0),'lateral-manoeuvring-thrusters':(0,0,0),'twin-main-engine-thrusters':(-15,20,150)}
    local_target=Vector({'anterior-device-assembly':(0,-1.86,.025),'lateral-manoeuvring-thrusters':(1.57,-.45,-.09),'twin-main-engine-thrusters':(-.43,1.70,-.06)}[group])
    root.rotation_euler=[math.radians(a) for a in angles[group]];bpy.context.view_layer.update()
    centre=root.matrix_world@local_target;g.camera.location=(centre.x,centre.y-12,centre.z+.15);g.camera.rotation_euler=(centre-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera_data.ortho_scale={'anterior-device-assembly':.90,'lateral-manoeuvring-thrusters':.50,'twin-main-engine-thrusters':.84}[group]
    render('highlight-'+group+'.png');export('terminator-highlight-'+group+'.glb',list(wire.values()))
    wire_cameras['highlight-'+group]=(g.camera.matrix_world.copy(),g.camera_data.ortho_scale)
    phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,highlight_glb='terminator-highlight-'+group+'.glb',closeup_camera=list(g.camera.location),target=list(centre),local_target=list(local_target),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=g.camera_data.ortho_scale))
# Independent import proof, then fresh saved-source reload proof.
bpy.ops.wm.open_mainfile(filepath=str(out/'terminator.blend'));s=bpy.context.scene
for o in list(s.objects):
    if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'terminator.glb'));render('imported-solid.png')
for name,(camera_matrix,scale) in wire_cameras.items():
    for o in list(s.objects):
        if o.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/('terminator-'+name+'.glb')))
    assert any(o.type=='MESH' for o in s.objects),'Missing exported wire geometry'
    s.view_settings.view_transform='Standard'
    s.cycles.samples=4;s.camera.matrix_world=camera_matrix;s.camera.data.ortho_scale=scale;s.render.resolution_x=896;s.render.resolution_y=896
    render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'terminator.blend'));s=bpy.context.scene;render('reload-solid.png')
(out/'model.json').write_text(json.dumps(dict(issue=208,id='scitek:terminator',legacy_index=30,source='_MA/ST30.256 + ST30.VID; _SCITEK/ST30.VID',components=component_names,solid_framing=framing,base_source=base_lineage,base_mesh_signatures=base_signatures,base_packed_images=base_images,whole_information_rotation_euler=whole_info_euler,information_timeline_frames=423,phases=phases,limitations=['Camera close-ups approximate observed framing; do not claim source-exact recovered 3D camera transforms.','Full information-motion sequence still pending; phase assets are not a replacement for the complete film.'],verified=['Native render','Saved-source reload','Independent solid GLB import render']),indent=2)+'\n')
assert source_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n')
print('TRACKER_VARIANTS_READY')
