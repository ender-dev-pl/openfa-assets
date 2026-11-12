"""Read-only component-scoped distance audit, retaining all unmatched evidence."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
root=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.parent.mkdir(parents=True,exist_ok=True)
integration=json.loads((root/'gallery/media/ui/scitek/integration.json').read_text());records=[]
for rec in integration['records']:
 if rec.get('model_relationship',{}).get('kind')!='upgrade-device-presentation':continue
 source=root/rec['blend'];metadata=json.loads((source.parent/'model.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();roles={};issues=[]
 for role,names in metadata['components'].items():
  vertices=[];polygons=[];objects=[];raw_edges=[]
  for name in names:
   ob=bpy.data.objects.get(name)
   if not ob or ob.type not in ['MESH','CURVE']:issues.append(dict(role=role,missing_physical=name));continue
   if ob.type=='MESH':raw_edges.extend(tuple(ob.matrix_world@ob.data.vertices[i].co for i in edge.vertices) for edge in ob.data.edges)
   else:
    for sp in ob.data.splines:
     if sp.type!='POLY':continue
     pts=[ob.matrix_world@Vector(p.co[:3]) for p in sp.points];raw_edges.extend(zip(pts,pts[1:]))
     if sp.use_cyclic_u:raw_edges.append((pts[-1],pts[0]))
   ev=ob.evaluated_get(deps);mesh=ev.to_mesh();offset=len(vertices);vertices.extend(ob.matrix_world@v.co for v in mesh.vertices);polygons.extend(tuple(offset+i for i in p.vertices) for p in mesh.polygons);objects.append(name);ev.to_mesh_clear()
  if not polygons:issues.append(dict(role=role,no_physical_faces=True));continue
  tree=BVHTree.FromPolygons(vertices,polygons,all_triangles=False);minimum=Vector(tuple(min(v[i] for v in vertices) for i in range(3)));maximum=Vector(tuple(max(v[i] for v in vertices) for i in range(3)));extent=(maximum-minimum).length
  wire=bpy.data.objects.get(role+' technical wire')
  if wire is None:issues.append(dict(role=role,missing_group_wire=True));continue
  edge_tree=kdtree.KDTree(len(raw_edges))
  for i,(a,b) in enumerate(raw_edges):edge_tree.insert((a+b)*.5,i)
  edge_tree.balance();distances=[];segments=0;worst=None;raw_matches=0;unmatched=[]
  for spline in wire.data.splines:
   if spline.type!='POLY':issues.append(dict(role=role,non_poly_spline=spline.type));continue
   points=[wire.matrix_world@Vector(p.co[:3]) for p in spline.points]
   pairs=list(zip(points,points[1:]));pairs+= [(points[-1],points[0])] if spline.use_cyclic_u else []
   for a,b in pairs:
    segments+=1;matches=[]
    for _,index,_ in edge_tree.find_range((a+b)*.5,2e-5):
     c,d=raw_edges[index];matches.append(min(max((a-c).length,(b-d).length),max((a-d).length,(b-c).length)))
    if matches and min(matches)<2e-5:raw_matches+=1
    elif len(unmatched)<8:unmatched.append([list(a),list(b)])
    for t in [0,.25,.5,.75,1]:
     p=a.lerp(b,t);nearest=tree.find_nearest(p);distance=nearest[3] if nearest else float('inf');distances.append(distance)
     if worst is None or distance>worst['distance']:worst=dict(distance=distance,position=list(p),segment=[list(a),list(b)])
  distances.sort();roles[role]=dict(physical_objects=objects,wire_object=wire.name,wire_segments=segments,exact_raw_skeleton_segments=raw_matches,raw_skeleton_match_fraction=raw_matches/segments if segments else None,unmatched_segment_examples=unmatched,samples=len(distances),physical_bbox_diagonal=extent,maximum_surface_distance=distances[-1] if distances else None,median_surface_distance=distances[len(distances)//2] if distances else None,p99_surface_distance=distances[min(len(distances)-1,int(len(distances)*.99))] if distances else None,relative_maximum=distances[-1]/extent if distances and extent else None,worst_sample=worst)
 timeline_path=source.parent/'information-timeline.json';timeline=json.loads(timeline_path.read_text()) if timeline_path.exists() else {};digest=hashlib.sha256(source.read_bytes()).hexdigest()
 records.append(dict(id=rec['id'],source=rec['blend'],source_sha256=digest,information_declared_source_sha256=timeline.get('source_sha256'),information_source_hash_matches_current_master=timeline.get('source_sha256')==digest,roles=roles,issues=issues))
 print('UPGRADE_GEOMETRY_OBSERVED',rec['id'],len(roles),len(issues),flush=True)
out.write_text(json.dumps(dict(method='Read-only source-master audit. Per-component raw physical-edge/curve-control-point matching at2e-5 endpoint tolerance, plus evaluated physical surface BVH with five samples along every diagram segment at source frame1. Distances are observations, not automatic visual acceptance. Missing groups and outliers remain explicit.',limitations=['This checks hidden technical curves in each source master. Separate exported static/information GLBs require their own source-bound import checks.','Centreline diagrams of thin rods naturally lie inside their physical surfaces.','Raw pre-bevel skeleton edges can differ from evaluated surfaces by the authored bevel width.','Surface proximity alone does not prove semantic ownership or recovered legacy geometry.','No threshold is used to declare the entire task complete.'],records=records),indent=2)+'\n',encoding='utf-8')
print('UPGRADE_DIAGRAM_AUDIT_SAVED',len(records))
