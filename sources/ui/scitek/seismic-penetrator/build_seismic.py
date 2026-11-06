"""Shared PB21 refinement and ST24 presentations from one evaluated geometry."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='26c8c65423ce550ab3689cce806dc1ce8a9bfc17543e16132f5b732377c80e9c'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects['PlacementRoot'];root.name='SeismicPenetratorRoot'
assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==225;preserved=[o.name for o in meshes]
roles=['chassis','control-computers-and-antennae','shaft-head-drive','ore-slurry-recovery-pipes'];parts={r:[] for r in roles}
shaft_names=['Probe guide collar','Internal precision drill head','Front geophysical probe shaft','Pale probe fork tine','Pale probe fork tine.001','Probe fork bridge']
for ob in meshes:
    role='shaft-head-drive' if ob.name in shaft_names else 'control-computers-and-antennae' if ob.name.startswith(('Hatch ','Short rear survey aerial')) else 'chassis'
    parts[role].append(ob)
metal=g.material('Research worn slurry conduit alloy',(.19,.20,.23),.55,.57)
for node in metal.node_tree.nodes:
    if node.type=='BUMP':node.inputs['Distance'].default_value=.001;node.inputs['Strength'].default_value=.12
    if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=75

def pipe(name,points,outer,inner,N=16):
    verts=[];count=len(points);faces=[];up=Vector((0,0,1))
    for radius in [outer,inner]:
        for j,p in enumerate(points):
            tangent=(points[min(j+1,count-1)]-points[max(j-1,0)]).normalized();side=tangent.cross(up).normalized()
            for k in range(N):verts.append(tuple(p+side*(radius*math.cos(k*math.tau/N))+up*(radius*math.sin(k*math.tau/N))))
    layer=count*N
    for side in [0,1]:
        for j in range(count-1):
            for k in range(N):
                q=(side*layer+j*N+k,side*layer+j*N+(k+1)%N,side*layer+(j+1)*N+(k+1)%N,side*layer+(j+1)*N+k)
                faces.append(q if side==0 else tuple(reversed(q)))
    for j in [0,count-1]:
        for k in range(N):faces.append((j*N+k,j*N+(k+1)%N,layer+j*N+(k+1)%N,layer+j*N+k))
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(data);bm.free();ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(metal)
    for face in data.polygons:face.use_smooth=True
    meshes.append(ob);parts['ore-slurry-recovery-pipes'].append(ob);return ob

# Two hidden return/feed circuits inside the lower drum, clarified by the
# underside ST24 projection. Exact internal routing is an authored fit.
for index,(radius,z) in enumerate([(.90,.095),(.81,.16)]):
    points=[Vector((-radius,.30,z)),Vector((-radius,-.40,z))]
    points += [Vector((radius*math.cos(math.pi+i*math.pi/32),-.40+radius*math.sin(math.pi+i*math.pi/32),z)) for i in range(1,33)]
    points.append(Vector((radius,.30,z)))
    pipe('Research slurry '+('return' if index==0 else 'feed')+' continuous U pipe',points,.030,.018)
    for side in [-1,1]:pipe('Research slurry circuit coupling', [Vector((side*radius,.22,z)),Vector((side*radius,.30,z))],.060,.033)

bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
    curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0015;curve.bevel_resolution=0
    for ob in obs:
        if ob.name.startswith(('Edge abrasion','Roof fine service scratch','Faded red roof marking','Pale nose roof stripe')):continue
        evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update();transform=inverse@ob.matrix_world
        for edge in bm.edges:
            if edge.calc_length()<.008:continue
            if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
            a,b=[transform@v.co for v in edge.verts];spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
        bm.free();evaluated.to_mesh_clear()
    ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True

root.rotation_mode='XYZ';root.animation_data_clear();s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
target=Vector((0,-.2,.60));s.camera.location=(4,-7,4.5);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=3.6
bpy.ops.wm.save_as_mainfile(filepath=str(out/'seismic-penetrator.blend'));export_solid(root,meshes,out/'seismic-penetrator.glb');s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(roles[1:]):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,.47,1.13],[0,-1.35,.49],[0,-.40,.12]][i],closeup_rotation_euler=[[.40,0,0],[0,0,0],[-math.pi/2,0,0]][i],ortho_scale=[2.70,1.15,2.35][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:seismic-penetrator',object_id='terran:seismic-penetrator',legacy_index=24,components={k:[o.name for o in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,-.2,.60],whole_information_rotation_euler=[.42,0,.35],whole_information_ortho_scale=3.55,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],wire_geometry_contract='Subset of actual evaluated shared solid edges; cameras/hue differ, geometry does not.',limitations=['All225prior meshes, UVs and material slots retained, including curved nose/common drill axis and packed authored wear. Two internal slurry circuits and four couplings are authored from the ST24 underside view; exact hidden routing and cameras are approximations.']),indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('SEISMIC_PENETRATOR_VARIANTS_READY',len(meshes))
