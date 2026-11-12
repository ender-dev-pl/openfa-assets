"""AC15 actual supported receiver/elbow, narrow silhouette and recessed fields."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import material_contract,points,bounds


def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/165' and list(root['footprint'])==[2,2]
    base=bounds('AC15 main ground chamber');foot=bounds('AC15 right ground foot');assert abs(base[2])<1e-5 and abs(foot[2])<1e-5 and base[3]>foot[0]
    lower=bounds('AC15 lower slate support');receiver=bounds('AC15 stepped coral receiver');needle=bounds('AC15 muted red needle');side=bounds('AC15 ribbed ochre side column');elbow=bounds('AC15 supported coral return elbow')
    assert lower[2]<base[5] and lower[5]>receiver[2] and needle[2]<receiver[5] and 6.59<needle[5]<6.61
    assert side[2]<foot[5] and side[5]>elbow[2] and elbow[0]<receiver[3] and elbow[5]>receiver[2]
    width=max(base[3],foot[3])-min(base[0],foot[0]);ratio=needle[5]/width;assert 3.4<ratio<3.6
    assert .78<receiver[3]-receiver[0]<.82 and .1<needle[3]-needle[0]<.13
    ps=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        offset=len(ps);ps.extend(points(o.name))
        for f in o.data.polygons:faces.append(tuple(offset+i for i in f.vertices));owners.append(o.name)
    tree=BVHTree.FromPolygons(ps,faces)
    def ray(p,d,name):
        hit=tree.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);return hit
    depths=[]
    for i,z in enumerate([.65,.95]):depths.append(ray((-.15,-2,z),(0,1,0),'AC15 amber source pane '+str(i))[3])
    assert all(1.64<d<1.67 for d in depths)
    ray((.75,-2,.22),(0,1,0),'AC15 forward dark red field')
    for i,z in enumerate([1.60,1.94,2.28]):ray((-.15,-2,z+.07),(0,1,0),'AC15 lower slate collar '+str(i))
    for i,z in enumerate([3.45,3.80]):ray((-.15,-2,z+.08),(0,1,0),'AC15 upper slate band '+str(i))
    tier_depths=[]
    for z,lo,hi in [(4.25,1.69,1.71),(4.65,1.77,1.79),(5.00,1.86,1.88)]:
        d=ray((-.15,-2,z),(0,1,0),'AC15 stepped coral receiver')[3];assert lo<d<hi;tier_depths.append(d)
    return dict(actual_receiver_tier_ray_paths=3,minimum_receiver_tier_ray_depth=min(tier_depths),maximum_receiver_tier_ray_depth=max(tier_depths),grounded_connected_chambers=2,supported_receiver_and_needle=True,supported_parallel_side_column_and_elbow=True,narrow_height_width_ratio=ratio,receiver_width=receiver[3]-receiver[0],actual_stacked_amber_fields=2,unobstructed_amber_ray_paths=2,minimum_amber_ray_depth=min(depths),maximum_amber_ray_depth=max(depths),actual_forward_round_field=1,lower_slate_collar_rays=3,upper_slate_band_rays=2,coral_roughness_range=material_contract(),operational_timing_established=False,hidden_rear_interpretation=True)
