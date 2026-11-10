"""AC08 hall, physically supported striped towers and three blue entrance pavilions."""
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
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/158' and list(root['footprint'])==[3,3]
    hall=bounds('AC08 central hall');crown=bounds('AC08 central crown');assert abs(hall[2])<1e-5 and crown[2]<hall[5] and 4.8<crown[5]<4.9
    assert components('AC08 consolidated hall panes')==16 and components('AC08 consolidated blue portal panes')==12
    assert components('AC08 consolidated tower bands')==28
    support=[]
    for i,x in enumerate([-1.15,1.15]):
        podname='AC08 entrance pavilion '+str(2*i);pod=bpy.data.objects[podname];tree=BVHTree.FromPolygons(points(podname),[tuple(f.vertices) for f in pod.data.polygons]);shaft=bounds('AC08 tower shaft '+str(i));head=bounds('AC08 tower upper chamber '+str(i));hit=tree.ray_cast(Vector((x,.10,2)),Vector((0,0,-1)),3);assert hit[0] is not None and shaft[2]<hit[0].z-.05;assert head[2]<shaft[5] and 4.65<head[5]<4.75;support.append(hit[0].z-shaft[2])
    for i in range(3):assert abs(bounds('AC08 entrance pavilion '+str(i))[2])<1e-5
    finial=bounds('AC08 centre portal short finial');assert finial[2]<bounds('AC08 entrance pavilion 1')[5] and 1.7<finial[5]<1.8
    verts=[];faces=[];owners=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        for face in obj.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(obj.name)
    surface=BVHTree.FromPolygons(verts,faces)
    def ray(p,d,name):
        hit=surface.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,('Covered field',name,owners[hit[2]] if hit[0] is not None else None);return hit[3]
    depths=[]
    for z in [1.70,2.60]:
        for a in [-math.pi/2-.42,-math.pi/2+.42]:
            n=Vector((math.cos(a),math.sin(a),0));t=Vector((-math.sin(a),math.cos(a),0))
            for x,dz in [(0,.16),(-.05,0),(.05,0),(0,-.16)]:depths.append(ray(n*2+t*x+Vector((0,0,z+dz)),-n,'AC08 consolidated hall panes'))
    assert all(1.20<d<1.25 for d in depths)
    for i,(cx,cy) in enumerate([(-1.15,-.10),(0,-.96),(1.15,-.10)]):
        for x,z in [(-.12,.18),(.12,.18),(-.12,.43),(.12,.43)]:ray((cx+x,cy-2,z),(0,1,0),'AC08 consolidated blue portal panes')
        ray((cx,cy-2,.64),(0,1,0),'AC08 portal amber lens '+str(i))
    for i,x in enumerate([-1.15,1.15]):
        for dx,dz in [(0,.12),(-.023,.035),(.023,.035),(-.023,-.035),(.023,-.035),(0,-.12)]:ray((x+dx,-2,3.99+dz),(0,1,0),'AC08 tower pane '+str(i)+' '+str([(0,.12),(-.023,.035),(.023,.035),(-.023,-.035),(.023,-.035),(0,-.12)].index((dx,dz))))
    normal=Vector((0,-1,.6)).normalized();tangent=Vector((0,.6,1)).normalized();centre=Vector((0,-.665,3.30));ray(centre+normal,-normal,'AC08 upper red inset')
    hall_obj=bpy.data.objects['AC08 central hall'];hall_tree=BVHTree.FromPolygons(points(hall_obj.name),[tuple(f.vertices) for f in hall_obj.data.polygons]);corners=0
    for x in [-.10,.10]:
        for h in [-.27,.27]:
            rear=centre+Vector((x,0,0))+tangent*h-normal*.10;hit=hall_tree.ray_cast(rear+normal*.40,-normal,1);assert hit[0] is not None and hit[3]<.40;corners+=1

    obj=bpy.data.objects['AC08 central hall'];tree=BVHTree.FromPolygons(points(obj.name),[tuple(f.vertices) for f in obj.data.polygons]);distance=max(tree.find_nearest(p)[3] for name in ['AC08 long right flowing casting','AC08 left flowing casting'] for p in points(name));assert distance<.05
    return dict(grounded_pavilions=3,supported_long_towers=2,minimum_tower_root_overlap=min(support),seated_crown=True,striped_shaft_bands=28,main_window_ray_paths=16,blue_portal_ray_paths=12,tower_window_ray_paths=12,portal_status_ray_paths=3,upper_red_inset_ray_paths=1,seated_tilted_red_frame_corners=corners,centre_short_finial_supported=True,maximum_flowing_casting_surface_distance=distance,operational_timing_established=False,hidden_rear_interpretation=True)
