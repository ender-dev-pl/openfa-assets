"""AC22 actual cluster contact graph, fitting support and source-field rays."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from checks_achaean_shipyard import bounds,points,material_contract

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/172' and list(root['footprint'])==[3,3]
    trees={};vs=[];faces=[];owners=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        ps=points(o.name);fs=[tuple(f.vertices) for f in o.data.polygons];trees[o.name]=BVHTree.FromPolygons(ps,fs);off=len(vs);vs.extend(ps)
        for f in fs:faces.append(tuple(off+i for i in f));owners.append(o.name)
    tree=BVHTree.FromPolygons(vs,faces);lower='AC22 tall grounded lower chamber';upper='AC22 compact upper shoulder chamber';pods=['AC22 grounded small chamber '+str(i) for i in range(5)];graph={n:set() for n in [lower,upper,*pods]};contacts=0
    for i,a in enumerate(graph):
        for b in list(graph)[i+1:]:
            if trees[a].overlap(trees[b]):graph[a].add(b);graph[b].add(a);contacts+=1
    seen=set();queue=[lower]
    while queue:
        n=queue.pop()
        if n in seen:continue
        seen.add(n);queue.extend(graph[n]-seen)
    assert len(seen)==7 and upper in graph[lower]
    for n in [lower,*pods]:assert abs(bounds(n)[2])<1e-5
    for i,pod in [(0,pods[1]),(1,pods[2])]:
        rod='AC22 slate vertical fitting '+str(i);collar='AC22 ochre middle coupling '+str(i);assert trees[rod].overlap(trees[pod]) and trees[rod].overlap(trees[lower]) and trees[rod].overlap(trees[collar])
    connector='AC22 supported right slate connector';assert trees[connector].overlap(trees[pods[2]]) and trees[connector].overlap(trees[pods[4]])
    for a,b in [(upper,'AC22 narrow coral neck'),('AC22 narrow coral neck','AC22 small coral top cap'),('AC22 small coral top cap','AC22 tall ochre sleeve'),('AC22 tall ochre sleeve','AC22 thin slate upper tip')]:assert trees[a].overlap(trees[b]),(a,b)
    assert 4.95<bounds('AC22 thin slate upper tip')[5]<4.97
    distance=0
    for i,z in enumerate([1.18,1.61,2.04]):
        name='AC22 lower cast relief '+str(i);hit=tree.ray_cast(Vector((-.27,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==name
        distance=max(distance,max(trees[lower].find_nearest(p)[3] for p in points(name)))
    assert distance<.065
    names=[f'AC22 upper amber segment {i}' for i in range(4)]+[f'AC22 upper red middle band {i}' for i in range(2)]+['AC22 amber slit '+n for n in ['main','front left','front right','outer right']]+['AC22 red slit back '+n for n in ['main','front left','front right','outer right']];depths=[]
    for name in names:
        o=bpy.data.objects[name];normal=o.matrix_world.to_3x3()@Vector((0,-1,0));centre=o.matrix_world.translation.copy()
        if name.startswith('AC22 red slit back'):centre+=o.matrix_world.to_3x3()@Vector((.055,0,0))
        hit=tree.ray_cast(centre+normal,-normal,2);assert hit[0] is not None and owners[hit[2]]==name,(name,owners[hit[2]] if hit[0] else None);assert .98<hit[3]<1.001;depths.append(hit[3])
    return dict(grounded_main_and_small_chambers=6,connected_chamber_graph_nodes=7,chamber_surface_contact_pairs=contacts,attached_supported_vertical_fittings=2,supported_ochre_couplings=2,right_connector_attached_at_both_ends=True,supported_neck_cap_sleeve_tip=True,actual_cast_relief_visibility_rays=3,maximum_relief_surface_distance=distance,actual_source_field_visibility_rays=len(names),minimum_field_depth=min(depths),maximum_field_depth=max(depths),coral_roughness_range=material_contract(),operating_cycle_established=False,hidden_depth_interpretation=True)
