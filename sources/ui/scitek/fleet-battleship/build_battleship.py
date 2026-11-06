"""Preserve existing PS06 ship; add source-observed ST09 lower field sensor and technical curves."""
import bpy,bmesh,sys,math,json,hashlib,tempfile
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='e28f83b6d9100af1646a04521a2d508644a406b3a8feeb40780d61ad271f8372'
(out/'tmp').mkdir(exist_ok=True);tempfile.tempdir=str(out/'tmp');s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Fleet Battleship ')]
root=bpy.data.objects.new('BattleshipResearchRoot',None);s.collection.objects.link(root);meshes=[]
for ob in dst.objects:
 if ob.type!='MESH':continue
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
assert len(meshes)==35
sensor=g.material('Research sensor worn bronze',(.24,.16,.08),.7,.65);sensor.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=sensor.diffuse_color
new=[]
def add(ob):ob.parent=root;meshes.append(ob);new.append(ob);return ob
add(g.uv('Research field sensor housing',(0,-2.6,-.23),(.055,.20,.06),sensor))
add(g.tube('Research field sensor mount',(0,-2.25,-.08),(0,-2.50,-.23),.025,sensor))
add(g.tube('Research field sensor probe',(0,-2.76,-.23),(0,-3.35,-.23),.008,sensor))
add(g.uv('Research field sensor probe bulb',(0,-3.10,-.23),(.020,.045,.020),sensor))
for y in [-2.55,-2.63]:add(g.tube('Research sensor wear seam',(0,-2.5 if y==-2.55 else -2.60,-.174),(.018,y,-.174),.002,g.dark))

wingmetal=g.material('Research wingtip weathered alloy',(.21,.20,.24),.7,.64)
for side in [-1,1]:
 x=side*2.35;cy=-.47;z=.225;profile=[(cy+.16,.10),(cy+.10,.12),(cy-.15,.12),(cy-.30,.045),(cy-.38,.005)];N=40
 verts=[(x+r*math.cos(i*math.tau/N),y,z+r*math.sin(i*math.tau/N)) for y,r in profile for i in range(N)];faces=[tuple(reversed(range(N))),tuple(range((len(profile)-1)*N,len(profile)*N))]
 for j in range(len(profile)-1):
  for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 data=bpy.data.meshes.new('Research wingtip housing');data.from_pydata(verts,[],faces);data.update();ob=bpy.data.objects.new('Research wingtip housing '+str(side),data);s.collection.objects.link(ob);g.finish(ob,wingmetal,ob.name);add(ob)
 add(g.tube('Research wingtip wear '+str(side),(x+.01,cy+.09,z+.120),(x+.025,cy+.06,z+.118),.002,g.dark))
assert len(meshes)==45

parts={k:[] for k in ['chassis','rear-thruster','wingtip-directional-thrusters','antenna-and-field-sensor']}
for ob in meshes:
 role='chassis'
 if any(t in ob.name for t in ['central exhaust','exhaust throat','cooling rib']):role='rear-thruster'
 elif any(n in ob.name for n in ['tip fairing','tip probe','Research wingtip']):role='wingtip-directional-thrusters'
 elif (ob in new and 'wingtip' not in ob.name) or 'bow probe' in ob.name:role='antenna-and-field-sensor'
 parts[role].append(ob)
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);wires={}
for role,obs in parts.items():
 data=bpy.data.curves.new(role+' technical wire','CURVE');data.dimensions='3D';data.bevel_depth=.004;data.bevel_resolution=0
 for ob in obs:
  if 'wear seam' in ob.name:continue
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update();ys=sorted({round((ob.matrix_basis@v.co).y,5) for v in bm.verts});xs=sorted({round((ob.matrix_basis@v.co).x,5) for v in bm.verts})
  for edge in bm.edges:
   a,b=[ob.matrix_basis@v.co for v in edge.verts];angle=edge.calc_face_angle(0) if len(edge.link_faces)==2 else math.pi
   if 'continuous arched wing' in ob.name:
    if abs(a.x-b.x)<1e-6:
     row=min(range(len(xs)),key=lambda j:abs(xs[j]-a.x))
     if row%8:continue
    elif angle<.012:continue
   elif 'long central hull' in ob.name or 'central engine housing' in ob.name:
    if abs(a.y-b.y)<1e-6:
     row=min(range(len(ys)),key=lambda j:abs(ys[j]-a.y))
     if row%4:continue
    elif round(math.atan2(a.z-.05,a.x)/math.tau*64)%4:continue
   elif angle<.012:continue
   spl=data.splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
  bm.free()
 ob=bpy.data.objects.new(role+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(mat);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler=(0,0,-(f-1)*math.tau/60);root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,0));g.camera.location=(-6,-9,8);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=8.2;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fleet-battleship.blend'))
# Export mapped existing materials unchanged; only procedural new materials need a portable base value.
saved=[]
for m in [sensor,wingmetal,g.dark]:
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color
 for slot in ['Base Color','Normal']:
  for link in list(bs.inputs[slot].links):saved.append((m.node_tree,link.from_socket,link.to_socket));m.node_tree.links.remove(link)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in meshes:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'fleet-battleship.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
for nt,a,b in saved:nt.links.new(a,b)
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,0)
for ob in meshes:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
phases=[]
for i,role in enumerate(['rear-thruster','wingtip-directional-thrusters','antenna-and-field-sensor']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,1.15,-.18],[2.35,-.6,.23],[0,-2.82,-.10]][i],closeup_rotation_euler=[[.5,.4,math.pi-.45],[-math.pi/2,0,0],[0,0,-math.pi/2]][i],ortho_scale=[1.45,.90,1.80][i]))
model=dict(id='scitek:fleet-battleship',legacy_index=9,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,-.3,0],whole_information_rotation_euler=[.65,0,.75],whole_information_ortho_scale=10.5,information_timeline_frames=423,base_source_sha256=digest,source_mesh_count=35,new_presentation_meshes=[o.name for o in new],limitations=['Existing ship preserved; source-observed lower field sensor is an authored approximation. Camera, pose and wire topology approximate legacy.'])
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(base.read_bytes()).hexdigest()==digest;print('BATTLESHIP_VARIANTS_READY')
