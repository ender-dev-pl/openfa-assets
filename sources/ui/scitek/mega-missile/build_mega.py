"""PM09/ST13 research presentation: reuse 64 meshes, add four observed thrust lobes."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='f2d64f7510bcc84f1a5a43b21f9447b30c54a65d154609ebcfd5c1f59c1af3de'
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Mega ')]
root=bpy.data.objects.new('MegaResearchRoot',None);s.collection.objects.link(root);meshes=[]
for ob in dst.objects:
 if ob.type!='MESH':continue
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
assert len(meshes)==64
copper=g.material('Research thruster weathered copper',(.35,.17,.08),.65,.63);new=[]
for i in range(4):
 a=i*math.tau/4;radial=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-math.sin(a),math.cos(a),0));centre=radial*.30+Vector((0,0,.45));ob=g.uv('Research directional thrust chamber '+str(i),centre,(.27,.27,.40),copper);ob.parent=root;meshes.append(ob);new.append(ob)
 p=centre+radial*.268+Vector((0,0,.02));ob=g.tube('Research chamber wear seam '+str(i),p-tangent*.02,p+tangent*.02,.003,g.dark);ob.parent=root;meshes.append(ob);new.append(ob)
assert len(meshes)==72
parts={k:[] for k in ['chassis','four-directional-thrusters','manoeuvring-fins','nose-guidance-sensors']}
for ob in meshes:
 role='chassis'
 if ob in new:role='four-directional-thrusters'
 elif 'vane' in ob.name:role='manoeuvring-fins'
 elif any(n in ob.name for n in ['ivory nose cone','copper nose tip','short nose pin']):role='nose-guidance-sensors'
 parts[role].append(ob)
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);wires={}
for role,obs in parts.items():
 data=bpy.data.curves.new(role+' technical wire','CURVE');data.dimensions='3D';data.bevel_depth=.003;data.bevel_resolution=0
 def line(points):
  spl=data.splines.new('POLY');spl.points.add(len(points)-1)
  for p,v in zip(spl.points,points):p.co=(*v,1)
 for ob in obs:
  if 'wear' in ob.name.lower():continue
  if any(n in ob.name for n in ['thick copper lower panel','hollow lower casing','hollow copper nozzle','annular nozzle support','recessed throat']):continue
  if ob.name.startswith('Research directional thrust chamber'):
   for mode in ['meridian','parallel']:
    for j in range(16 if mode=='meridian' else 11):
     points=[]
     for k in range(65):
      a=k*math.tau/64;b=j*math.tau/16 if mode=='meridian' else (j+1)*math.pi/12
      p=ob.location+Vector((.27*math.sin(a)*math.cos(b),.27*math.sin(a)*math.sin(b),.40*math.cos(a))) if mode=='meridian' else ob.location+Vector((.27*math.sin(b)*math.cos(a),.27*math.sin(b)*math.sin(a),.40*math.cos(b)));points.append(p)
     line(points)
   continue
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
  for edge in bm.edges:
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_basis@v.co for v in edge.verts]
   if len(bm.verts)>300 and abs(a.z-b.z)>1e-5 and round(math.atan2(a.y,a.x)/math.tau*64)%2:continue
   line([a,b])
  bm.free()
 ob=bpy.data.objects.new(role+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,3.1));g.camera.location=(0,-12,5);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=7.7;s.render.resolution_x=320;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'mega-missile.blend'));saved=[]
for m in [copper,g.dark]:
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color
 for slot in ['Base Color','Normal']:
  for link in list(bs.inputs[slot].links):saved.append((m.node_tree,link.from_socket,link.to_socket));m.node_tree.links.remove(link)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in meshes:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'mega-missile.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
for nt,a,b in saved:nt.links.new(a,b)
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,0)
for ob in meshes:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(['four-directional-thrusters','manoeuvring-fins','nose-guidance-sensors']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,0,.45],[0,0,2.65],[0,0,5.65]][i],closeup_rotation_euler=[[0,0,0],[0,0,0],[0,0,0]][i],ortho_scale=[1.9,3.8,2.1][i]))
(out/'model.json').write_text(json.dumps(dict(id='scitek:mega-missile',legacy_index=13,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,3.1],whole_information_rotation_euler=[0,0,0],whole_information_ortho_scale=11.5,information_timeline_frames=423,base_source_sha256=digest,preserved_source_meshes=64,new_presentation_meshes=[o.name for o in new],directional_thrust_chambers=4,limitations=['Existing threefold fins/lower armour retained; four thrust chambers follow explicit source caption and visible lobes. Hidden construction, poses and camera are authored approximations.']),indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(base.read_bytes()).hexdigest()==digest;print('MEGA_VARIANTS_READY')
