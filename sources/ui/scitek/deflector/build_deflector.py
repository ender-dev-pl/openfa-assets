"""Reuse unchanged PH10 source meshes and maps; author technical presentation curves."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True);base=Path(sys.argv[sys.argv.index('--')+2]).resolve();digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='a55e8430133da4b6df86610c53eb4d6f08f24bf480e8d2106fb9ed320879c0ed'
import tempfile
(out/'tmp').mkdir(exist_ok=True);tempfile.tempdir=str(out/'tmp')
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith('Deflector ')]
root=bpy.data.objects.new('DeflectorResearchRoot',None);s.collection.objects.link(root);meshes=[]
for ob in dst.objects:
 if ob.type!='MESH':continue
 s.collection.objects.link(ob);ob.parent=root;meshes.append(ob)
assert len(meshes)==35
parts={k:[] for k in ['chassis','energising-nose-cone','overpressure-relief-valve','auxiliary-electronics']}
for ob in meshes:
 role='chassis'
 if 'ribbed taper' in ob.name or 'taper rib' in ob.name:role='energising-nose-cone'
 elif 'red rear pin' in ob.name:role='overpressure-relief-valve'
 elif any(t in ob.name for t in ['side boss','rear bracket','rear conduit','bracket bolt','service','fastener']):role='auxiliary-electronics'
 parts[role].append(ob)
def emission(name,color):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=color;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0]);return mat
green=emission('Technical green',(0,.72,.005,1));curves={};wires={}
for role in parts:
 data=bpy.data.curves.new(role+' technical wire','CURVE');data.dimensions='3D';data.bevel_depth=.0015;data.bevel_resolution=0;curves[role]=data
for role,obs in parts.items():
 for ob in obs:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
  for edge in bm.edges:
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[ob.matrix_basis@v.co for v in edge.verts];dest=role
   if any(token in ob.name for token in ['spherical shell','ribbed taper','red rear pin']):
    if abs(a.y-b.y)<1e-6:
     heights=sorted({round(v.co.y,5) for v in bm.verts});row=min(range(len(heights)),key=lambda j:abs(heights[j]-a.y))
     if row%2:continue
    else:
     az=round(math.atan2(a.z,a.x)/math.tau*128)%128
     if az%4:continue
   if 'taper rib' in ob.name:
    radius=max(math.hypot(v.co.x,v.co.z) for v in bm.verts)
    if min(math.hypot(a.x,a.z),math.hypot(b.x,b.z))<radius*.95:continue
    if abs(a.y-b.y)>1e-6 and round(math.atan2(a.z,a.x)/math.tau*128)%8:continue
   # Source highlights only the distal energising portion, not the entire taper.
   if role=='energising-nose-cone' and (a.y+b.y)/2>-.55:dest='chassis'
   # Keep small fasteners readable without dense triangulation.
   if 'fastener' in ob.name and edge.index%3:continue
   spl=curves[dest].splines.new('POLY');spl.points.add(1);spl.points[0].co=(*a,1);spl.points[1].co=(*b,1)
  bm.free()
for role,data in curves.items():
 ob=bpy.data.objects.new(role+' technical wire',data);s.collection.objects.link(ob);ob.parent=root;ob.data.materials.append(green);ob.hide_render=True;wires[role]=ob
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler=(0,0,math.pi/2-(f-1)*math.tau/60);root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
s.frame_set(1);target=Vector((0,0,0));g.camera.location=(0,-8,4);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=2.65;s.render.resolution_x=576;s.render.resolution_y=640;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(out/'deflector.blend'))
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for ob in objects:ob.select_set(True)
 temporary=[]
 for mat in {m for ob in objects for m in ob.data.materials if m and m.use_nodes}:
  nt=mat.node_tree;em=nt.nodes.get('Emission')
  if not em:continue
  output=nt.nodes.get('Material Output');rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=em.inputs['Color'].default_value;nt.links.new(rgb.outputs[0],output.inputs['Surface']);temporary.append((nt,em,output,rgb))
 bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
 for nt,em,output,rgb in temporary:nt.links.new(em.outputs[0],output.inputs['Surface']);nt.nodes.remove(rgb)
export('deflector.glb',meshes);s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
root.animation_data_clear();root.rotation_euler=(0,0,math.pi/2)
for ob in meshes:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True);export('deflector-wireframe.glb',list(wires.values()))
phases=[]
for i,role in enumerate(['energising-nose-cone','overpressure-relief-valve','auxiliary-electronics']):phases.append(dict(component=role,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=[[0,-.77,0],[0,.52,0],[0,0,0]][i],closeup_rotation_euler=[[-math.pi/2,0,0],[math.pi/2,0,0],[-math.pi/2,0,.1]][i],ortho_scale=[1.2,.78,2.25][i]))
model=dict(id='scitek:deflector',legacy_index=8,components={k:[ob.name for ob in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,-.15,0],whole_information_rotation_euler=[0,0,math.pi/2],whole_information_ortho_scale=4.8,information_timeline_frames=423,base_source_sha256=digest,source_mesh_count=35,limitations=['Existing authored source geometry preserved. Distal cone wire classification is an authored approximation. Cameras and topology approximate actual legacy views.'])
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('DEFLECTOR_VARIANTS_READY')
