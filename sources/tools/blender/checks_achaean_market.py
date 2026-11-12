"""AC09 real cross windows, circular blue portholes and supported raised rooms."""
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
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/159' and list(root['footprint'])==[3,3]
    hall=bounds('AC09 central market hall');neck=bounds('AC09 coral crown neck');hood=bounds('AC09 slate crown hood');assert abs(hall[2])<1e-5 and neck[2]<hall[5] and hood[2]<neck[5] and 3.25<hood[5]<3.35
    supports=[];links=[]
    hobj=bpy.data.objects['AC09 central market hall'];hall_tree=BVHTree.FromPolygons(points(hobj.name),[tuple(f.vertices) for f in hobj.data.polygons])
    for i,sign in enumerate([-1,1]):
        podname='AC09 fore pavilion '+str(i);pod=bpy.data.objects[podname];tree=BVHTree.FromPolygons(points(podname),[tuple(f.vertices) for f in pod.data.polygons]);shaft=bounds('AC09 side room support '+str(i));roomname='AC09 raised side room '+str(i);room=bpy.data.objects[roomname];rb=bounds(roomname);assert abs(bounds(podname)[2])<1e-5
        hit=tree.ray_cast(Vector((sign,-.03,2)),Vector((0,0,-1)),3);assert hit[0] is not None and shaft[2]<hit[0].z-.05;assert shaft[5]>rb[2]+.05;supports.append(hit[0].z-shaft[2])
        rt=BVHTree.FromPolygons(points(roomname),[tuple(f.vertices) for f in room.data.polygons]);h=hall_tree.ray_cast(Vector((sign*2,-.03,1.30)),Vector((-sign,0,0)),4);r=rt.ray_cast(Vector((0,-.03,1.30)),Vector((sign,0,0)),3);assert h[0] is not None and r[0] is not None
        link=bounds('AC09 side room link '+str(i));start=min(abs(link[0]),abs(link[3]));end=max(abs(link[0]),abs(link[3]));assert start<abs(h[0].x)-.05 and end>abs(r[0].x)+.05;links.append(min(abs(h[0].x)-start,end-abs(r[0].x)))
    verts=[];faces=[];owners=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        for face in obj.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(obj.name)
    surface=BVHTree.FromPolygons(verts,faces)
    def ray(p,d,name):
        hit=surface.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,('Covered field',name,owners[hit[2]] if hit[0] is not None else None);return hit[3]
    warm=[]
    for i,a in enumerate([-math.pi/2-.55,-math.pi/2+.55]):
        n=Vector((math.cos(a),math.sin(a),0));t=Vector((-math.sin(a),math.cos(a),0))
        for x,z in [(0,0),(-.055,0),(.055,0),(0,-.055),(0,.055)]:warm.append(ray(n*2+t*x+Vector((0,0,1.50+z)),-n,'AC09 warm cross '+str(i)))
        for x,z in [(-.075,-.075),(.075,-.075),(-.075,.075),(.075,.075)]:ray(n*2+t*x+Vector((0,0,1.50+z)),-n,'AC09 consolidated corner cells')
    assert all(1.24<d<1.27 for d in warm)
    dark_depth=ray((0,-2,1.50),(0,1,0),'AC09 central opening dark floor');assert 1.42<dark_depth<1.49
    ray((0,-2,.78),(0,1,0),'AC09 lower red status')
    normal=Vector((0,-1,.15)).normalized();q=normal.to_track_quat('Z','Y');glazing=[]
    for i,x in enumerate([-.80,.80]):
        p=Vector((x,-.835,.45))
        for u,v in [(-.045,-.045),(.045,-.045),(-.045,.045),(.045,.045)]:glazing.append(ray(p+normal+q@Vector((u,v,0)),-normal,'AC09 blue porthole glass '+str(i)))
        ray(p+normal,-normal,'AC09 porthole separator '+str(i))
    assert all(1.00<d<1.02 for d in glazing)
    centre=Vector((0,-.55,2.15));up=Vector((0,.85,1)).normalized();boundary=[]
    for p in points('AC09 upper circular coral casting'):
        v=p-centre;x=v.x;y=v.dot(up);r=math.hypot(x,y)
        if r>.20:boundary.append((x,y,r))
    circle_error=max(abs(r-.21) for x,y,r in boundary);assert circle_error<2e-6;assert len({round(math.atan2(y,x),4) for x,y,r in boundary})==48
    distance=max(hall_tree.find_nearest(p)[3] for name in ['AC09 upper circular coral casting','AC09 right flowing casting','AC09 left flowing casting'] for p in points(name));assert distance<.05
    return dict(grounded_main_hall=True,grounded_fore_pavilions=2,supported_raised_rooms=2,minimum_vertical_support_overlap=min(supports),minimum_side_corridor_overlap=min(links),seated_crown_neck_and_hood=True,actual_warm_cross_ray_paths=10,actual_corner_cell_ray_paths=8,deep_central_opening_ray_depth=dark_depth,red_status_ray_paths=1,actual_blue_porthole_quadrant_rays=8,porthole_separator_ray_paths=2,maximum_flowing_casting_surface_distance=distance,projected_medallion_radius_error=circle_error,projected_medallion_boundary_angles=48,operational_timing_established=False,hidden_rear_interpretation=True)
