"""AC23 actual four-lobe profiles, column contacts and attached visible brace assemblies."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import points,bounds,material_contract

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/173' and list(root['footprint'])==[2,2]
    trees={};ps=[];fs=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        vs=points(o.name);faces=[tuple(f.vertices) for f in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(vs,faces);off=len(ps);ps.extend(vs)
        for f in faces:fs.append(tuple(off+i for i in f));owners.append(o.name)
    scene=BVHTree.FromPolygons(ps,fs);centres=[(-.48,.22),(.48,.22),(0,-.58)];names=['AC23 four-lobed storage column '+str(i) for i in range(3)];contacts=0;peaks=[];waists=[]
    for i,(cx,cy) in enumerate(centres):
        name=names[i];assert abs(bounds(name)[2])<1e-5;tip='AC23 short red top tip '+str(i);assert trees[name].overlap(trees[tip]) and 2.30<bounds(tip)[5]<2.32
        for z in [.21,.70,1.23,1.76]:
            hit=trees[name].ray_cast(Vector((cx,-3,z)),Vector((0,1,0)),5);assert hit[0] is not None;r=cy-hit[0].y;assert r>.48;peaks.append(r)
        for z in [.50,1.03,1.56]:
            hit=trees[name].ray_cast(Vector((cx,-3,z)),Vector((0,1,0)),5);assert hit[0] is not None;r=cy-hit[0].y;assert r<.40;waists.append(r)
        for other in names[i+1:]:
            if trees[name].overlap(trees[other]):contacts+=1
    assert contacts==3
    rib_contacts=0;visibility=0
    for i,(x,y,body) in enumerate([(0,-1.05,names[2]),(.61,-.26,names[1])]):
        brace='AC23 grounded slate brace '+str(i);b=bounds(brace);assert abs(b[2])<1e-5 and trees[brace].overlap(trees[body])
        for z in [.21,.70,1.23,1.76]:
            hit=trees[body].ray_cast(Vector((x,-3,z)),Vector((0,1,0)),5);assert hit[0] is not None and b[1]<hit[0].y+.04<b[4];rib_contacts+=1
            visible=scene.ray_cast(Vector((x,-3,z)),Vector((0,1,0)),5);assert visible[0] is not None and owners[visible[2]]==brace,(i,z,owners[visible[2]] if visible[0] else None);visibility+=1
        for j in range(3):
            strap=f'AC23 brace strap {i} {j}';assert trees[strap].overlap(trees[brace]) and trees[strap].overlap(trees[body])
            for k in range(2):assert trees[f'AC23 strap fastener {i} {j} {k}'].overlap(trees[strap])
    return dict(grounded_connected_columns=3,actual_column_surface_contact_pairs=contacts,supported_short_red_tips=3,actual_lobe_peak_sections=len(peaks),minimum_lobe_peak_radius=min(peaks),actual_waist_sections=len(waists),maximum_waist_radius=max(waists),grounded_braces=2,actual_brace_rib_contact_sections=rib_contacts,actual_brace_visibility_rays=visibility,attached_brace_straps=6,attached_fasteners=12,coral_roughness_range=material_contract(),exposed_ore_or_fill_stages_established=False,operating_motion_established=False,hidden_depth_interpretation=True)
