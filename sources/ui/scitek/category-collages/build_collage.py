"""Build a static category collage from preserved, already-authored subjects.

Blender CLI: -- MANIFEST OUTPUT ASSET_ROOT. No legacy pixels are loaded.
"""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args=sys.argv[sys.argv.index('--')+1:]
manifest_path=Path(args[0]).resolve();out=Path(args[1]).resolve();assets=Path(args[2]).resolve();out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(Path(__file__).resolve().parent));import geometry as g
spec=json.loads(manifest_path.read_text());s=g.scene;s.cycles.samples=16
s.render.resolution_x=800;s.render.resolution_y=640;s.render.film_transparent=True;s.view_settings.view_transform='AgX'
cam=s.camera;cam.location=(4,-10,6);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=8
root=bpy.data.objects.new('ScitekCategoryRoot',None);s.collection.objects.link(root)
all_meshes=[];groups={};provenance=[];materials={}
def signature(ob):
 if ob.type=='CURVE':
  d=dict(type='CURVE',dimensions=ob.data.dimensions,bevel_depth=ob.data.bevel_depth,bevel_resolution=ob.data.bevel_resolution,resolution_u=ob.data.resolution_u,fill_caps=ob.data.use_fill_caps,splines=[dict(type=sp.type,cyclic=sp.use_cyclic_u,order=sp.order_u,points=[dict(co=list(p.co),radius=p.radius,tilt=p.tilt) for p in sp.points],bezier=[dict(co=list(p.co),left=list(p.handle_left),right=list(p.handle_right),radius=p.radius,tilt=p.tilt) for p in sp.bezier_points]) for sp in ob.data.splines])
 else:
  d=dict(type='MESH',vertices=[list(v.co) for v in ob.data.vertices],faces=[list(p.vertices) for p in ob.data.polygons],uv={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers})
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def luma(v):return sum(a*b for a,b in zip(v,[.2126,.7152,.0722]))
def neutral(original):
 key=original.as_pointer()
 if key in materials:return materials[key]
 mat=original.copy();mat.name='Category neutral '+original.name;
 if mat.use_nodes:mat.node_tree.animation_data_clear()
 mat.diffuse_color=(luma(original.diffuse_color),)*3+(original.diffuse_color[3],)
 if mat.use_nodes:
  bs=mat.node_tree.nodes.get('Principled BSDF')
  if bs:
   socket=bs.inputs['Base Color'];representative=luma(original.diffuse_color)*.72 if socket.is_linked else luma(socket.default_value)
   mat['category_portable_luminance']=representative
   for name in ['Base Color','Emission Color']:
    socket=bs.inputs.get(name)
    if not socket:continue
    if socket.is_linked:
     source=socket.links[0].from_socket;bw=mat.node_tree.nodes.new('ShaderNodeRGBToBW');mat.node_tree.links.new(source,bw.inputs[0]);mat.node_tree.links.new(bw.outputs[0],socket)
    else:socket.default_value=(luma(socket.default_value),)*3+(socket.default_value[3],)
 materials[key]=mat;return mat
def bounds(meshes):
 points=[];deps=bpy.context.evaluated_depsgraph_get()
 for ob in meshes:
  if abs(ob.matrix_world.to_3x3().determinant())<1e-12:continue
  evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh()
  points.extend(world_to_camera_view(s,cam,evaluated.matrix_world@v.co) for v in mesh.vertices);evaluated.to_mesh_clear()
 return [min(v.x for v in points),min(v.y for v in points),max(v.x for v in points),max(v.y for v in points)]
