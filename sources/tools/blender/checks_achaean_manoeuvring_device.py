"""AC16 actual grounded pod contacts, projected fittings and source field rays."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import material_contract,points,bounds


def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/166' and list(root['footprint'])==[2,2]
    base=bounds('AC16 broad ground chamber');waist=bounds('AC16 connected narrow waist');upper=bounds('AC16 upper tear-drop chamber');tip=bounds('AC16 short slate tip')
    assert abs(base[2])<1e-5 and waist[2]<base[5] and waist[5]>upper[2] and tip[2]<upper[5] and 2.95<tip[5]<2.97
    ps=[];faces=[];owners=[];trees={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        vs=points(o.name);fs=[tuple(f.vertices) for f in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(vs,fs);offset=len(ps);ps.extend(vs)
        for f in fs:faces.append(tuple(offset+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(ps,faces)
    def ray(p,name):
        hit=tree.ray_cast(Vector(p),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);return hit
    field_depths=[]
    for name in ['AC16 upper red source field','AC16 pale blue source slot','AC16 lower red source field 0','AC16 lower red source field 1']:
        obj=bpy.data.objects[name];normal=obj.matrix_world.to_3x3()@Vector((0,-1,0));hit=tree.ray_cast(obj.matrix_world.translation+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);assert .98<hit[3]<1;field_depths.append(hit[3])
    contacts=0
    for i in range(4):
        name='AC16 grounded slate pod '+str(i);b=bounds(name);stem=bounds('AC16 red pod stem '+str(i));assert abs(b[2])<1e-5 and stem[2]<b[5];assert trees[name].overlap(trees['AC16 broad ground chamber']);contacts+=1
    distance=0
    for i,(x,z) in enumerate([(.08,2.30),(-.30,2.02),(.30,1.72)]):
        name='AC16 upper ochre fitting '+str(i);ray((x,-2,z),name);distance=max(distance,max(trees['AC16 upper tear-drop chamber'].find_nearest(p)[3] for p in points(name)))
    name='AC16 lower ochre fitting';ray((.60,-2,.40),name);distance=max(distance,max(trees['AC16 broad ground chamber'].find_nearest(p)[3] for p in points(name)));assert distance<.065
    return dict(grounded_main_body=True,connected_waist_upper_and_tip=True,grounded_attached_slate_pods=contacts,supported_red_pod_stems=4,actual_upper_ochre_fittings=3,actual_lower_ochre_fittings=1,ochre_fitting_ray_paths=4,maximum_ochre_surface_distance=distance,actual_red_field_ray_paths=3,actual_pale_blue_slot_ray_paths=1,minimum_source_field_ray_depth=min(field_depths),maximum_source_field_ray_depth=max(field_depths),source_fields_follow_casing_normals=True,coral_roughness_range=material_contract(),operational_timing_established=False,hidden_rear_interpretation=True)
