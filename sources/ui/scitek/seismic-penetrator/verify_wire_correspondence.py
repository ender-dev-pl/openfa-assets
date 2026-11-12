"""Every diagram centreline must be an edge of the evaluated shared solid."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector,kdtree
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(out/'seismic-penetrator.blend'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
model=json.loads((out/'model.json').read_text());deps=bpy.context.evaluated_depsgraph_get();checks={}
for component,names in model['components'].items():
    edges=[]
    for name in names:
        ob=bpy.data.objects[name].evaluated_get(deps);mesh=ob.to_mesh();vs=[ob.matrix_world@v.co for v in mesh.vertices]
        edges.extend((vs[e.vertices[0]],vs[e.vertices[1]]) for e in mesh.edges);ob.to_mesh_clear()
    assert edges
    tree=kdtree.KDTree(len(edges))
    for i,(a,b) in enumerate(edges):tree.insert((a+b)*.5,i)
    tree.balance();wire=bpy.data.objects[component+' technical wire'];maximum=0
    for spline in wire.data.splines:
        assert len(spline.points)==2
        a,b=[wire.matrix_world@Vector(p.co[:3]) for p in spline.points]
        matches=[]
        for _,index,_ in tree.find_range((a+b)*.5,2e-5):
            c,d=edges[index];matches.append(min(max((a-c).length,(b-d).length),max((a-d).length,(b-c).length)))
        error=min(matches,default=1)
        assert error<2e-5,(component,'diagram segment is not an evaluated solid edge',list(a),list(b),error)
        maximum=max(maximum,error)
    checks[component]=dict(solid_edges=len(edges),diagram_segments=len(wire.data.splines),maximum_endpoint_error=maximum)
(out/'wire-correspondence-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'seismic-penetrator.blend').read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),all_diagram_segments_are_evaluated_solid_edges=True,components=checks,contract='Technical lines are a subset of actual evaluated solid edges, including modifiers. Cameras, hue and line thickness differ; component geometry is shared.'),indent=2)+'\n')
print('REPAIR_WIRE_SOLID_CORRESPONDENCE_VERIFIED',sum(x['diagram_segments'] for x in checks.values()))
