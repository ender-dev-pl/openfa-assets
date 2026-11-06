import bpy,sys,json
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();info=Path(sys.argv[sys.argv.index('--')+2]).resolve();bpy.ops.wm.open_mainfile(filepath=str(info/'solar-matrix-information.blend'));s=bpy.context.scene;model=json.loads((out/'model.json').read_text(encoding='utf-8'));s.render.resolution_x=640;s.render.resolution_y=640
for phase,frame in zip(model['phases'],[87+141*i for i in range(len(model['phases']))]):
 s.frame_set(frame+1);root=bpy.data.objects['SolarMatrixRoot'];action=root.animation_data.action;pose=root.rotation_euler.copy();root.animation_data_clear();root.rotation_euler=pose;name='highlight-'+phase['component'];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['SolarMatrixRoot'].select_set(True)
 for o in s.objects:
  if o.name.endswith(' technical wire'):
   o.select_set(True);parent=o.parent
   while parent is not None:parent.select_set(True);parent=parent.parent
 temporary=[]
 for ob in s.objects:
  if not ob.name.endswith(' technical wire'):continue
  nt=ob.data.materials[0].node_tree;em=nt.nodes.get('Emission');output=nt.nodes.get('Material Output');rgb=nt.nodes.new('ShaderNodeRGB');rgb.outputs[0].default_value=em.inputs['Color'].default_value;nt.links.new(rgb.outputs[0],output.inputs['Surface']);temporary.append((nt,em,output,rgb))
 frozen=[]
 for hinge_name in model['articulation']['hinges']:
  hinge=bpy.data.objects[hinge_name];saved_action=hinge.animation_data.action;pose=hinge.rotation_euler.copy();hinge.animation_data.action=None;hinge.rotation_euler=pose;frozen.append((hinge,saved_action))
 bpy.ops.export_scene.gltf(filepath=str(out/('solar-matrix-'+name+'.glb')),use_selection=True,export_apply=True,export_animations=False,export_format='GLB')
 for hinge,saved_action in frozen:hinge.animation_data.action=saved_action
 for nt,em,output,rgb in temporary:nt.links.new(em.outputs[0],output.inputs['Surface']);nt.nodes.remove(rgb)
 root.animation_data_create();root.animation_data.action=action

print('ENGINE_HIGHLIGHTS_READY')
