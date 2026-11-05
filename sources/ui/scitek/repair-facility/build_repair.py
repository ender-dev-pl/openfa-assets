"""PB15/ST22 shared refined Repair Facility, based on actual source views."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='3afb7d6178ab7f4abe56e245f5609128140c46d11e4fa5dc2eae771b11d9c3f1'
s=g.scene;s.cycles.samples=16;s.view_settings.view_transform='AgX'
root=bpy.data.objects.new('RepairFacilityRoot',None);s.collection.objects.link(root)
roles=['chassis','four-data-dishes','droid-ports','droid-antennae'];parts={n:[] for n in roles};meshes=[]
names=['Cylindrical tower','Tower seam','Workshop gold roof','Repair drum replaceable skins']
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=list(names)
for ob in dst.objects:
    assert ob is not None
    s.collection.objects.link(ob);ob.parent=root;meshes.append(ob);parts['chassis'].append(ob)
preserved=[o.name for o in meshes]
purple=g.material('Research used purple-grey armour',(.19,.18,.25),.48,.58)
dark=g.material('Research grime in droid port seams',(.035,.033,.045),.2,.7)
port=g.material('Research pale blue worn droid port',(.65,.75,.78),.35,.45)
gold=g.material('Research worn dish bronze',(.43,.29,.105),.55,.5)
steel=g.material('Research tarnished antenna steel',(.26,.27,.29),.6,.5)
for mat in [purple,dark,port,gold,steel]:
    for node in mat.node_tree.nodes:
        if node.type=='BUMP':node.inputs['Distance'].default_value=.002;node.inputs['Strength'].default_value=.1
        if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=70

def add(ob,role='chassis'):
    ob.parent=root;meshes.append(ob);parts[role].append(ob);return ob

def box(name,loc,dims,mat,angle=0,role='chassis',bevel=.005):
    ob=add(g.box(name,loc,dims,mat,bevel),role);ob.rotation_euler.z=angle;return ob

def tube(name,a,b,r,mat,role):return add(g.tube(name,a,b,r,mat),role)

# Eight vertical recess/fascia bands, interspersed with repair-droid ports.
# Their count/hidden distribution is authored; the four dish count is caption evidence.
for i in range(8):
    a=i*math.tau/8;rad=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0))
    p=rad*.846+Vector((0,0,1.27))
    box('Research vertical recessed service band',p,(.025,.25,1.90),dark,a)
    for z in [.38,2.18]:
        box('Research fascia end cap',rad*.875+Vector((0,0,z)),(.12,.30,.17),purple,a)
    edge=a+math.pi/8;axis=Vector((math.cos(edge),math.sin(edge),0))
    box('Research raised protective fin',axis*.875+Vector((0,0,1.27)),(.13,.055,1.89),purple,edge)
    for row in range(7):
        # Paired pale square ports with a mid-body maintenance gap.
        z=.58+row*.20
        for col in [-1,1]:
            if (i+row)%7==0 and col==1:continue
            p=rad*.866+side*(col*.061)+Vector((0,0,z))
            box('Research droid port recessed frame',p,(.036,.10,.102),dark,a,'droid-ports',.004)
            box('Research droid port face',p+rad*.021,(.014,.077,.079),port,a,'droid-ports',.003)

# Closed thin paraboloid dishes, tilted outward on the gold dome.
for i in range(4):
    a=math.pi/4+i*math.pi/2;rad=Vector((math.cos(a),math.sin(a),0));normal=(rad*.78+Vector((0,0,.63))).normalized()
    N=32;profile=[(.0,.0),(.032,.055),(.10,.055),(.112,.022),(.112,.010),(.10,.038),(.032,.038),(.0,-.008)]
    # profile is (radius, depth); distinct axis vertices avoid degenerate rings.
    verts=[(0,0,profile[0][1])]
    for radius,z in profile[1:-1]:verts.extend((radius*math.cos(k*math.tau/N),radius*math.sin(k*math.tau/N),z) for k in range(N))
    verts.append((0,0,profile[-1][1]));faces=[]
    faces.extend((0,1+k,1+(k+1)%N) for k in range(N))
    for j in range(len(profile)-3):
        for k in range(N):faces.append((1+j*N+k,1+j*N+(k+1)%N,1+(j+1)*N+(k+1)%N,1+(j+1)*N+k))
    end=len(verts)-1;last=1+(len(profile)-3)*N
    faces.extend((end,last+(k+1)%N,last+k) for k in range(N))
    data=bpy.data.meshes.new('Repair data dish surface');data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new('Research data dish '+str(i),data);s.collection.objects.link(ob);ob.data.materials.append(gold)
    ob.location=rad*.43+Vector((0,0,2.44));ob.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
    for face in data.polygons:face.use_smooth=True
    add(ob,'four-data-dishes')

# Slender command aerial with two round plates; shown independently in ST22.
tube('Research dedicated droid antenna mast',(0,0,2.48),(0,0,2.88),.006,steel,'droid-antennae')
for z,radius in [(2.68,.026),(2.85,.035)]:
    add(g.uv('Research dedicated droid antenna disc',(0,0,z),(radius,.006,radius),steel),'droid-antennae')

bpy.context.view_layer.update()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
    curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0015;curve.bevel_resolution=0
    for ob in obs:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
        for edge in bm.edges:
            if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
            a,b=[ob.matrix_basis@v.co for v in edge.verts];spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
        bm.free()
    ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True

root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,1.40));g.camera.location=(4,-10,5.8);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=3.50;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'repair-facility.blend'));export_solid(root,meshes,out/'repair-facility.glb');s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(roles[1:]):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[.304,-.304,2.44],[.061,-.87,1.18],[0,0,2.77]][i],closeup_rotation_euler=[[0,0,-math.pi/4],[0,0,0],[0,0,0]][i],ortho_scale=[.36,.24,.50][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:repair-facility',object_id='terran:repair-facility',legacy_index=22,components={k:[o.name for o in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,1.4],whole_information_rotation_euler=[.12,0,.25],whole_information_ortho_scale=3.6,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],limitations=['Four scoped original meshes preserved. Recesses, droid port distribution, dish construction and aerial are authored from PB15/ST22; hidden details and camera interpolation are approximate.']),indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('REPAIR_FACILITY_VARIANTS_READY',len(meshes))
