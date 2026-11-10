"""Actual AC14 silhouette/support, front fields and open well checks."""
import math,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import material_contract,points,bounds
PORTS=[(-.18,.80),(.18,.80),(-.31,.55),(0,.55),(.31,.55),(-.18,.30),(.18,.30)]


def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/164' and list(root['footprint'])==[3,3]
    names=['AC14 left rear mast chamber','AC14 left foreground chamber','AC14 open rear launch chamber','AC14 right foreground field chamber']
    b=[bounds(n) for n in names];assert all(abs(v[2])<1e-5 for v in b)
    assert b[0][1]<b[1][4] and b[2][1]<b[3][4] and b[0][3]>b[2][0] and b[1][3]>b[3][0]
    lower=bounds('AC14 ochre lower mast');collar=bounds('AC14 slate mast collar');upper=bounds('AC14 ochre upper mast');assert lower[2]<b[0][5] and lower[5]>collar[2] and upper[2]<collar[5] and 4.54<upper[5]<4.56
    assert upper[3]-upper[0]<.16 and collar[3]-collar[0]>.45
    casting=bounds('AC14 connected interstitial casting');ped=bounds('AC14 short slate pedestal');bulb=bounds('AC14 short slate bulb');post=bounds('AC14 short slate post');assert ped[2]<casting[5] and ped[5]>bulb[2] and post[2]<bulb[5]
    ps=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        offset=len(ps);ps.extend(points(o.name))
        for f in o.data.polygons:faces.append(tuple(offset+i for i in f.vertices));owners.append(o.name)
    tree=BVHTree.FromPolygons(ps,faces)
    def ray(p,d,name):
        hit=tree.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);return hit
    for i,(dx,z) in enumerate(PORTS):ray((.65+dx,-2,z),(0,1,0),'AC14 dark field floor '+str(i))
    ray((-.65,-2,.20),(0,1,0),'AC14 low amber window')
    heights=[ray((.65,.40,3),(0,0,-1),'AC14 recessed launch well floor')[0].z]
    for i in range(16):
        a=i*math.pi/8;heights.append(ray((.65+.26*math.cos(a),.40+.26*math.sin(a),3),(0,0,-1),'AC14 recessed launch well floor')[0].z)
        assert ray((.65+.30*math.cos(a),.40+.30*math.sin(a),3),(0,0,-1),'AC14 open rear launch chamber')[0].z>1.55
    assert all(.05<h<.06 for h in heights)
    return dict(grounded_connected_lobes=4,supported_tall_ochre_mast=True,supported_slate_collar=True,tall_mast_height=upper[5],supported_short_slate_fitting=True,actual_dark_front_recesses=7,actual_amber_field_ray_paths=1,open_well_ray_paths=17,actual_collar_ray_paths=16,actual_mouth_radius_lower_bound=.26,actual_mouth_radius_upper_bound=.30,minimum_well_floor_height=min(heights),maximum_well_floor_height=max(heights),coral_roughness_range=material_contract(),operational_timing_established=False,hidden_rear_interpretation=True)
