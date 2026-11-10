"""AC05 rooted tiering, conformal ornaments, actual recessed panels and service feed."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def points(name):
    o=bpy.data.objects[name];return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(name):
    ps=points(name);return [min(p[a] for p in ps) for a in range(3)]+[max(p[a] for p in ps) for a in range(3)]
def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/155' and list(root['footprint'])==[2,2]
    obj=bpy.data.objects['AC05 tiered main casing'];body=BVHTree.FromPolygons(points(obj.name),[tuple(p.vertices) for p in obj.data.polygons]);assert abs(bounds(obj.name)[2])<1e-5
    ring=body.ray_cast(Vector((-2,0,1.54)),Vector((1,0,0)),4)[0];waist=body.ray_cast(Vector((-2,0,.99)),Vector((1,0,0)),4)[0];ratio=ring.x/waist.x;assert 1.35<ratio<1.60
    assert 2.92<bounds('AC05 small brass finial')[5]<2.94
    names=['AC05 upper right brass','AC05 upper left brass','AC05 upper lower-left brass','AC05 curved upper casting','AC05 middle brass sweep','AC05 middle right brass','AC05 middle raised casting'];distance=max(body.find_nearest(p)[3] for name in names for p in points(name));assert distance<.05
    ridge=bounds('AC05 curved upper casting');assert ridge[3]-ridge[0]>.30
    # Measure angular width from actual vertices at a middle section; a thin
    # decorative line does not reproduce the broad casting visible in legacy.
    ps=[p for p in points('AC05 curved upper casting') if abs(p.z-2.255)<.001]
    if not ps:
        target=min(abs(p.z-2.255) for p in points('AC05 curved upper casting'));ps=[p for p in points('AC05 curved upper casting') if abs(abs(p.z-2.255)-target)<1e-5]
    import math
    angular_width=max(math.atan2(p.y,p.x) for p in ps)-min(math.atan2(p.y,p.x) for p in ps);assert angular_width>.24
    verts=[];faces=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        offset=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
    surface=BVHTree.FromPolygons(verts,faces);depths=[]
    for x in [-.20,.20]:
        for z in [.20,.295,.405,.50]:
            hit=surface.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2);assert hit[0] is not None and .50<hit[3]<.65,('Base grille is blocked',x,z,hit);depths.append(hit[3])
    waistdepths=[]
    for x in [-.12,.12]:
        hit=surface.ray_cast(Vector((x,-.8,.99)),Vector((0,1,0)),2);assert hit[0] is not None and .45<hit[3]<.60;waistdepths.append(hit[3])
    for i in range(2):
        for j in range(3):assert 'AC05 base louvre '+str(i)+' '+str(j) in bpy.data.objects
    module=bounds('AC05 side service module');pipe=bounds('AC05 brass service pipe');assert abs(module[2])<1e-5 and pipe[2]<module[5]-.05
    assert bounds('AC05 red vertical indicator')[5]-bounds('AC05 red vertical indicator')[2]>.32
    assert 'AC05 amber indicator' in bpy.data.objects
    return dict(ring_to_waist_radius_ratio=ratio,one_grounded_tiered_main_body=True,maximum_facing_or_casting_surface_distance=distance,curved_upper_casting=True,upper_casting_measured_angular_width=angular_width,two_base_grille_fields=True,six_actual_louvres=True,clear_base_grille_paths=8,minimum_base_grille_ray_depth=min(depths),two_recessed_waist_panels=True,minimum_waist_panel_depth=min(waistdepths),grounded_side_service_module=True,pipe_seated_into_module=True,separate_red_and_amber_indicators=True,operational_timing_established=False)
