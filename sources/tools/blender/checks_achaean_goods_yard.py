"""AC24 actual casing/shoulder support, closed grooves, ribs and upper-port visibility."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import bounds,points,material_contract

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/174' and list(root['footprint'])==[2,2]
    trees={};ps=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        vs=points(o.name);fs=[tuple(f.vertices) for f in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(vs,fs);off=len(ps);ps.extend(vs)
        for f in fs:faces.append(tuple(off+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(ps,faces);contacts=0;depths=[];rays=0
    for i,(x,y) in enumerate([(-.46,.23),(.46,.23),(0,-.57)]):
        lower='AC24 grounded ochre casing '+str(i);upper='AC24 joined coral shoulder '+str(i);tip='AC24 short blue violet tip '+str(i)
        assert abs(bounds(lower)[2])<1e-5 and trees[lower].overlap(trees[upper]) and trees[upper].overlap(trees[tip])
        assert bpy.data.objects[lower].data.materials[0].name=='Ochre protected lower casings' and bpy.data.objects[upper].data.materials[0].name=='Coral alloy' and bpy.data.objects[tip].data.materials[0].name=='Blue violet source tips'
        for j in range(i+1,3):
            if trees[upper].overlap(trees['AC24 joined coral shoulder '+str(j)]):contacts+=1
        pane=bpy.data.objects['AC24 dark vertical casing recess '+str(i)];normal=pane.matrix_world.to_3x3()@Vector((0,-1,0))
        for z in [.40,.62,.84]:
            centre=pane.matrix_world.translation+pane.matrix_world.to_3x3()@Vector((0,0,z-.51));hit=tree.ray_cast(centre+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==pane.name;assert .98<hit[3]<1;depths.append(hit[3]);rays+=1
        for j,z in enumerate([.30,.51,.72]):
            rib=f'AC24 solid recess cross rib {i} {j}';assert trees[rib].overlap(trees[lower]);hit=tree.ray_cast(Vector((x,-3,z)),Vector((0,1,0)),5);assert hit[0] is not None and owners[hit[2]]==rib;rays+=1
        name='AC24 dark upper port '+str(i);o=bpy.data.objects[name];normal=o.matrix_world.to_3x3()@Vector((0,-1,0));hit=tree.ray_cast(o.matrix_world.translation+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);depths.append(hit[3]);rays+=1
    assert contacts==3
    return dict(grounded_ochre_casings=3,supported_coral_shoulders=3,actual_shoulder_contact_pairs=contacts,supported_blue_violet_tips=3,material_boundary_matches_source=True,actual_closed_recess_visibility_sections=9,attached_solid_cross_ribs=9,actual_recess_rib_port_rays=rays,minimum_recess_depth=min(depths),maximum_recess_depth=max(depths),coral_roughness_range=material_contract(),open_cargo_bays_established=False,operating_or_fill_states_established=False,hidden_depth_interpretation=True)
