"""Exercise topology diagnostic distinctions on controlled meshes, not game assets."""
import sys
from pathlib import Path
import bmesh
from mathutils import Matrix

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_catalogue_topology import metrics,flags,TOLERANCE


def main():
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=2)
    cube=metrics(bm)
    assert cube['boundary_edges']==0 and cube['components'][0]['closed']
    assert abs(cube['components'][0]['signed_volume']-8)<1e-6
    assert not flags({'cube':dict(welded=cube)})
    bm.transform(Matrix.Rotation(.71,4,'X'))
    assert abs(metrics(bm)['components'][0]['signed_volume']-8)<1e-5
    bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    assert 'nonpositive_closed_component' in flags({'cube':dict(welded=metrics(bm))})['cube']
    bm.free()
    # Triangles with separate corner vertices mimic export seam splits.
    source=bmesh.new();bmesh.ops.create_cube(source,size=2)
    split=bmesh.new()
    for face in source.faces:
        split.faces.new([split.verts.new(v.co) for v in face.verts])
    assert metrics(split)['boundary_edges']>0
    bmesh.ops.remove_doubles(split,verts=list(split.verts),dist=TOLERANCE)
    joined=metrics(split)
    assert joined['boundary_edges']==0 and abs(joined['components'][0]['signed_volume']-8)<1e-6
    source.free();split.free()
    plane=bmesh.new();a=plane.verts.new((0,0,0));b=plane.verts.new((1,0,0));c=plane.verts.new((0,1,0));plane.faces.new([a,b,c])
    assert metrics(plane)['boundary_edges']==3
    assert not metrics(plane)['components'][0]['closed']
    plane.edges.new([plane.verts.new((2,0,0)),plane.verts.new((3,0,0))])
    assert metrics(plane)['loose_edges']==1
    assert 'boundary_edges' in flags({'plane':dict(welded=metrics(plane))})['plane']
    plane.free()
    print('CATALOGUE_TOPOLOGY_METRICS_TEST_OK',flush=True)


if __name__=='__main__': main()
