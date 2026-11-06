"""PH15/ST26 shared X50 solid and technical projections from evaluated geometry."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='16a5f07ecef45e5518ecf68aa4a0fb6cdb345c5c2d420d2cc71e2d714b3aec6b'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects.new('ShieldX50Root',None);s.collection.objects.link(root)
meshes=[o for o in s.objects if o.type=='MESH'];assert len(meshes)==48;preserved=[o.name for o in meshes]
roles=['chassis','power-input','paramagnetic-shielding','generator-and-broadcast-system'];parts={r:[] for r in roles}
for ob in meshes:
    if ob.name in ['Recessed connector interior','Connector terminal lip']:role='power-input'
    elif ob.name in ['Continuous rounded front cap','Unbroken enclosure wall','Enclosure reinforcing band','Enclosure reinforcing band.001']:role='paramagnetic-shielding'
    elif ob.name.startswith(('Shield axial equipment spine','Gold central emitter','Emitter insulator collar','Internal copper feed','Internal radial insulator')):role='generator-and-broadcast-system'
    else:role='chassis'
    parts[role].append(ob)
    if ob.parent is None:ob.parent=root
# Single service opening on the visible upper connector side in PH15 colour.
# The cutter is editable authoring geometry and excluded from all exports.
angle=3*math.pi/4;radius=.52
bpy.ops.mesh.primitive_cube_add(size=1,location=(radius*math.cos(angle),.82,radius*math.sin(angle)))
cutter=bpy.context.object;cutter.name='Authoring connector service aperture cutter';cutter.scale=(.40,.25,.20)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cutter.rotation_euler.y=-angle;cutter.parent=root;cutter.hide_render=True;cutter.display_type='WIRE'
modifier=bpy.data.objects['Tapered connector pressure shell'].modifiers.new('PH15 service aperture','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
metal=g.material('Research used X50 contact alloy',(.34,.33,.28),.65,.53)
for node in metal.node_tree.nodes:
    if node.type=='BUMP':node.inputs['Distance'].default_value=.0008;node.inputs['Strength'].default_value=.10
    if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=95

def pin(name,a,b,radius,role):
    ob=g.tube(name,a,b,radius,metal);ob.parent=root;meshes.append(ob);parts[role].append(ob)
for i in range(3):
    a=i*math.tau/3;x=.065*math.cos(a);z=.065*math.sin(a)
    pin('Research power-input contact',(x,1.41,z),(x,1.46,z),.009,'power-input')

bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
    curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0015;curve.bevel_resolution=0
    for ob in obs:
        evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update();transform=inverse@ob.matrix_world
        for edge in bm.edges:
            if edge.calc_length()<.008:continue
            if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
            a,b=[transform@v.co for v in edge.verts];spl=curve.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
        bm.free();evaluated.to_mesh_clear()
    ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True

root.scale.y=1.3
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s.render.resolution_x=480;s.render.resolution_y=320;s.render.film_transparent=True
target=Vector((0,-.05,0));s.camera.location=(-8,-3,2.0);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=4.8
bpy.ops.wm.save_as_mainfile(filepath=str(out/'shield-x50.blend'));export_solid(root,meshes,out/'shield-x50.glb');s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(roles[1:]):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,1.39,0],[0,-.85,0],[0,-.48,0]][i],closeup_rotation_euler=[[0,0,math.pi/2],[-math.pi/2,0,0],[-math.pi/2,0,0]][i],ortho_scale=[.65,2.5,2.0][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:shield-x50',object_id='openfa:shield-x50',legacy_index=26,components={k:[o.name for o in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,0],whole_information_rotation_euler=[.15,-.15,math.pi/2],whole_information_ortho_scale=6.2,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[o.name for o in meshes if o.name not in preserved],wire_geometry_contract='Technical lines are actual evaluated shared-solid edges; no independent technical model.',limitations=['All52prior mesh/UV/material signatures and source poses retained. Two monitor terminals and three small input contacts authored from PH15/ST26; exact tiny contact dimensions and camera interpolation are interpretations. Ship mounting transforms still require client validation.']),indent=2)+'\n')
p=out/'model.json';d=json.loads(p.read_text());d['source_transform_refinements']={};d['shared_root_scale']=list(root.scale);d['whole_information_ortho_scale']=8.0;d['limitations']=['All48prior mesh/UV/material signatures and Root-local poses retained. Shared Root scale[1,1.3,1] refines length/diameter from PH15. Three small input contacts are authored from PH15/ST26. Exact contact dimensions, camera interpolation and ship attachment remain interpretations.'];p.write_text(json.dumps(d,indent=2)+'\n')
p=out/'model.json';d=json.loads(p.read_text());d['modifier_refinements']=['Single connector service aperture from PH15 colour, using an editable Boolean cutter excluded from runtime exports.'];d['limitations'].append('Service opening position/shape follows the colour reference; exact engineering dimensions remain authored.');p.write_text(json.dumps(d,indent=2)+'\n')
assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('SHIELD_X50_VARIANTS_READY',len(meshes))
