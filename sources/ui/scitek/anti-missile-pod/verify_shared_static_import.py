import bpy,sys,json,struct
from pathlib import Path
out,info=map(lambda p:Path(p).resolve(),sys.argv[sys.argv.index('--')+1:]);model=json.loads((out/'model.json').read_text());timeline=json.loads((info/'information-timeline.json').read_text())['timeline']
bpy.ops.wm.open_mainfile(filepath=str(info/'anti-missile-pod-information.blend'));s=bpy.context.scene;s.frame_set(1)
proof=[]
for variant,frame in [('wireframe',0)]+[('highlight-'+phase['component'],f) for phase,f in zip(model['phases'],[87,228,369])]:
 for ob in list(s.objects):
  if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
 path=out/('anti-missile-pod-'+variant+'.glb');raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];data=json.loads(raw[20:20+length]);assert all('KHR_materials_unlit' in m.get('extensions',{}) for m in data['materials'])
 bpy.ops.import_scene.gltf(filepath=str(path))
 for ob in s.objects:
  if ob.type!='MESH':continue
  node=next(n for n in data['nodes'] if n.get('name')==ob.name and 'mesh' in n);index=data['meshes'][node['mesh']]['primitives'][0]['material'];colour=data['materials'][index]['pbrMetallicRoughness'].get('baseColorFactor',[1,1,1,1])
  for mat in ob.data.materials:
   nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=colour;o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],o.inputs[0])
 s.camera.animation_data_clear();s.camera.data.animation_data_clear();t=timeline[frame];s.camera.location=t['camera_position'];s.camera.rotation_euler=t['camera_euler'];s.camera.data.ortho_scale=t['ortho_scale']
 s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=4;s.render.filepath=str(out/('imported-'+variant+'.png'));bpy.ops.render.render(write_still=True);proof.append(dict(variant=variant,frame=frame,independent_import=True,all_materials_unlit=True))
(out/'static-import-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('POD_SHARED_STATIC_IMPORTS_VERIFIED')
