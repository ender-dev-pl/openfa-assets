"""AC18 actual open-span rays, tier contacts and source instrument visibility."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import bounds,points,material_contract

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/168' and list(root['footprint'])==[2,2]
    trees={};vs=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        ps=points(o.name);fs=[tuple(p.vertices) for p in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(ps,fs);off=len(vs);vs.extend(ps)
        for f in fs:faces.append(tuple(off+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(vs,faces)
    contacts=0
    for i in range(3):
        lower='AC18 tier 0 chamber '+str(i);mid='AC18 tier 1 chamber '+str(i);rod='AC18 lower exposed conduit '+str(i)
        assert abs(bounds(lower)[2])<1e-5 and trees[lower].overlap(trees[rod]) and trees[mid].overlap(trees[rod]);contacts+=2
    for i in range(2):
        rod='AC18 upper exposed conduit '+str(i);assert trees[rod].overlap(trees['AC18 tier 1 chamber '+str(i)]) and trees[rod].overlap(trees['AC18 upper onion chamber']);contacts+=2
    coupling='AC18 ribbed ochre middle coupling';instrument='AC18 front slate instrument';top='AC18 upper onion chamber'
    assert trees[coupling].overlap(trees['AC18 tier 1 chamber 2']) and trees[coupling].overlap(trees[instrument]) and trees[instrument].overlap(trees[top])
    assert bounds('AC18 short ochre tip')[2]<bounds(top)[5] and 5.57<bounds('AC18 short ochre tip')[5]<5.59
    for z in [3.10,3.23,3.33]:
        hit=tree.ray_cast(Vector((0,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==coupling
    openings=0
    for z in [1.2,1.7,2.1,3.5]:
        for x in [-.20,.20]:assert tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0] is None;openings+=1
    names=[f'AC18 lower blue field {i} {j}' for i in range(3) for j in range(3)]+[f'AC18 upper blue field {i} {j}' for i in range(2) for j in range(2)]+['AC18 top red field','AC18 neck dark aperture','AC18 lower amber slit','AC18 instrument amber slit','AC18 lower red field','AC18 instrument red field']
    depths=[]
    for name in names:
        o=bpy.data.objects[name];normal=o.matrix_world.to_3x3()@Vector((0,-1,0));centre=o.matrix_world.translation.copy()
        if name=='AC18 lower red field':centre+=o.matrix_world.to_3x3()@Vector((.08,0,0))
        if name=='AC18 instrument red field':centre+=o.matrix_world.to_3x3()@Vector((.065,0,0))
        hit=tree.ray_cast(centre+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);assert .98<hit[3]<1.001;depths.append(hit[3])
    allpoints=[p for o in trees for p in points(o)];width=max(p.x for p in allpoints)-min(p.x for p in allpoints);assert 3.7<5.58/width<4.2
    return dict(grounded_coral_chambers=3,actual_tier_rod_contacts=contacts,supported_coupling_instrument_top=True,supported_tip=True,actual_open_span_rays=openings,actual_source_field_visibility_rays=len(names),minimum_field_depth=min(depths),maximum_field_depth=max(depths),height_width_ratio=5.58/width,coral_roughness_range=material_contract(),operating_motion_established=False,hidden_depth_interpretation=True)

