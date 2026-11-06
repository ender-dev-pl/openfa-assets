"""Verify nine new closed parts and retain packed paint references for GLB checks."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();reports={};paint={};inputs=out/'packed-paint-inputs';inputs.mkdir(exist_ok=True)
for imported in [False,True]:
 if imported:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'warp-generator.glb'))
 else:bpy.ops.wm.open_mainfile(filepath=str(out/'warp-generator.blend'))
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update();errors=[];nodes=[]
 for i in range(4):
  a=i*math.pi/2
  nodes.append((f'Monitored energy duct {i+1}',(.32*math.cos(a),.225,.32*math.sin(a)),(.10,.25,.10)))
  nodes.append((f'Energy flow monitoring circuit {i+1}',(.23*math.cos(a),-.91,.23*math.sin(a)),(.065,.10,.065)))
 nodes.append(('Energy flow monitoring central circuit',(0,-.985,0),(.11,.12,.11)))
 for name,centre,scale in nodes:
  ob=bpy.data.objects[name];points=[ob.matrix_world@v.co for v in ob.data.vertices]
  for p in points:errors.append(abs(sum(((p[i]-centre[i])/scale[i])**2 for i in range(3))-1))
  assert max(errors)<2e-5,(name,max(errors))
  if not imported:
   mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF');bindings={}
   for slot in ['Base Color','Roughness']:
    tex=bs.inputs[slot].links[0].from_node;assert tex.type=='TEX_IMAGE';im=tex.image;assert im.packed_file
    file=Path(im.name).name;(inputs/file).write_bytes(im.packed_file.data);bindings[slot]=file
   assert 'Authored box wear' in ob.data.uv_layers;paint[name]=bindings
 reports['imported' if imported else 'native']=dict(new_parts=len(nodes),ellipsoid_surface_equation_max_error=max(errors),duct_ring_radius=.32,monitor_ring_radius=.23,monitor_count=5,duct_count=4,minimum_duct_clearance=math.sqrt(2)*.32-.20,minimum_peripheral_monitor_clearance=math.sqrt(2)*.23-.13,central_monitor_radial_clearance=.23-.11-.065)
proof=dict(source_sha256=hashlib.sha256((out/'warp-generator.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'warp-generator.glb').read_bytes()).hexdigest(),checks=reports,new_part_paint_bindings=paint,limitations=['Circuit seating is internal and intentionally intersects support shell; hidden dimensions are authored, not recovered.'])
(out/'anatomy-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('WARP_ANATOMY_VERIFIED')
