"""PH08/ST28 shared model refinement and projections of its evaluated solid."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='5e64d263bbc8ed2141c934c7f7fe3b6e87ece17fd9a80ba6391a31864f6dd6e4'
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects['PlacementRoot'];assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
root.name='StaticInducerRoot';root.animation_data_clear()
meshes=[ob for ob in s.objects if ob.type=='MESH'];assert len(meshes)==52
old=bpy.data.objects['Static Inducer collar 0'];material=old.data.materials[0]
preserved=[ob.name for ob in meshes if ob!=old];bpy.data.objects.remove(old,do_unlink=True)
bpy.ops.mesh.primitive_torus_add(major_segments=64,minor_segments=16,major_radius=.48,minor_radius=.055,location=(0,-.43,0),rotation=(math.pi/2,0,0))
coil=bpy.context.object;coil.name='Toroidal interference coil';coil.parent=root;coil.data.materials.append(material)
for polygon in coil.data.polygons:polygon.use_smooth=True
roles=['chassis','transmitter-array','toroidal-interference-coil','tri-phase-power-input'];parts={r:[] for r in roles}
meshes=[ob for ob in s.objects if ob.type=='MESH']
for ob in meshes:
 if ob==coil:role='toroidal-interference-coil'
 elif ob.name.startswith(('Static Inducer studded dome','Static Inducer stud base','Static Inducer stud tip','Static Inducer axial red terminal')):role='transmitter-array'
 elif ob.name.startswith(('Static Inducer blue terminal','Static Inducer recessed rim','Static Inducer recess floor')):role='tri-phase-power-input'
 else:role='chassis'
 parts[role].append(ob)
# PH08 rear view and ST28 power closeup resolve compact rounded cells, not
# elongated bottles. Refine the entire attached group with one axial affine map.
power_names=[ob.name for ob in parts['tri-phase-power-input']]
power_transform=Matrix.Diagonal((1,.7,1,1));power_transform.translation.y=.35*(1-.7)
for ob in parts['tri-phase-power-input']:
 ob.matrix_world=power_transform@ob.matrix_world
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
for role,obs in parts.items():
 curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0015;curve.bevel_resolution=0
 for ob in obs:
  evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update();transform=inverse@ob.matrix_world
  for edge in bm.edges:
   if edge.calc_length()<.008:continue
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[transform@v.co for v in edge.verts];sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();evaluated.to_mesh_clear()
 ob=bpy.data.objects.new(role+' technical wire',curve);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
s.frame_set(1);s.render.resolution_x=480;s.render.resolution_y=320;s.render.film_transparent=True
target=Vector((0,-.03,0));s.camera.location=(-8,-3,2);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.8
bpy.ops.wm.save_as_mainfile(filepath=str(out/'static-inducer.blend'));s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True);export_solid(root,meshes,out/'static-inducer.glb')
phases=[dict(component=r,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=t,closeup_rotation_euler=pose,ortho_scale=scale) for i,(r,t,pose,scale) in enumerate(zip(roles[1:],[[0,-.68,0],[0,-.43,0],[0,.55,0]],[[-math.pi/2,0,0],[0,0,math.pi/2],[-math.pi/2,0,0]],[1.4,1.5,1.25]))]
model=dict(id='scitek:static-inducer',object_id='openfa:static-inducer',legacy_index=28,components={r:[o.name for o in obs] for r,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,0],whole_information_rotation_euler=[.08,-.08,math.pi/2],whole_information_ortho_scale=4.3,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=preserved,new_presentation_meshes=[coil.name],removed_source_meshes=['Static Inducer collar 0'],source_transform_refinements={},power_input_affine_refinement=dict(names=power_names,axis='Y',scale=.7,pivot=.35),shared_root_scale=list(root.scale),wire_geometry_contract='Every technical segment is an actual evaluated shared-solid edge.',limitations=['PH08 colour and ST28 anchors reviewed. Rounded toroidal coil replaces the flat front collar; all51 other raw mesh/UV/material signatures remain unchanged. Nine power-cell/connector instances share a Y-scale .7 about Y=.35 to recover rounded proportions; all42 other source poses remain unchanged. Root unit scale. Exact engineering dimensions, hidden winding, camera interpolation and ship attachment remain interpretations.'])
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');print('STATIC_INDUCER_READY',len(meshes))
