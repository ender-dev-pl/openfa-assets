import bpy,sys,json,struct
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();info=Path(sys.argv[sys.argv.index('--')+2]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'nuclear-missile.blend'));s=bpy.context.scene;root=bpy.data.objects['NuclearResearchRoot'];root.animation_data_clear();root.rotation_euler=(0,0,0)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in s.objects:
 if not ob.name.endswith(' technical wire'):continue
 ob.select_set(True);nt=ob.data.materials[0].node_tree;em=nt.nodes.get('Emission');output=nt.nodes.get('Material Output');rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=(0,.72,.005,1);nt.links.new(rgb.outputs[0],output.inputs['Surface'])
bpy.ops.export_scene.gltf(filepath=str(out/'nuclear-missile-wireframe.glb'),use_selection=True,export_apply=True,export_animations=False,export_format='GLB')
model=json.loads((out/'model.json').read_text());timeline=json.loads((info/'information-timeline.json').read_text())['timeline'];proof=[]
for name,f in [('wireframe',None)]+[('highlight-'+p['component'],f) for p,f in zip(model['phases'],[87,228,369])]:
 for ob in list(s.objects):
  if ob.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(ob,do_unlink=True)
 path=out/('nuclear-missile-'+name+'.glb');raw=path.read_bytes();length=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+length]);assert all('KHR_materials_unlit' in m.get('extensions',{}) for m in d['materials'])
 bpy.ops.import_scene.gltf(filepath=str(path));s.frame_set(1);s.cycles.samples=8;s.view_settings.view_transform='Standard';s.render.resolution_x=640;s.render.resolution_y=640
 if f is not None:
  t=timeline[f];s.camera.location=t['camera_position'];s.camera.rotation_euler=t['camera_euler'];s.camera.data.ortho_scale=t['ortho_scale']
 s.render.filepath=str(out/('imported-'+name+'.png'));bpy.ops.render.render(write_still=True);proof.append(dict(variant=name,independent_import=True,all_materials_unlit=True))
(out/'static-import-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('ENGINE_STATIC_IMPORTS_VERIFIED')
