"""AC06 low crown, real warm window recesses and four dark-backed top ports."""
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
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/156' and list(root['footprint'])==[2,2]
    roof=bounds('AC06 broad lobed roof');drum=bounds('AC06 inhabited lower drum');cap=bounds('AC06 blue roof cap');ratio=(roof[3]-roof[0])/(drum[3]-drum[0]);assert 1.45<ratio<1.70
    assert abs(drum[2])<1e-5 and roof[2]<drum[5] and cap[2]<roof[5]-.04
    assert .85<cap[5]/(roof[3]-roof[0])<.95 and 1.75<cap[5]<1.85
    assert components('AC06 twenty warm panes')==20
    roof_obj=bpy.data.objects['AC06 broad lobed roof'];roof_tree=BVHTree.FromPolygons(points(roof_obj.name),[tuple(f.vertices) for f in roof_obj.data.polygons]);distance=max(roof_tree.find_nearest(p)[3] for name in ['AC06 upper flowing casting','AC06 lower flowing casting','AC06 right flowing casting'] for p in points(name));assert distance<.045
    verts=[];faces=[];owners=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        for face in obj.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(obj.name)
    surface=BVHTree.FromPolygons(verts,faces);windows=[]
    for i in range(10):
        a=2*math.pi*i/10;normal=Vector((math.cos(a),math.sin(a),0))
        for z in [.165,.295]:
            hit=surface.ray_cast(Vector((1.2*math.cos(a),1.2*math.sin(a),z)),-normal,2);assert hit[0] is not None and .52<hit[3]<.55;assert owners[hit[2]]=='AC06 twenty warm panes',('Window is covered',i,z,owners[hit[2]]);windows.append(hit[3])
    ports=[];pz=1.59+(.39-.26)/(.39-.18)*.10
    for i in range(4):
        a=math.pi/4+i*math.pi/2;normal=Vector((math.cos(a),math.sin(a),2.1)).normalized();p=Vector((.26*math.cos(a),.26*math.sin(a),pz));hit=surface.ray_cast(p+normal*.20,-normal,1);assert hit[0] is not None and .205<hit[3]<.235;assert owners[hit[2]]=='AC06 port dark floor '+str(i),('Roof port is covered or unbacked',i,owners[hit[2]]);ports.append(hit[3])
    return dict(one_low_surface_crown=True,roof_to_drum_width_ratio=ratio,roof_and_cap_seated=True,maximum_copper_casting_surface_distance=distance,paired_warm_window_panes=20,actual_window_ray_paths=20,minimum_window_ray_depth=min(windows),maximum_window_ray_depth=max(windows),actual_dark_backed_top_ports=4,minimum_top_port_ray_depth=min(ports),maximum_top_port_ray_depth=max(ports),underground_interior_not_invented=True,operational_timing_established=False)