for subject in spec['subjects']:
 key=subject['key'];source=assets/subject['blend'];digest=hashlib.sha256(source.read_bytes()).hexdigest();model=json.loads((source.parent/'model.json').read_text());wanted={n for names in model['components'].values() for n in names}
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):names=list(src.objects);dst.objects=list(names)
 loaded=dict(zip(names,dst.objects));objects=[ob for n,ob in loaded.items() if n in wanted or ob.type=='EMPTY'];members=[loaded[n] for n in sorted(wanted)];originals={n:signature(loaded[n]) for n in sorted(wanted)}
 wrapper=bpy.data.objects.new(key+' placement',None);s.collection.objects.link(wrapper);wrapper.parent=root
 for ob in objects:s.collection.objects.link(ob)
 s.frame_set(subject['pose_frame']);bpy.context.view_layer.update()
 for ob in objects:ob.animation_data_clear()
 for ob in objects:
  if ob.parent not in objects:ob.parent=wrapper
  ob.name=key+'::'+ob.name
 for ob in members:
  ob.data=ob.data.copy()
  for slot in ob.material_slots:
   if slot.material:slot.material=neutral(slot.material)
  ob.hide_render=False
 groups[key]=[ob.name for ob in members];all_meshes.extend(members)
 bpy.context.view_layer.update();initial=bounds(members);x0,y0,x1,y1=subject['box'];target=[x0/80,1-y1/64,x1/80,1-y0/64]
 factor=min((target[2]-target[0])/(initial[2]-initial[0]),(target[3]-target[1])/(initial[3]-initial[1]));wrapper.scale=(factor,)*3;bpy.context.view_layer.update();fitted=bounds(members)
 dx=(target[0]+target[2]-fitted[0]-fitted[2])/2;dy=(target[1]+target[3]-fitted[1]-fitted[3])/2
 rotation=cam.rotation_euler.to_matrix();wrapper.location+=(rotation@Vector((1,0,0)))*(dx*8)+(rotation@Vector((0,1,0)))*(dy*6.4)
 bpy.context.view_layer.update();fitted=bounds(members)
 assert all(signature(ob)==originals[n] for n,ob in zip(sorted(wanted),members))
 provenance.append(dict(subject=key,source=subject['blend'],source_sha256=digest,pose_frame=subject['pose_frame'],mesh_signatures=originals,target_box=subject['box'],actual_normalized_box=fitted,wrapper=wrapper.name,mesh_names=groups[key]))
 assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
s.frame_start=1;s.frame_end=1;s.frame_set(1)
s.use_nodes=True;nt=s.node_tree;nt.nodes.clear();layers=nt.nodes.new('CompositorNodeRLayers');bw=nt.nodes.new('CompositorNodeRGBToBW');gain=nt.nodes.new('CompositorNodeMath');gain.operation='MULTIPLY';gain.inputs[1].default_value=spec['monochrome_gain'];alpha=nt.nodes.new('CompositorNodeSetAlpha');output=nt.nodes.new('CompositorNodeComposite');nt.links.new(layers.outputs['Image'],bw.inputs[0]);nt.links.new(bw.outputs[0],gain.inputs[0]);nt.links.new(gain.outputs[0],alpha.inputs['Image']);nt.links.new(layers.outputs['Alpha'],alpha.inputs['Alpha']);nt.links.new(alpha.outputs['Image'],output.inputs[0])
stem=spec['id'].split(':')[-1];blend=out/(stem+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend));s.render.filepath=str(out/'native.png');bpy.ops.render.render(write_still=True)
for key,names in groups.items():
 for ob in all_meshes:ob.hide_render=ob.name not in names
 s.render.filepath=str(out/(key+'.png'));bpy.ops.render.render(write_still=True)
for ob in all_meshes:ob.hide_render=False
# Portable neutral PBR uses representative values; native procedural wear is kept.
links=[];defaults=[]
for mat in set(m for ob in all_meshes for m in ob.data.materials if m):
 bs=mat.node_tree.nodes.get('Principled BSDF') if mat.use_nodes else None
 if not bs:continue
 defaults.append((bs.inputs['Base Color'],bs.inputs['Base Color'].default_value[:]))
 value=mat.get('category_portable_luminance',luma(mat.diffuse_color));bs.inputs['Base Color'].default_value=(value,value,value,1)
 for name in ['Base Color','Normal']:
  for link in list(bs.inputs[name].links):links.append((mat.node_tree,link.from_socket,link.to_socket));mat.node_tree.links.remove(link)
bpy.ops.object.select_all(action='DESELECT')
for ob in s.objects:
 if ob.type in ['MESH','CURVE','EMPTY']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/(stem+'.glb')),use_selection=True,export_apply=True,export_animations=False,export_format='GLB')
for nt,a,b in links:nt.links.new(a,b)
for socket,value in defaults:socket.default_value=value
(out/'provenance.json').write_text(json.dumps(dict(id=spec['id'],manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),subjects=provenance,mesh_count=len(all_meshes),native_mesh_count=sum(ob.type=='MESH' for ob in all_meshes),native_curve_count=sum(ob.type=='CURVE' for ob in all_meshes),blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/(stem+'.glb')).read_bytes()).hexdigest(),canvas=[80,64],render_canvas=[800,640],root=root.name,monochrome_gain=spec['monochrome_gain'],limitations=['Layout follows actual category sprite; neutral materials/lighting, poses and hidden geometry are authored approximations. Portable materials approximate native procedural wear.']),indent=2)+'\n')
print('SCITEK_CATEGORY_BUILT',stem,len(all_meshes))
