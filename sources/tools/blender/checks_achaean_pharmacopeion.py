"""AC07 true passage, window banks, narrow neck and onion chamber."""
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
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/157' and list(root['footprint'])==[3,3]
    base=bounds('AC07 curved lower quarters');neck=bounds('AC07 narrow neck');upper=bounds('AC07 onion upper chamber');ratio=(upper[3]-upper[0])/(base[3]-base[0]);assert .50<ratio<.65;assert 3.4<upper[5]<3.5 and abs(base[2])<1e-5;assert neck[2]<base[5] and upper[2]<neck[5];assert (neck[3]-neck[0])/(base[3]-base[0])<.30
    assert components('AC07 consolidated window panes')==32
    verts=[];faces=[];owners=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        for face in obj.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(obj.name)
    surface=BVHTree.FromPolygons(verts,faces)
    passage=[]
    for x in [-.20,0,.20]:
        for z in [.12,.35,.60]:
            hit=surface.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is None,('Blocked doorway',x,z,owners[hit[2]]);passage.append([x,z])
    lower=bpy.data.objects['AC07 curved lower quarters'];lower_tree=BVHTree.FromPolygons(points(lower.name),[tuple(f.vertices) for f in lower.data.polygons]);supports=0
    for a in [math.atan2(-.96,-.72),math.atan2(-.96,.72),math.atan2(.96,-.72),math.atan2(.96,.72)]:
        n=Vector((math.cos(a),math.sin(a),0));t=Vector((-math.sin(a),math.cos(a),0));rim_depths=[p.dot(n) for p in points('AC07 consolidated window rims') if abs(p.dot(t))<.13 and p.dot(n)>1]
        assert min(rim_depths)<1.25 and max(rim_depths)>1.45
        for x in [-.10,.10]:
            for z in [.19,1.03]:
                hit=lower_tree.ray_cast(n*2+t*x+Vector((0,0,z)),-n,3);assert hit[0] is not None and hit[0].dot(n)>1.26;supports+=1
    window_depth=[]
    for i,a in enumerate([math.atan2(-.96,-.72),math.atan2(-.96,.72),math.atan2(.96,-.72),math.atan2(.96,.72)]):
        n=Vector((math.cos(a),math.sin(a),0));t=Vector((-math.sin(a),math.cos(a),0))
        for x,z in [(-.045,.43),(.045,.43),(-.045,.59),(.045,.59),(-.045,.75),(.045,.75),(0,.32),(0,.90)]:
            hit=surface.ray_cast(n*2+t*x+Vector((0,0,z)),-n,3);assert hit[0] is not None and .54<hit[3]<.59;assert owners[hit[2]]=='AC07 consolidated window panes',('Covered window',i,x,z,owners[hit[2]]);window_depth.append(hit[3])
    for i,a in enumerate([-math.pi/2-.34,-math.pi/2+.34,math.pi/2-.34,math.pi/2+.34]):
        n=Vector((math.cos(a),math.sin(a),0));hit=surface.ray_cast(n+Vector((0,0,1.71)),-n,2);assert hit[0] is not None and owners[hit[2]]=='AC07 blue neck inset '+str(i),('Covered neck field',i,owners[hit[2]])
    for z,name in [(2.92,'AC07 upper dark red slit'),(.95,'AC07 central amber lens')]:
        hit=surface.ray_cast(Vector((0,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None and owners[hit[2]]==name,('Covered status field',name,owners[hit[2]])
    crown=bpy.data.objects['AC07 onion upper chamber'];tree=BVHTree.FromPolygons(points(crown.name),[tuple(f.vertices) for f in crown.data.polygons]);distance=max(tree.find_nearest(p)[3] for name in ['AC07 upper flowing casting','AC07 lower flowing casting','AC07 side flowing casting'] for p in points(name));assert distance<.05
    return dict(grounded_two_sided_arched_base=True,clear_entrance_rays=len(passage),seated_window_rim_corner_checks=supports,upper_to_base_width_ratio=ratio,neck_and_crown_seated=True,window_panes=32,visible_window_ray_paths=len(window_depth),minimum_window_ray_depth=min(window_depth),maximum_window_ray_depth=max(window_depth),actual_neck_inset_ray_paths=4,actual_status_lens_ray_paths=2,maximum_flowing_casting_surface_distance=distance,operational_timing_established=False,hidden_rear_interpretation=True)
