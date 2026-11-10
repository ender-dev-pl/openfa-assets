"""AC19 body/facing/conduit contacts and source-field visibility in both representations."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import bounds,points,material_contract

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/169' and list(root['footprint'])==[2,2]
    trees={};vs=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        ps=points(o.name);fs=[tuple(p.vertices) for p in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(ps,fs);off=len(vs);vs.extend(ps)
        for f in fs:faces.append(tuple(off+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(vs,faces);body='AC19 enclosed main casing';shoe='AC19 grounded front shoe';conduit='AC19 supported front conduit';collar='AC19 red conduit instrument'
    assert abs(bounds(body)[2])<1e-5 and 3.77<bounds('AC19 short slate upper tip')[5]<3.79 and bounds('AC19 short slate upper tip')[2]<bounds(body)[5]
    for name in ['AC19 grounded ochre left facing','AC19 grounded long coral right facing',shoe]:assert abs(bounds(name)[2])<1e-5 and trees[name].overlap(trees[body])
    assert trees[shoe].overlap(trees[conduit]) and trees[conduit].overlap(trees[body]) and trees[collar].overlap(trees[conduit])
    names=[f'AC19 pale conduit field {i}' for i in range(5)]+[f'AC19 small left pale field {i}' for i in range(2)]+['AC19 upper red recessed port','AC19 red instrument lens','AC19 amber lower slit','AC19 lower red inset']
    depths=[]
    for name in names:
        o=bpy.data.objects[name];normal=o.matrix_world.to_3x3()@Vector((0,-1,0));centre=o.matrix_world.translation.copy()
        if name=='AC19 lower red inset':centre+=o.matrix_world.to_3x3()@Vector((.065,0,0))
        hit=tree.ray_cast(centre+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);assert .98<hit[3]<1.001;depths.append(hit[3])
    visible=0
    for x,z,name in [(-.63,1.2,'AC19 grounded ochre left facing'),(.49,1.2,'AC19 grounded long coral right facing')]:
        hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);visible+=1
    return dict(grounded_main_casing=True,grounded_attached_side_facings_and_shoe=3,conduit_supported_by_body_and_shoe=True,red_instrument_supported_by_conduit=True,upper_tip_supported=True,actual_source_field_visibility_rays=len(names),actual_side_facing_visibility_rays=visible,minimum_field_depth=min(depths),maximum_field_depth=max(depths),coral_roughness_range=material_contract(),operating_cycle_established=False,shield_surface_effect_established=False,hidden_rear_interpretation=True)
