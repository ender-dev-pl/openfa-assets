"""PM06/ST16 presentation variant: preserve 19 meshes, complete upper manoeuvring set."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='4cb6c68243a2ff7ea0b1cf8395d8810243a6714cf6b5e1c773738dbb867c4db6'
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Nuclear ')]
root=bpy.data.objects.new('NuclearResearchRoot',None);s.collection.objects.link(root);meshes=[]
for ob in dst.objects:
 if ob.type!='MESH':continue
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
assert len(meshes)==19
silver=g.material('Research rear airbrake worn silver',(.32,.36,.40),.74,.50)
for node in silver.node_tree.nodes:
 if node.type=='BUMP':node.inputs['Distance'].default_value=.0018
 if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=80
new=[]
for i,ob in enumerate([o for o in meshes if 'upper silver side form' in o.name]):
 rear=ob.copy();rear.data=ob.data.copy();rear.name='Research rear manoeuvring airbrake '+str(i);s.collection.objects.link(rear);rear.rotation_euler.z+=math.pi;rear.data.materials.clear();rear.data.materials.append(silver);meshes.append(rear);new.append(rear)
assert len(new)==2 and len(meshes)==21
parts={k:[] for k in ['chassis','four-delivery-thrusters','air-brake-manoeuvring-system','atomic-warhead-nose']}
for ob in meshes:
 role='chassis'
 if 'red tail pod' in ob.name or 'silver tail foot' in ob.name:role='four-delivery-thrusters'
 elif 'upper silver side form' in ob.name or ob in new:role='air-brake-manoeuvring-system'
 elif 'long yellow tip' in ob.name or 'tip seating ring' in ob.name:role='atomic-warhead-nose'
 parts[role].append(ob)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);curves={};wires={}
for role in parts:
 data=bpy.data.curves.new(role+' technical wire','CURVE');data.dimensions='3D';data.bevel_depth=.003;data.bevel_resolution=0;curves[role]=data
for role,obs in parts.items():
 for ob in obs:
  if 'trefoil' in ob.name:continue
  shaped=any(n in ob.name for n in ['red tail pod','upper silver side form','Research rear manoeuvring'])
  data=bpy.data.meshes.new_from_object(ob.evaluated_get(deps)) if shaped else ob.data
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update();rows={}
  if shaped:
   for v in bm.verts:rows.setdefault(round(v.co.z,5),[]).append(v.co)
   heights=sorted(rows);centres={z:sum(rows[z],Vector())/len(rows[z]) for z in heights}
  for edge in bm.edges:
   a0,b0=[v.co for v in edge.verts]
   if shaped:
    if abs(a0.z-b0.z)<1e-5:
     row=min(range(len(heights)),key=lambda i:abs(heights[i]-a0.z))
     if row%2:continue
    else:
     z=min(heights,key=lambda z:abs(z-a0.z));c=centres[z]
     if round(math.atan2(a0.y-c.y,a0.x-c.x)/math.tau*256)%8:continue
   elif len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_basis@v for v in [a0,b0]];dest='atomic-warhead-nose' if 'pressure casing' in ob.name and (a.z+b.z)/2>=4.70 else role
   spl=curves[dest].splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
  bm.free()
  if shaped:bpy.data.meshes.remove(data)
for role,data in curves.items():
 ob=bpy.data.objects.new(role+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,3.1));g.camera.location=(0,-12,4.8);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=7.4;s.render.resolution_x=320;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'nuclear-missile.blend'));saved=[];bs=silver.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=silver.diffuse_color
for slot in ['Base Color','Normal']:
 for link in list(bs.inputs[slot].links):saved.append((silver.node_tree,link.from_socket,link.to_socket));silver.node_tree.links.remove(link)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in meshes:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'nuclear-missile.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
for nt,a,b in saved:nt.links.new(a,b)
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,0)
for ob in meshes:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
phases=[];top_pose=list((Matrix.Rotation(math.pi/2,3,'X')@Matrix.Rotation(math.pi/4,3,'Z')).to_euler('XYZ'))
for i,role in enumerate(['four-delivery-thrusters','air-brake-manoeuvring-system','atomic-warhead-nose']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,0,1.05],[0,0,4.45],[0,0,5.45]][i],closeup_rotation_euler=[[0,0,.30],top_pose,[0,0,0]][i],ortho_scale=[2.6,2.7,2.2][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:nuclear-missile',legacy_index=16,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,3.1],whole_information_rotation_euler=[0,0,0],whole_information_ortho_scale=10.5,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=19,new_presentation_meshes=[o.name for o in new],delivery_thrusters=4,manoeuvring_forms=4,limitations=['Two rear manoeuvring forms supplement the original two; observed fourfold layout is approximated using existing geometry. Nose technical selection includes casing above4.70. Camera, hidden geometry and wire topology are authored.']),indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(base.read_bytes()).hexdigest()==digest;print('NUCLEAR_VARIANTS_READY')
