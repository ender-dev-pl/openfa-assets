"""AC10 asymmetric receiver pods, 18 actual coloured cells and two roof bores."""
import math
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def points(name):
    o=bpy.data.objects[name];return [o.matrix_world@v.co for v in o.data.vertices]
def bounds(name):
    ps=points(name);return [min(p[a] for p in ps) for a in range(3)]+[max(p[a] for p in ps) for a in range(3)]
def components(name):
    bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);remaining=set(bm.verts);count=0
    while remaining:
        stack=[remaining.pop()];count+=1
        while stack:
            v=stack.pop()
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in remaining:remaining.remove(other);stack.append(other)
    bm.free();return count

def structure():
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/160' and list(root['footprint'])==[3,3]
    tower=bounds('AC10 central information tower');hood=bounds('AC10 tiered slate hood');assert hood[2]<tower[5] and 4.60<hood[5]<4.70
    for name in ['AC10 central information tower','AC10 left receiver chamber','AC10 right aperture chamber','AC10 foreground terminal']:assert abs(bounds(name)[2])<1e-5
    assert components('AC10 eighteen display cells')==18
    verts=[];faces=[];owners=[];materials=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        for face in obj.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(obj.name);materials.append(obj.data.materials[face.material_index].name)
    surface=BVHTree.FromPolygons(verts,faces)
    def ray(p,d,name):
        hit=surface.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,('Covered field',name,owners[hit[2]] if hit[0] is not None else None);return hit
    for i in range(18):
        hit=ray((0,-2,.60+i*.10),(0,1,0),'AC10 eighteen display cells');assert materials[hit[2]]==['Deep blue strip','Violet strip','Cold blue strip'][i%3];assert 1.11<hit[3]<1.14
    ray((0,-2,.23),(0,1,0),'AC10 red terminal glass')
    t=bpy.data.objects['AC10 central information tower'];tt=BVHTree.FromPolygons(points(t.name),[tuple(f.vertices) for f in t.data.polygons]);corner_checks=0
    for x in [-.10,.10]:
        for z in [.44,2.46]:
            hit=tt.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None and hit[0].y<-.68;corner_checks+=1
    terminal=bpy.data.objects['AC10 foreground terminal'];tree=BVHTree.FromPolygons(points(terminal.name),[tuple(f.vertices) for f in terminal.data.polygons]);hit=tree.ray_cast(Vector((0,-.84,1)),Vector((0,0,-1)),2);assert hit[0] is not None and hit[0].z>.45
    left=bpy.data.objects['AC10 left receiver chamber'];lt=BVHTree.FromPolygons(points(left.name),[tuple(f.vertices) for f in left.data.polygons]);post=bounds('AC10 left short post');hit=lt.ray_cast(Vector((-1.20,.07,2)),Vector((0,0,-1)),3);assert hit[0] is not None and post[2]<hit[0].z-.03
    cyan_depths=[]
    for i,a in enumerate([-math.pi/2-.35,-math.pi/2+.35]):
        n=Vector((math.cos(a),math.sin(a),0));q=n.to_track_quat('Z','Y');p=Vector((-1.05+.80*math.cos(a),-.03+.80*math.sin(a),.23))
        for u,v in [(0,0),(-.025,-.025),(.025,-.025),(-.025,.025),(.025,.025)]:cyan_depths.append(ray(p+n+q@Vector((u,v,0)),-n,'AC10 cyan glass '+str(i))[3])
    assert all(.99<d<1.01 for d in cyan_depths)
    ports=[]
    for i,(dx,dy) in enumerate([(-.23,-.28),(.24,-.40)]):
        r=math.hypot(dx,dy)
        if i==0:z=1.05+(.44-r)/(.44-.21)*.15;slope=(.44-.21)/.15
        else:z=.80+(.60-r)/(.60-.44)*.25;slope=(.60-.44)/.25
        n=Vector((dx/r,dy/r,slope)).normalized();p=Vector((1.05+dx,-.03+dy,z));hit=ray(p+n*.5,-n,'AC10 roof aperture dark floor '+str(i));assert .55<hit[3]<.58;ports.append(hit[3])
    distance=max(lt.find_nearest(p)[3] for i in range(3) for p in points('AC10 left rosette casting '+str(i)));assert distance<.05
    return dict(grounded_core_and_lower_chambers=4,seated_tiered_hood=True,display_cells=18,actual_palette_order_ray_paths=18,seated_display_case_corners=corner_checks,display_terminal_connected=True,supported_left_short_post=True,actual_cyan_glazing_ray_paths=10,actual_dark_roof_bores=2,minimum_roof_bore_ray_depth=min(ports),maximum_roof_bore_ray_depth=max(ports),maximum_rosette_surface_distance=distance,operational_timing_established=False,hidden_rear_interpretation=True)
