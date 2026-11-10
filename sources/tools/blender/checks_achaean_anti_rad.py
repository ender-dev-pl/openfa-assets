"""AC02-specific rooted anatomy and unobstructed exposed-conductor checks."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def points(name):
    o=bpy.data.objects[name];return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(name):
    ps=points(name);return [min(p[a] for p in ps) for a in range(3)]+[max(p[a] for p in ps) for a in range(3)]
def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/152' and list(root['footprint'])==[2,2]
    roof=bounds('AC02 main arch dome');assert roof[3]-roof[0]>1.75 and .97<roof[2]<.99 and 1.78<roof[5]<1.80
    antenna=bounds('AC02 antenna');assert 2.57<antenna[5]<2.59 and antenna[3]-antenna[0]<.25
    bars=[bounds('AC02 exposed conductor '+str(i)) for i in range(6)]
    for b in bars:assert abs(b[5]-1.04)<1e-5 and .02<b[2]<.21
    gaps=[bars[i+1][0]-bars[i][3] for i in range(5)];assert min(gaps)>.045
    assert all(abs(bounds('AC02 side pod '+str(s))[2])<1e-5 for s in [-1,1])
    assert all(bounds('AC02 gold pod cap '+str(s))[5]>1.29 for s in [-1,1])
    assert 'Conformal uneven brass roof facing' in bpy.data.objects
    obj=bpy.data.objects['AC02 main arch dome'];surface=BVHTree.FromPolygons(points(obj.name),[tuple(p.vertices) for p in obj.data.polygons]);patch_distance=max(surface.find_nearest(p)[3] for p in points('Conformal uneven brass roof facing'));assert patch_distance<.03
    # The combined geometry, not a component name/manifest, must leave each
    # lower inter-bar interval open. This rejects a substituted solid front wall.
    verts=[];faces=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    tree=BVHTree.FromPolygons(verts,faces)
    for i in range(5):
        x=(bars[i][3]+bars[i+1][0])/2
        hit=tree.ray_cast(Vector((x,-2,.30)),Vector((0,1,0)),4)
        assert hit[0] is None,('Blocked conductor interval',i)
    return dict(rooted_two_grounded_pods=True,six_supported_independent_conductors=True,open_interbar_ray_paths=5,minimum_interbar_gap=min(gaps),maximum_conductor_top_error=max(abs(b[5]-1.04) for b in bars),conformal_closed_brass_facing=True,maximum_brass_facing_surface_distance=patch_distance,stepped_antenna=True,operational_timing_established=False)
