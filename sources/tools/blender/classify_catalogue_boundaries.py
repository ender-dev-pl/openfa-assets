"""Conservative sampled boundary containment; never edits saved model geometry."""
import hashlib
import json
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REPO=Path(__file__).resolve().parents[2]
TOPOLOGY=REPO/'docs/assets/reconstruction/evidence/catalogue-topology'
OUTPUT=REPO/'docs/assets/reconstruction/evidence/boundary-coverage'
EPSILON=1e-5
DIRECTIONS=[Vector(v).normalized() for v in [(0.173,0.291,0.941),(-0.431,0.852,0.297),(0.647,-0.385,0.658)]]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def containment(tree,point):
    nearest=tree.find_nearest(point)
    if nearest[0] is None: return 'unknown'
    if nearest[3]<=EPSILON: return 'surface_ambiguous'
    votes=[]
    for direction in DIRECTIONS:
        origin=point.copy();crossings=0
        for _ in range(128):
            hit=tree.ray_cast(origin,direction)
            if hit[0] is None: break
            crossings+=1;origin=hit[0]+direction*EPSILON
        else: return 'unknown'
        votes.append(crossings%2==1)
    return 'inside' if all(votes) else 'outside' if not any(votes) else 'ray_disagreement'


def sample_boundaries(bm):
    bm.verts.index_update();bm.edges.index_update()
    edges=[e for e in bm.edges if e.is_boundary]
    pending={v for e in edges for v in e.verts};groups=[]
    while pending:
        start=min(pending,key=lambda v:v.index);pending.remove(start);group={start};stack=[start]
        while stack:
            for edge in stack.pop().link_edges:
                if not edge.is_boundary: continue
                for vertex in edge.verts:
                    if vertex in pending: pending.remove(vertex);group.add(vertex);stack.append(vertex)
        vertices=sorted(group,key=lambda v:v.index)
        selected=sorted((e for e in edges if e.verts[0] in group),key=lambda e:e.index)
        points=[]
        for items,midpoint in [(vertices,False),(selected,True)]:
            for index in sorted({i*len(items)//min(12,len(items)) for i in range(min(12,len(items)))}):
                item=items[index];points.append((sum((v.co for v in item.verts),Vector())/2 if midpoint else item.co.copy()))
        groups.append(dict(boundary_vertices=len(vertices),boundary_edges=len(selected),
            closed_wire_loop=all(sum(e.is_boundary for e in v.link_edges)==2 for v in vertices),points=points))
    return groups


def prepare(report):
    graph=bpy.context.evaluated_depsgraph_get();closed={};boundaries={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or obj.get('preview_only'): continue
        evidence=report['native'][obj.name];evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
        bm=bmesh.new();bm.from_mesh(mesh);bm.transform(evaluated.matrix_world)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
        boundary_count=sum(e.is_boundary for e in bm.edges)
        assert boundary_count==evidence['welded']['boundary_edges'],('Boundary count changed',obj.name)
        if boundary_count: boundaries[obj.name]=sample_boundaries(bm)
        elif obj.name not in report['native_flags'] and all(c['closed'] for c in evidence['welded']['components']):
            points=[v.co for v in bm.verts]
            closed[obj.name]=dict(tree=BVHTree.FromBMesh(bm),
                low=[min(p[a] for p in points) for a in range(3)],high=[max(p[a] for p in points) for a in range(3)])
        bm.free();evaluated.to_mesh_clear()
    return closed,boundaries


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    summary_path=TOPOLOGY/'summary.json';summary=json.loads(summary_path.read_text());rows=[]
    for row in summary['records']:
        topology_path=TOPOLOGY/row['report'];report=json.loads(topology_path.read_text())
        assert sha(topology_path)==row['sha256']
        if not any('boundary_edges' in issues for issues in report['native_flags'].values()): continue
        source=REPO/report['blend'];assert sha(source)==report['blend_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
        closed,boundaries=prepare(report);objects={}
        for name,groups in boundaries.items():
            results=[]
            for group in groups:
                samples=[]
                for point in group['points']:
                    covers=[];ambiguous=[]
                    for other,solid in closed.items():
                        if not all(solid['low'][a]-EPSILON<=point[a]<=solid['high'][a]+EPSILON for a in range(3)): continue
                        state=containment(solid['tree'],point)
                        if state=='inside': covers.append(other)
                        elif state!='outside': ambiguous.append(dict(object=other,state=state))
                    samples.append(dict(point=list(point),inside_closed_objects=covers,ambiguous=ambiguous))
                covered=sum(bool(s['inside_closed_objects']) for s in samples)
                status='all_samples_inside_closed_geometry' if covered==len(samples) else 'some_samples_inside_closed_geometry' if covered else 'coverage_not_established'
                results.append(dict(boundary_vertices=group['boundary_vertices'],boundary_edges=group['boundary_edges'],
                    closed_wire_loop=group['closed_wire_loop'],sampled_points=len(samples),covered_samples=covered,status=status,samples=samples))
            objects[name]=results
        assert sha(source)==report['blend_sha256']
        output=OUTPUT/row['report'];output.write_text(json.dumps(dict(issue=1109,id=report['id'],blend=report['blend'],
            blend_sha256=report['blend_sha256'],topology_report_sha256=sha(topology_path),closed_cover_candidates=sorted(closed),
            objects=objects,source_assets_unchanged=True,final_visual_acceptance=False),indent=2)+'\n')
        rows.append(dict(id=report['id'],report=output.name,sha256=sha(output),boundary_meshes=len(objects)))
        print('BOUNDARY_COVERAGE_INSPECTED',report['id'],len(objects),flush=True)
    assert sum(r['boundary_meshes'] for r in rows)==347
    result=dict(issue=1109,blender=bpy.app.version_string,auditor_sha256=sha(Path(__file__)),
        topology_summary_sha256=sha(summary_path),models=len(rows),boundary_meshes=347,records=rows,
        surface_epsilon=EPSILON,maximum_vertices_and_midpoints_per_boundary_group=24,ray_directions=[list(v) for v in DIRECTIONS],
        scope='Native first-pose finite boundary samples inside other unflagged closed shells, requiring agreement of three parity rays. No proof of complete edge/loop coverage or final assembly/art acceptance.',final_visual_acceptance=False)
    (OUTPUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print('BOUNDARY_COVERAGE_AUDIT_OK',len(rows),347,flush=True)


if __name__=='__main__': main()
