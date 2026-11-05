"""Repair a cut-face crack introduced by displaced Boolean bridge vertices on TI048."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,bmesh
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
source=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined/TI048/TI048.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();prior=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));wheel=next(o for o in bpy.context.scene.objects if o.name.endswith('whole cheese wheel with removed wedge'));wheel.data=wheel.data.copy();bm=bmesh.new();bm.from_mesh(wheel.data)
before=dict(vertices=len(bm.verts),faces=len(bm.faces),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.010);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4],ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after=dict(vertices=len(bm.verts),faces=len(bm.faces),nonmanifold_edges=sum(not e.is_manifold for e in bm.edges));bm.to_mesh(wheel.data);bm.free()
a.out.mkdir(parents=True,exist_ok=True);native=a.out/'TI048.blend';bpy.context.scene.render.filepath='//renders/';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
for m in bpy.data.materials:
 bs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
 if not bs:continue
 for key in ['Base Color','Roughness','Normal']:
  for link in list(bs.inputs[key].links):m.node_tree.links.remove(link)
bpy.ops.export_scene.gltf(filepath=str(a.out/'TI048.glb'),export_format='GLB',export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
record=json.loads((source.parent/'refinement.json').read_text());record.update(refined_native_sha256=sha(native),glb_sha256=sha(a.out/'TI048.glb'),geometry_builder='sources/tools/trading-goods/refining/repair_cheese.py',geometry_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=prior,topology_repair=dict(before=before,after=after,method='Weld displaced near-coincident Boolean bridge vertices, triangulate holed n-gons and recalculate normals'));(a.out/'refinement.json').write_text(json.dumps(record,indent=2)+'\n');assert sha(source)==prior;print('CHEESE_CUT_FACE_REPAIRED',before,after,flush=True)
