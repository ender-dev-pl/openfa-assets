"""AC04 unequal grounded vessels, physically recessed filters and seated lights."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def points(name):
    o=bpy.data.objects[name];return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(name):
    ps=points(name);return [min(p[a] for p in ps) for a in range(3)]+[max(p[a] for p in ps) for a in range(3)]
def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/154' and list(root['footprint'])==[2,2]
    for name in ['AC04 central vessel','AC04 short left vessel','AC04 right neck']:assert abs(bounds(name)[2])<1e-5
    heights=[bounds(n)[5] for n in ['AC04 main finial','AC04 right finial','AC04 short finial']];assert heights[0]>heights[1]+.4 and heights[1]>heights[2]+.8
    assert bounds('AC04 short left vessel')[3]<bounds('AC04 central vessel')[0]+.15
    verts=[];faces=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        offset=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in o.data.polygons)
    surface=BVHTree.FromPolygons(verts,faces);depths=[]
    for x in [-.16,.16]:
        for z in [.40,.56,.74,.90]:
            hit=surface.ray_cast(Vector((x,-.9,z)),Vector((0,1,0)),2);assert hit[0] is not None and .50<hit[3]<.65,('Filter pocket obstructed',x,z,hit);depths.append(hit[3])
    lower=[]
    for z in [.195,.285]:
        hit=surface.ray_cast(Vector((.13,-.9,z)),Vector((0,1,0)),2);assert hit[0] is not None and .50<hit[3]<.65;lower.append(hit[3])
    for i in range(2):
        for j in range(3):assert 'AC04 filter louvre '+str(i)+' '+str(j) in bpy.data.objects
    for name in ['AC04 low left connection','AC04 low right connection','AC04 hood feed','AC04 steel connector hood','AC04 red port horizontal insert','AC04 red port vertical insert']:assert name in bpy.data.objects
    lens=bounds('AC04 left amber lamp');pod=bounds('AC04 short left vessel');assert pod[0]<lens[0]<lens[3]<pod[3]
    assert bounds('AC04 right amber lamp 0')[3]<bounds('AC04 right amber lamp 1')[0]
    # Actual bounds must span the physical gap between the separated lower vats.
    left=bounds('AC04 low left connection');right=bounds('AC04 low right connection');assert left[0]<-.65 and left[3]>-.57;assert right[0]<.55 and right[3]>.80
    casting=bpy.data.objects['AC04 consolidated coral fittings'].data;casting.calc_loop_triangles();minimum_area=min(t.area for t in casting.loop_triangles);assert minimum_area>1e-10,('Degenerate casting sliver',minimum_area)
    mat=bpy.data.materials['Coral alloy'];image=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
    assert list(image.size)==[256,256]
    def green_red(x,y):
        i=(y*256+x)*4;return image.pixels[i+1]/max(image.pixels[i],1e-6)
    patina_gain=green_red(69,25)-green_red(102,25);assert patina_gain>.10,('Authored wet-joint patina missing from loaded material',patina_gain)
    return dict(three_grounded_unequal_vessels=True,main_finial_height=heights[0],right_finial_height=heights[1],short_finial_height=heights[2],two_filter_fields=True,six_actual_filter_louvres=True,clear_filter_ray_paths=8,minimum_filter_ray_depth=min(depths),maximum_filter_ray_depth=max(depths),clear_lower_grille_ray_paths=2,minimum_lower_grille_ray_depth=min(lower),connected_lower_vessels=True,three_amber_pod_lamps=True,four_spoke_red_port_interpretation=True,minimum_casting_triangle_area=minimum_area,wet_joint_patina_green_red_gain=patina_gain,operational_timing_established=False)
