"""AC17 ground contacts, field visibility and surface-seated plate checks."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import bounds,points,material_contract

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/167' and list(root['footprint'])==[2,2]
    body=bounds('AC17 main rounded casing');tip=bounds('AC17 short stepped ochre tip')
    assert abs(body[2])<1e-5 and body[5]>2.77 and tip[2]<body[5] and 3.23<tip[5]<3.25
    vs=[];fs=[];owners=[];trees={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        ps=points(o.name);faces=[tuple(f.vertices) for f in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(ps,faces);off=len(vs);vs.extend(ps)
        for f in faces:fs.append(tuple(off+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(vs,fs)
    fields=['AC17 pale blue circular instrument','AC17 paired lower dark slot 0','AC17 paired lower dark slot 1','AC17 upper dark aperture','AC17 red axial inset']+[f'AC17 side blue inset {i} {j}' for i in range(2) for j in range(2)]
    depths=[]
    for name in fields:
        obj=bpy.data.objects[name];normal=obj.matrix_world.to_3x3()@Vector((0,-1,0));hit=tree.ray_cast(obj.matrix_world.translation+normal,-normal,2)
        assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);assert .98<hit[3]<1;depths.append(hit[3])
    distance=0
    for name,x,z in [('AC17 broad circular coral field',.24,1.57),('AC17 left stepped slate plate',-.52,1.35)]:
        hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None)
        distance=max(distance,max(trees['AC17 main rounded casing'].find_nearest(p)[3] for p in points(name)))
    assert distance<.065
    for i in range(2):
        foot='AC17 grounded coral side foot '+str(i);cap='AC17 slate side cap '+str(i)
        assert abs(bounds(foot)[2])<1e-5 and trees[foot].overlap(trees['AC17 main rounded casing'])
        assert trees[foot].overlap(trees[cap])
    axial='AC17 ochre ground axial fitting';shoe='AC17 grounded axial shoe';front='AC17 tall slate front fitting'
    assert abs(bounds(axial)[2])<1e-5 and abs(bounds(shoe)[2])<1e-5
    assert trees[axial].overlap(trees['AC17 main rounded casing']) and trees[axial].overlap(trees[shoe]) and trees[axial].overlap(trees[front])
    assert trees[front].overlap(trees['AC17 main rounded casing'])
    hit=tree.ray_cast(Vector((0,-2,.85)),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==front
    return dict(grounded_main_casing=True,tip_supported=True,grounded_attached_side_feet=2,supported_side_caps=2,grounded_axial_fitting_and_shoe=True,slate_front_fitting_supported_by_body_and_axial_fitting=True,actual_visible_field_rays=len(fields),field_depth_range=[min(depths),max(depths)],actual_surface_relief_visibility_rays=2,maximum_relief_surface_distance=distance,coral_roughness_range=material_contract(),operating_motion_established=False,hidden_rear_interpretation=True)
