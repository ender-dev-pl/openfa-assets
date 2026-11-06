"""Export packed native paint references for independent GLB comparisons."""
import bpy,sys,json
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'command-cruiser.blend'));inputs=out/'packed-paint-inputs';inputs.mkdir(exist_ok=True);model=json.loads((out/'model.json').read_text());bindings={}
for name in model['new_presentation_meshes']:
 ob=bpy.data.objects[name];mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');entry={}
 for slot in ['Base Color','Roughness']:
  socket=bs.inputs[slot]
  if socket.links:
   tex=socket.links[0].from_node;assert tex.type=='TEX_IMAGE';im=tex.image;assert im.packed_file;file=Path(im.name).name;(inputs/file).write_bytes(im.packed_file.data);entry[slot]=dict(image=file)
  else:entry[slot]=dict(value=list(socket.default_value) if slot=='Base Color' else socket.default_value)
 if 'image' in entry['Base Color']:assert len(ob.data.uv_layers)>0
 bindings[name]=entry
(out/'paint-input-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n',encoding='utf-8');print('COMMAND_PAINT_INPUTS_EXTRACTED',len(bindings))
