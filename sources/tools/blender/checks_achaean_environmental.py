"""AC03 anatomy: flared foot, small bulb, genuine 3x5 intake pocket and paired feeds."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def points(name):
    o=bpy.data.objects[name];return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(name):
    ps=points(name);return [min(p[a] for p in ps) for a in range(3)]+[max(p[a] for p in ps) for a in range(3)]
def tree(name):
    o=bpy.data.objects[name];return BVHTree.FromPolygons(points(name),[tuple(p.vertices) for p in o.data.polygons])
def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/153' and list(root['footprint'])==[2,2]
    casing=bounds('AC03 bell casing');assert abs(casing[2])<1e-5 and 1.65<casing[3]-casing[0]<1.67
    body=tree('AC03 bell casing');p=body.ray_cast(Vector((-2,0,.8)),Vector((1,0,0)),4)[0];assert p is not None;ratio=(casing[3]-casing[0])/(-2*p.x);assert 1.30<ratio<1.50
    bulb=bounds('AC03 top bulb');assert bulb[5]-bulb[2]<.47 and bulb[3]-bulb[0]<.48;assert 2.79<bounds('AC03 finial')[5]<2.81
    for i in range(2):assert 'AC03 vertical grille bar '+str(i) in bpy.data.objects
    for i in range(4):assert 'AC03 horizontal grille bar '+str(i) in bpy.data.objects
    verts=[];faces=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        offset=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
    surface=BVHTree.FromPolygons(verts,faces);depths=[]
    for x in [-.113,0,.113]:
        for z in [.41,.53,.65,.77,.89]:
            hit=surface.ray_cast(Vector((x,-.95,z)),Vector((0,1,0)),2);assert hit[0] is not None;distance=hit[3];assert .50<distance<.70,('Intake cell is blocked or missing rear well',x,z,distance);depths.append(distance)
    for x in [-.20,.20]:
        for z,name in [(.32,'bottom'),(.98,'top')]:
            skin=body.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)[0];assert skin is not None
            rim=bounds('AC03 intake rim '+name);assert rim[1]<skin.y<rim[4],('Rim not seated through casing',x,z)
    for i in range(2):
        pump=bounds('AC03 blue pump '+str(i));pipe=bounds('AC03 copper riser '+str(i));assert abs(pump[2])<1e-5 and pipe[2]<pump[5]-.06
        seat=bounds('AC03 shoulder pipe seat '+str(i));assert pipe[0]<seat[0] and pipe[3]>seat[3]
    maximum=max(body.find_nearest(p)[3] for name in ['AC03 upper brass facing','AC03 lower left inspection facing','AC03 upper left inspection facing'] for p in points(name));assert maximum<.03
    lens=bounds('AC03 red vertical status lens');grille=bounds('AC03 vertical grille bar 0');assert lens[5]-lens[2]>.29
    assert (lens[2]+lens[5])/2>(grille[2]+grille[5])/2+.05 and lens[5]<=grille[5]+1e-5
    return dict(foot_to_casing_width_ratio=ratio,small_top_bulb=True,actual_intake_open_cells=15,four_intake_rim_corner_seats=True,minimum_intake_ray_depth=min(depths),maximum_intake_ray_depth=max(depths),status_lens_beside_upper_grille=True,paired_grounded_pumps=True,paired_seated_copper_risers=True,maximum_brass_facing_surface_distance=maximum,operational_timing_established=False)
