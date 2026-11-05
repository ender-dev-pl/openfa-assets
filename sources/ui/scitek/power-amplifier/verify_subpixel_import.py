"""Independent GLB check at the source-visible reflector coverage regression."""
import bpy,sys,json,hashlib
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();manifest=json.loads((out/'information-timeline.json').read_text());entry=manifest['timeline'][266]
assert manifest['cycles_samples']==64 and entry['highlight_component']=='distorted-reflector'
bpy.ops.wm.open_mainfile(filepath=str(out/'power-amplifier-information.blend'));s=bpy.context.scene
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'power-amplifier-information.glb'));s.frame_set(267)
for name in manifest['component_nodes']:
 ob=bpy.data.objects[name+' technical wire'];nt=ob.data.materials[0].node_tree;nt.nodes.clear();emission=nt.nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(.9,.003,.001,1) if name==entry['highlight_component'] else (0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(emission.outputs[0],output.inputs[0])
s.camera.location=entry['camera_position'];s.camera.rotation_euler=entry['camera_euler'];s.camera.data.ortho_scale=entry['ortho_scale'];s.cycles.samples=64;s.render.filepath=str(out/'subpixel-imported-266.png');bpy.ops.render.render(write_still=True)
proof=dict(frame=266,cycles_samples=64,glb_sha256=hashlib.sha256((out/'power-amplifier-information.glb').read_bytes()).hexdigest(),native_png_sha256=hashlib.sha256((out/'frames/266.png').read_bytes()).hexdigest(),imported_png_sha256=hashlib.sha256((out/'subpixel-imported-266.png').read_bytes()).hexdigest())
(out/'subpixel-import-inputs.json').write_text(json.dumps(proof,indent=2)+'\n')
print('AMPLIFIER_SUBPIXEL_IMPORT_RENDERED')
