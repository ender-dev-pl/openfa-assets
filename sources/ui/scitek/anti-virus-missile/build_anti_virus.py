"""Sci-Tek PM08/ST03 presentation derived from the unchanged authored missile."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
relative_base='sources/docs/assets/reconstruction/missiles/terran/anti-virus/model.blend'
base=Path(sys.argv[sys.argv.index('--base-blend')+1]).resolve() if '--base-blend' in sys.argv else next(p/relative_base for p in Path(__file__).resolve().parents if (p/relative_base).is_file())
digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='83795063d7b9bfb688abd34e13a0b054a702fb82eabf5800db09e4a3abb84283'
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(g.__file__)]}
s=g.scene;s.cycles.samples=16
with bpy.data.libraries.load(str(base),link=False) as (src,dst):dst.objects=[n for n in src.objects if n.startswith(('Anti Virus ','Virus family '))]
objects=[ob for ob in dst.objects if ob and ob.type=='MESH'];assert len(objects)==19
for ob in objects:s.collection.objects.link(ob)
bpy.context.view_layer.update()
def signature(ob):
 d=ob.data;return hashlib.sha256(json.dumps(dict(matrix=[v for row in ob.matrix_basis for v in row],vertices=[list(v.co) for v in d.vertices],faces=[list(f.vertices)+[f.material_index] for f in d.polygons],uv=[[list(x.uv) for x in layer.data] for layer in d.uv_layers],materials=[m.name for m in d.materials]),separators=(',',':')).encode()).hexdigest()
before={ob.name:signature(ob) for ob in objects}
root=bpy.data.objects.new('AntiVirusRotor',None);s.collection.objects.link(root);root.scale=(.83,.83,1)
roles=['chassis','anti-viral-payload-pods','four-main-rocket-thrusters','nose-navigation-assembly'];parts={k:[] for k in roles}
for ob in objects:
 name=ob.name
 role=roles[1] if name.startswith('Anti Virus long violet side form') else roles[2] if name.startswith(('Virus family hollow red nozzle','Virus family recessed nozzle throat')) else roles[3] if name.startswith(('Anti Virus pale nose collar','Virus family red nose cap','Anti Virus shorter antenna','Virus family upper neck joint')) else roles[0]
 ob.parent=root;ob['scitek_component']=role;parts[role].append(ob)
component_names={k:[ob.name for ob in v] for k,v in parts.items()}
def emit(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*c,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
green=emit('ST03 technical green',(0,.72,.005));red=emit('ST03 selected red',(.9,.003,.001));wires={};data={k:bpy.data.curves.new(k+' wire edges','CURVE') for k in roles}
for d in data.values():d.dimensions='3D';d.bevel_depth=.003;d.bevel_resolution=0
bpy.context.view_layer.update();partitioned=0
for group,obs in parts.items():
 for ob in obs:
  for edge in ob.data.edges:
   a,b=[root.matrix_world.inverted()@ob.matrix_world@ob.data.vertices[i].co for i in edge.vertices];target=group
   # Display-only semantic partition; the original continuous casing is intact.
   if ob.name=='Anti Virus long-neck pressure casing' and min(a.z,b.z)>=4.3999:target=roles[3];partitioned+=1
   sp=data[target].splines.new('POLY');sp.points.add(1)
   for p,v in zip(sp.points,[a,b]):p.co=(*v,1)
for k,d in data.items():
 ob=bpy.data.objects.new(k+' technical wire',d);s.collection.objects.link(ob);ob.parent=root;d.materials.append(green);ob.hide_render=True;wires[k]=ob
g.camera.location=(0,-12,3.6);target=Vector((0,0,3.05));g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=7.4
s.render.resolution_x=320;s.render.resolution_y=640;s.render.film_transparent=True
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for frame in [1,16,31,46,61]:root.rotation_euler.z=-(frame-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=frame)
for fc in root.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
cm=g.camera.rotation_euler.to_matrix();right,up=cm.col[0],cm.col[1];projected=[];extent=0;aspect=.5
for frame in range(1,61):
 s.frame_set(frame);bpy.context.view_layer.update();pts=[ob.matrix_world@v.co for ob in objects for v in ob.data.vertices];xs=[(p-g.camera.location).dot(right) for p in pts];ys=[(p-g.camera.location).dot(up) for p in pts]
 extent=max(extent,2*max(abs(min(xs)),abs(max(xs)))/aspect,2*max(abs(min(ys)),abs(max(ys))));projected.append([min(xs),min(ys),max(xs),max(ys)])
g.camera.data.ortho_scale=max(7.4,math.ceil(extent*1.06*100)/100)
framing=dict(frame_count=60,ortho_scale=g.camera.data.ortho_scale,ndc_bounds=[[.5+a/(g.camera.data.ortho_scale*aspect),.5+b/g.camera.data.ortho_scale,.5+c/(g.camera.data.ortho_scale*aspect),.5+d/g.camera.data.ortho_scale] for a,b,c,d in projected])
def render(name):s.render.filepath=str(out/name);bpy.ops.render.render(write_still=True)
def export(name,obs):
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for ob in obs:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(out/name),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
s.frame_set(1);render('solid.png');bpy.ops.wm.save_as_mainfile(filepath=str(out/'anti-virus-missile.blend'));export('anti-virus-missile.glb',objects)
assert before=={ob.name:signature(ob) for ob in objects}
root.animation_data_clear();root.rotation_euler=(0,0,0)
for ob in objects:ob.hide_render=True
for ob in wires.values():ob.hide_render=False
s.cycles.samples=4;s.view_settings.view_transform='Standard';s.render.resolution_x=896;s.render.resolution_y=896
whole_scale=10.6;whole_target=[0,0,3.05];whole_info_euler=list(Matrix((cm.col[0],-cm.col[2],cm.col[1])).to_euler('XYZ'));g.camera.data.ortho_scale=whole_scale
render('wireframe.png');export('anti-virus-missile-wireframe.glb',list(wires.values()));wire_cameras={'wireframe':(g.camera.matrix_world.copy(),g.camera.data.ortho_scale)};phases=[]
targets={roles[1]:(0,0,2.9),roles[2]:(0,0,.26),roles[3]:(0,0,5.2)};scales={roles[1]:2.8,roles[2]:1.2,roles[3]:2.0};angles={roles[1]:(0,0,30),roles[2]:(0,0,15),roles[3]:(0,0,0)}
for i,group in enumerate(roles[1:]):
 for k,ob in wires.items():ob.data.materials[0]=red if k==group else green
 root.rotation_euler=[math.radians(a) for a in angles[group]];bpy.context.view_layer.update();local=Vector(targets[group]);target=root.matrix_world@local
 g.camera.location=(target.x,target.y-12,target.z+.15);g.camera.rotation_euler=(target-g.camera.location).to_track_quat('-Z','Y').to_euler();g.camera.data.ortho_scale=scales[group]
 name='highlight-'+group;render(name+'.png');export('anti-virus-missile-'+name+'.glb',list(wires.values()));wire_cameras[name]=(g.camera.matrix_world.copy(),g.camera.data.ortho_scale)
 phases.append(dict(component=group,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=list(local),closeup_rotation_euler=list(root.rotation_euler),ortho_scale=scales[group],highlight_glb='anti-virus-missile-'+name+'.glb'))
bpy.ops.wm.open_mainfile(filepath=str(out/'anti-virus-missile.blend'));s=bpy.context.scene
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'anti-virus-missile.glb'));render('imported-solid.png')
for name,(camera,scale) in wire_cameras.items():
 for ob in list(s.objects):
  if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(out/('anti-virus-missile-'+name+'.glb')));s.camera.matrix_world=camera;s.camera.data.ortho_scale=scale;s.cycles.samples=4;s.view_settings.view_transform='Standard';s.render.resolution_x=896;s.render.resolution_y=896;render('imported-'+name+'.png')
bpy.ops.wm.open_mainfile(filepath=str(out/'anti-virus-missile.blend'));s=bpy.context.scene;render('reload-solid.png')
model=dict(issue=208,id='scitek:anti-virus-missile',legacy_index=3,source='_MA/PM08.256 + PM08.VID; _SCITEK/ST03.VID',components=component_names,phases=phases,information_timeline_frames=423,root_scale=[.83,.83,1],solid_framing=framing,whole_information_rotation_euler=whole_info_euler,whole_information_local_target=whole_target,whole_information_ortho_scale=whole_scale,base_source=dict(path=relative_base,sha256=digest,status='All nineteen meshes, original local transforms, UVs and materials preserved; presentation root applies transverse scale .83; no wear retrofit'),base_mesh_signatures=before,technical_partition=dict(object='Anti Virus long-neck pressure casing',nose_edges_min_z=4.3999,assigned_edge_count=partitioned,method='Display-only edges above the upper neck joint; solid mesh remains intact'))
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n');(out/'source-hashes.json').write_text(json.dumps(source_hashes,indent=2)+'\n');assert hashlib.sha256(base.read_bytes()).hexdigest()==digest
print('ANTI_VIRUS_VARIANTS_READY')
