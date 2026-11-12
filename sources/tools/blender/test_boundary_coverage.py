"""Controlled containment and boundary-network tests; no game asset writes."""
import sys
from pathlib import Path
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from classify_catalogue_boundaries import containment,sample_boundaries


def main():
    bm=bmesh.new();bmesh.ops.create_cube(bm,size=2);bm.normal_update();tree=BVHTree.FromBMesh(bm)
    assert containment(tree,Vector((.1,.2,.3)))=='inside'
    assert containment(tree,Vector((2,0,0)))=='outside'
    assert containment(tree,Vector((1,0,0)))=='surface_ambiguous'
    # Two nested closed surfaces require two crossings from the cavity;
    # an envelope-only test would incorrectly report containment.
    inner=set(bmesh.ops.create_cube(bm,size=1)['verts'])
    bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if all(v in inner for v in f.verts)])
    bm.normal_update();hollow=BVHTree.FromBMesh(bm)
    assert containment(hollow,Vector((0,0,0)))=='outside'
    assert containment(hollow,Vector((.75,.1,.1)))=='inside'
    bm.free()
    bm=bmesh.new();a=bm.verts.new((0,0,0));b=bm.verts.new((1,0,0));c=bm.verts.new((0,1,0));bm.faces.new([a,b,c])
    groups=sample_boundaries(bm)
    assert len(groups)==1 and groups[0]['closed_wire_loop'] and len(groups[0]['points'])==6
    d=bm.verts.new((-1,0,0));e=bm.verts.new((0,-1,0));bm.faces.new([a,d,e])
    groups=sample_boundaries(bm)
    assert len(groups)==1 and not groups[0]['closed_wire_loop'],'Touching loops must remain a branched boundary network'
    bm.free()
    print('BOUNDARY_COVERAGE_TEST_OK',flush=True)


if __name__=='__main__': main()
