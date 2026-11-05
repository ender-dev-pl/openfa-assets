"""Independent imported wing-loop UV correspondence and packed paint references."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import kdtree
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'terminator.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();expected={};bindings={};inputs=out/'packed-paint-inputs';inputs.mkdir(exist_ok=True)
for side in [-1,1]:
 name=f'Terminator swept outer wing {side}';ob=bpy.data.objects[name];tree=kdtree.KDTree(len(ob.data.vertices));uvs={}
 for i,v in enumerate(ob.data.vertices):tree.insert(ob.matrix_world@v.co,i);uvs[i]=[]
 tree.balance();uv=ob.data.uv_layers.active
 for loop,value in zip(ob.data.loops,uv.data):uvs[loop.vertex_index].append(value.uv.copy())
 expected[name]=(tree,uvs);mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');paint={}
 for slot in ['Base Color','Roughness']:
  tex=bs.inputs[slot].links[0].from_node;assert tex.type=='TEX_IMAGE';im=tex.image;assert im.packed_file;file=Path(im.name).name;(inputs/file).write_bytes(im.packed_file.data);paint[slot]=file
 bindings[name]=paint
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(out/'terminator.glb'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();checks={}
for name,(tree,uvs) in expected.items():
 ob=bpy.data.objects[name];uv=ob.data.uv_layers.active;maximum=0
 for loop,value in zip(ob.data.loops,uv.data):
  p=ob.matrix_world@ob.data.vertices[loop.vertex_index].co;candidates=[u for _,index,_ in tree.find_range(p,2e-6) for u in uvs[index]];assert candidates,(name,p);error=min((value.uv-u).length for u in candidates);assert error<2e-6,(name,error);maximum=max(maximum,error)
 checks[name]=dict(imported_loop_count=len(ob.data.loops),maximum_native_import_uv_error=maximum)
(out/'wing-runtime-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'terminator.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'terminator.glb').read_bytes()).hexdigest(),checks=checks,wing_paint_bindings=bindings),indent=2)+'\n',encoding='utf-8');print('TERMINATOR_WING_RUNTIME_UV_VERIFIED')
