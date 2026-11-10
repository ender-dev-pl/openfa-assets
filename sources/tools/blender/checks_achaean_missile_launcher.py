"""Actual AC13 structural support, seven recesses and permanently open well."""
import math,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import material_contract,points,bounds
PORTS=[(-.16,.70),(.16,.70),(-.28,.48),(0,.48),(.28,.48),(-.16,.24),(.16,.24)]


def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/163' and list(root['footprint'])==[2,2]
    left=bounds('AC13 left twin-post chamber');right=bounds('AC13 seven-field launcher chamber');assert abs(left[2])<1e-5 and abs(right[2])<1e-5 and left[3]>right[0]
    ps=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        offset=len(ps);ps.extend(points(o.name))
        for face in o.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(o.name)
    tree=BVHTree.FromPolygons(ps,faces)
    def ray(p,d,name):
        hit=tree.ray_cast(Vector(p),Vector(d),4);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);return hit
    depths=[]
    for i,(dx,z) in enumerate(PORTS):depths.append(ray((.55+dx,-2,z),(0,1,0),'AC13 dark field floor '+str(i))[3])
    for i,x in enumerate([-.70,-.43]):ray((x,-2,.20),(0,1,0),'AC13 low red optic '+str(i))
    heights=[]
    for dx,dy in [(0,0),(-.12,0),(.12,0),(0,-.12),(0,.12)]:heights.append(ray((.55+dx,-.20+dy,2),(0,0,-1),'AC13 recessed launch well floor')[0].z)
    assert all(.05<h<.06 for h in heights)
    for i in range(16):
        a=i*math.pi/8
        ray((.55+.16*math.cos(a),-.20+.16*math.sin(a),2),(0,0,-1),'AC13 recessed launch well floor')
        hit=ray((.55+.18*math.cos(a),-.20+.18*math.sin(a),2),(0,0,-1),'AC13 seven-field launcher chamber');assert hit[0].z>1.04
    for i,x in enumerate([-.75,-.35]):
        post=bounds('AC13 coral post '+str(i));head=bounds('AC13 slate post head '+str(i));assert post[2]<left[5] and post[5]>head[2] and head[5]>2.68
        ray((x,-2,2.17),(0,1,0),'AC13 slate head dark slot '+str(i))
    return dict(grounded_connected_chambers=2,parallel_supported_posts=2,seated_slate_heads=2,actual_dark_front_recesses=7,unobstructed_dark_recess_rays=len(depths),low_red_source_fields=2,open_well_ray_paths=21,actual_exposed_mouth_radius_lower_bound=.16,actual_exposed_mouth_radius_upper_bound=.18,actual_collar_ray_paths=16,minimum_well_floor_height=min(heights),maximum_well_floor_height=max(heights),retained_exposed_mouth_radius=.17,coral_roughness_range=material_contract(),operational_timing_established=False,hidden_rear_interpretation=True)
