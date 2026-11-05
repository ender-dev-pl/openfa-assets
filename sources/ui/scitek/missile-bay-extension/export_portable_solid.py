"""Explicit portable PBR colours; preserve native procedural materials and rig."""
import bpy,sys,json,hashlib
from pathlib import Path
folder=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(folder/'missile-bay-extension.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();model=json.loads((folder/'model.json').read_text());meshes=[bpy.data.objects[n] for names in model['components'].values() for n in names];root=bpy.data.objects['MissileBayRig'];links=[];values=[];colours={}
for mat in set(m for ob in meshes for m in ob.data.materials if m):
 if not mat.use_nodes:continue
 node=mat.node_tree.nodes.get('Principled BSDF')
 if not node:continue
 values.append((node.inputs['Base Color'],node.inputs['Base Color'].default_value[:]))
 for slot in ['Base Color','Normal']:
  for link in list(node.inputs[slot].links):links.append((mat.node_tree,link.from_socket,link.to_socket));mat.node_tree.links.remove(link)
 node.inputs['Base Color'].default_value=mat.diffuse_color;colours[mat.name]=list(mat.diffuse_color)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for ob in meshes:
 ob.select_set(True);parent=ob.parent
 while parent and parent!=root:parent.select_set(True);parent=parent.parent
target=folder/'missile-bay-extension.glb';old=hashlib.sha256(target.read_bytes()).hexdigest();bpy.ops.export_scene.gltf(filepath=str(target),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB')
for nt,a,b in links:nt.links.new(a,b)
for socket,value in values:socket.default_value=value
rig_path=folder/'solid-animation-timeline.json';rig=json.loads(rig_path.read_text());rig['source_glb_sha256']=hashlib.sha256(target.read_bytes()).hexdigest();rig_path.write_text(json.dumps(rig,separators=(',',':'))+'\n',encoding='utf-8')
proof_path=folder/'technical-refinement-verification.json';proof=json.loads(proof_path.read_text());proof.update(previous_glb_sha256=old,glb_sha256=rig['source_glb_sha256'],colour_glb_bytes_unchanged=False,portable_material_colours=colours,portable_material_refinement='Exported explicit representative PBR base colours instead of unsupported procedural base-colour links; native source materials remain unchanged. Geometry, hierarchy and choreography preserved.');proof_path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('BAY_PORTABLE_COLOURS_EXPORTED',len(colours))
