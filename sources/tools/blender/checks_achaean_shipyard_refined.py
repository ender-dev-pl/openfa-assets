"""AC11 revised profiles, constructed frame, equipment and visible source fields."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import points,bounds,material_contract


def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/161' and list(root['footprint'])==[3,3]
    for name in ['AC11 rear chamber 0','AC11 rear chamber 1','AC11 front chamber 0','AC11 front chamber 1','AC11 spine pedestal','AC11 fixture ground shoe']+[f'AC11 blue base housing {i}' for i in range(3)]:assert abs(bounds(name)[2])<1e-5
    ps=[];faces=[];owners=[];trees={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        vs=points(o.name);fs=[tuple(f.vertices) for f in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(vs,fs);offset=len(ps);ps.extend(vs)
        for f in fs:faces.append(tuple(offset+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(ps,faces)
    def ray(p,d,name):
        hit=tree.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);return hit
    overlap=[]
    for i,x in enumerate([-.60,.60]):
        front=bounds('AC11 front chamber '+str(i));rear=bounds('AC11 rear chamber '+str(i));assert 1.38<front[5]<1.40 and 2.02<rear[5]<2.04
        ray((x,-.60,3),(0,0,-1),'AC11 front red optic '+str(i));ray((x,.20,3),(0,0,-1),'AC11 rear red optic '+str(i))
        assert trees['AC11 front chamber '+str(i)].overlap(trees['AC11 rear chamber '+str(i)]);overlap.append(front[4]-rear[1])
    for i,dx in enumerate([-.17,.17]):ray((-.60+dx,-2,.23),(0,1,0),'AC11 lower slot dark floor '+str(i))
    spine=bounds('AC11 blue structural spine');coupling=bounds('AC11 stepped ochre spine coupling');pedestal=bounds('AC11 spine pedestal');assert 2.79<spine[5]<2.81 and spine[2]<coupling[5] and coupling[2]<pedestal[5]
    step_depths=[ray((0,-2,z),(0,1,0),'AC11 stepped ochre spine coupling')[3] for z in [1.00,1.14,1.28]];assert max(step_depths)-min(step_depths)>.012
    ray((.12,-2,2.05),(0,1,0),'AC11 spine side blue field')
    for i,(x,y,h) in enumerate([(-.12,-1.08,.33),(.055,-1.12,.23),(.20,-1.08,.15)]):ray((x,-2,h*.68),(0,1,0),'AC11 blue base field '+str(i))
    arch=points('AC11 broad constructed ochre arch');distance=max(trees['AC11 front chamber 1'].find_nearest(p)[3] for p in arch);assert distance<.07
    ab=bounds('AC11 broad constructed ochre arch');assert ab[0]<.36 and ab[3]>.84 and .93<ab[5]<.96
    fixture=bounds('AC11 constructed coral service fixture');shoe=bounds('AC11 fixture ground shoe');assert fixture[2]<shoe[5] and fixture[5]>.84 and fixture[3]-fixture[0]>.14
    assert trees['AC11 constructed coral service fixture'].overlap(trees['AC11 front chamber 1'])
    return dict(grounded_chamber_lobes=4,articulated_front_neck_height=bounds('AC11 front chamber 0')[5],seated_front_and_rear_red_optics=4,actual_left_slot_ray_paths=2,stepped_spine_coupling_visible=True,actual_spine_coupling_step_ray_paths=3,measured_coupling_step_depth_range=max(step_depths)-min(step_depths),spine_side_blue_field_visible=True,grounded_blue_equipment_housings=3,actual_blue_base_ray_paths=3,maximum_arch_surface_distance=distance,broad_arch_width=ab[3]-ab[0],grounded_constructed_service_fixture=True,minimum_front_rear_overlap=min(overlap),coral_roughness_range=material_contract(),operational_timing_established=False,hidden_rear_interpretation=True)
