"""Check evaluated TI067 handles against its inner lining and cavity profile."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);native=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined/TI067/repaired/TI067.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def evaluated(o):
 e=o.evaluated_get(dg);m=e.to_mesh();vertices=[e.matrix_world@v.co for v in m.vertices];polygons=[tuple(p.vertices) for p in m.polygons];tree=BVHTree.FromPolygons(vertices,polygons);e.to_mesh_clear();return vertices,tree
lining=next(o for o in bpy.context.scene.objects if o.name.endswith('red inner lining'));_,inner_tree=evaluated(lining);rows=[]
for o in bpy.context.scene.objects:
 if 'separate cup loop handle' not in o.name:continue
 vertices,tree=evaluated(o);dist=[]
 for p in vertices:
  if not 1.42<=p.z<=1.94:continue
  radius=.2+(p.z-1.42)*.64/.25 if p.z<1.67 else .84+(p.z-1.67)*.07/.27
  dist.append(math.hypot(p.x,p.y)-radius)
 overlaps=tree.overlap(inner_tree);rows.append(dict(name=o.name,center=list(o.location),tested_vertices=len(dist),vertices_inside_cavity=sum(d<0 for d in dist),minimum_radial_clearance=min(dist),intersections_with_evaluated_lining=len(overlaps)))
assert len(rows)==2 and all(r['vertices_inside_cavity']==0 and r['minimum_radial_clearance']>.02 and r['intersections_with_evaluated_lining']==0 for r in rows),rows
assert sha(native)==before
a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(dict(native=native.relative_to(a.repo).as_posix(),native_sha256=before,verifier_sha256=sha(Path(__file__)),method='Evaluated world-space handle vertices checked against the piecewise radial cavity profile; BVH triangle intersections with evaluated enamel lining checked independently. Profile clearance exceeds coating thickness.',handles=rows),indent=2)+'\n');print('CUP_HANDLES_CLEAR_OF_INTERIOR',flush=True)
