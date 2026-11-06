import bpy,sys,json,struct
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();info=Path(sys.argv[sys.argv.index('--')+2]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'shield-x40.blend'));s=bpy.context.scene;root=bpy.data.objects['ShieldX40Root'];root.animation_data_clear();root.rotation_euler=(0,0,0)
s.view_settings.view_transform='Standard';s.cycles.samples=8;s.render.resolution_x=640;s.render.resolution_y=640
for ob in s.objects:
 if ob.type=='MESH':ob.hide_render=True
 if ob.name.endswith(' technical wire'):ob.hide_render=False
s.render.filepath=str(out/'wireframe.png');bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in s.objects:
 if not ob.name.endswith(' technical wire'):continue
 ob.select_set(True);nt=ob.data.materials[0].node_tree;em=nt.nodes.get('Emission');output=nt.nodes.get('Material Output');rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=(0,.72,.005,1);nt.links.new(rgb.outputs[0],output.inputs['Surface'])
bpy.ops.export_scene.gltf(filepath=str(out/'shield-x40-wireframe.glb'),use_selection=True,export_apply=True,export_animations=False,export_format='GLB')
model=json.loads((out/'model.json').read_text());timeline=json.loads((info/'information-timeline.json').read_text())['timeline'];proof=[]
for name,f in [('wireframe',None)]+[('highlight-'+p['component'],f) for p,f in zip(model['phases'],[87+141*i for i in range(len(model['phases']))])]:
 for ob in list(s.objects):
  if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
 path=out/('shield-x40-'+name+'.glb');raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+length]);assert all('KHR_materials_unlit' in m.get('extensions',{}) for m in d['materials'])
 colours={m['name']:m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1]) for m in d['materials']}
 bpy.ops.import_scene.gltf(filepath=str(path))
 # Reconstruct the direct unlit shader from the actual exported linear RGBA,
 # matching the client contract, rather than Blender's glTF shader wrapper.
 for ob in s.objects:
  if ob.type!='MESH':continue
  node=next(n for n in d['nodes'] if n.get('name')==ob.name and 'mesh' in n)
  index=d['meshes'][node['mesh']]['primitives'][0]['material'];colour=d['materials'][index].get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1])
  for mat in ob.data.materials:
   nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=colour;output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
 s.frame_set(1);s.cycles.samples=8;s.view_settings.view_transform='Standard';s.render.resolution_x=640;s.render.resolution_y=640
 s.render.film_transparent=f is None
 if f is not None:
  # Native closeups come from the information scene (opaque black), whereas
  # the whole wireframe comes from the transparent studio source.
  s.world.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=0
  t=timeline[f];s.camera.location=t['camera_position'];s.camera.rotation_euler=t['camera_euler'];s.camera.data.ortho_scale=t['ortho_scale']
 s.render.filepath=str(out/('imported-'+name+'.png'));bpy.ops.render.render(write_still=True);proof.append(dict(variant=name,independent_import=True,all_materials_unlit=True))
(out/'static-import-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('ENGINE_STATIC_IMPORTS_VERIFIED')
