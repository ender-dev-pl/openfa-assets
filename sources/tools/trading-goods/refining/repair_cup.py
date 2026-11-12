"""Open TI067's intended hollow red-lined bowl by removing an accidental rim cap."""
import argparse,hashlib,json,sys,math
from pathlib import Path
import bpy,bmesh
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined/TI067/TI067.blend';prior=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));lining=next(o for o in bpy.context.scene.objects if o.name.endswith('red inner lining'));lining.data=lining.data.copy();bm=bmesh.new();bm.from_mesh(lining.data);top=max(v.co.z for v in bm.verts);caps=[f for f in bm.faces if len(f.verts)>4 and all(abs(v.co.z-top)<1e-5 for v in f.verts)];assert len(caps)==1;bmesh.ops.delete(bm,geom=caps,context='FACES');bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(lining.data);bm.free();mod=lining.modifiers.new('Thin enamel coating with actual open rim','SOLIDIFY');mod.thickness=.006;mod.offset=0
m=lining.data.materials[0];bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Roughness'].default_value=.25;bs.inputs['Coat Weight'].default_value=.30;bs.inputs['Coat Roughness'].default_value=.18
for n in m.node_tree.nodes:
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.20;n.inputs['To Max'].default_value=.30
 if n.type=='BUMP':n.inputs['Distance'].default_value=.00018;n.inputs['Strength'].default_value=.12
handles=[o for o in bpy.context.scene.objects if 'separate cup loop handle' in o.name];assert len(handles)==2
for handle in handles:handle.location.x=math.copysign(1.22,handle.location.x)
bpy.context.scene.camera.data.ortho_scale*=1.15
bpy.context.scene.render.filepath='//renders/';bpy.context.preferences.filepaths.save_version=0;a.out.mkdir(parents=True,exist_ok=True);native=a.out/'TI067.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
for material in bpy.data.materials:
 bs=material.node_tree.nodes.get('Principled BSDF') if material.use_nodes else None
 if not bs:continue
 for key in ['Base Color','Roughness','Normal']:
  for link in list(bs.inputs[key].links):material.node_tree.links.remove(link)
bpy.ops.export_scene.gltf(filepath=str(a.out/'TI067.glb'),export_format='GLB',export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
r=json.loads((source.parent/'refinement.json').read_text());r.update(refined_native_sha256=sha(native),glb_sha256=sha(a.out/'TI067.glb'),geometry_builder='sources/tools/trading-goods/refining/repair_cup.py',geometry_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=prior,bowl_repair='Remove one unintended red-lining rim cap, orient coating towards the interior and retain thin enamel thickness; restore a reflective enamel surface and move intersecting handles outside the bowl wall. This follows the documented hollow-bowl construction, not a new claim about unseen legacy detail.');
for material in r['materials']:
 if 'red enamel inner bowl' in material['name']:material.update(roughness=.25,micro_relief_distance=.00018,coat_weight=.30)
(a.out/'refinement.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==prior;print('CUP_INTERIOR_OPENED',flush=True)
