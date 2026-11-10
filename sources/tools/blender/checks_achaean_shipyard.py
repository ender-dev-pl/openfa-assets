"""AC11 four supported chambers, actual slots and projected front fitting."""
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

def material_contract():
    mat=bpy.data.materials['Coral alloy'];shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    def upstream(socket):
        queue=[l.from_node for l in socket.links];seen=set();images=set();normals=[]
        while queue:
            node=queue.pop()
            if node.name in seen:continue
            seen.add(node.name)
            if node.type=='TEX_IMAGE':assert node.image is not None;images.add(node.image.name)
            if node.type=='NORMAL_MAP':normals.append(node)
            queue.extend(l.from_node for pin in node.inputs for l in pin.links)
        return images,normals
    rough,_=upstream(shader.inputs['Roughness']);metal,_=upstream(shader.inputs['Metallic']);normal,maps=upstream(shader.inputs['Normal']);assert rough==metal and len(rough)==len(normal)==1 and rough!=normal;assert len(maps)==1 and abs(maps[0].inputs['Strength'].default_value-.35)<1e-6
    for name in rough|normal:assert bpy.data.images[name].colorspace_settings.name=='Non-Color' and tuple(bpy.data.images[name].size)==(256,256)
    values=list(bpy.data.images[next(iter(rough))].pixels)[1::4];variation=max(values)-min(values);assert variation>.02
    return variation


def structure():
    material_variation=material_contract()
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:building/legacy/161' and list(root['footprint'])==[3,3]
    for name in ['AC11 rear chamber 0','AC11 rear chamber 1','AC11 front chamber 0','AC11 front chamber 1','AC11 spine pedestal','AC11 small blue base','AC11 fitting ground shoe']:assert abs(bounds(name)[2])<1e-5
    spine=bounds('AC11 blue structural spine');collar=bounds('AC11 ochre spine collar');pedestal=bounds('AC11 spine pedestal');assert 2.70<spine[5]<2.80 and spine[2]<collar[5] and spine[2]<pedestal[5]
    verts=[];faces=[];owners=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        offset=len(verts);verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        for face in obj.data.polygons:faces.append(tuple(offset+i for i in face.vertices));owners.append(obj.name)
    surface=BVHTree.FromPolygons(verts,faces)
    def ray(p,d,name):
        hit=surface.ray_cast(Vector(p),Vector(d),6);assert hit[0] is not None and owners[hit[2]]==name,('Covered field',name,owners[hit[2]] if hit[0] is not None else None);return hit[3]
    for i,x in enumerate([-.60,.60]):
        ray((x,-2,1.38),(0,1,0),'AC11 middle red glass '+str(i));ray((x,.20,3),(0,0,-1),'AC11 upper red tip '+str(i))
    for x in [-.07,0,.07]:ray((x,-2,.95),(0,1,0),'AC11 ochre spine collar')
    depths=[]
    for i,dx in enumerate([-.16,.16]):depths.append(ray((-.60+dx,-2,.22),(0,1,0),'AC11 lower slot dark floor '+str(i)))
    assert all(.94<d<.98 for d in depths)
    for i,(x,z) in enumerate([(-.07,.21),(.07,.11)]):ray((x,-2,z),(0,1,0),'AC11 small base blue optic '+str(i))
    body=bpy.data.objects['AC11 front chamber 1'];tree=BVHTree.FromPolygons(points(body.name),[tuple(f.vertices) for f in body.data.polygons]);arch=points('AC11 ochre arched fitting collar');radius=max(tree.find_nearest(p)[3] for p in arch);assert radius<.07
    # The projected arch actually spans both sides and rises over the fitting.
    ab=bounds('AC11 ochre arched fitting collar');assert ab[0]<.44 and ab[3]>.76 and .71<ab[5]<.75
    fitting=bounds('AC11 coral vertical fitting');shoe=bounds('AC11 fitting ground shoe');assert fitting[2]<shoe[5] and fitting[5]>.64
    contacts=[]
    for i,sign in enumerate([-1,1]):
        body=bpy.data.objects['AC11 rear chamber '+str(i)];tree2=BVHTree.FromPolygons(points(body.name),[tuple(f.vertices) for f in body.data.polygons]);hit=tree2.ray_cast(Vector((sign*.60,-2,.40)),Vector((0,1,0)),4);front=bounds('AC11 front chamber '+str(i));assert hit[0] is not None and front[4]>hit[0].y;contacts.append(front[4]-hit[0].y)
    return dict(grounded_chamber_lobes=4,grounded_spine_and_base=True,spine_supported=True,visible_collar_ray_paths=3,red_middle_ray_paths=2,red_tip_ray_paths=2,actual_left_slot_ray_paths=2,minimum_left_slot_depth=min(depths),maximum_left_slot_depth=max(depths),blue_base_ray_paths=2,maximum_arch_surface_distance=radius,arch_spans_vertical_fitting=True,fitting_ground_supported=True,minimum_front_rear_overlap=min(contacts),operational_timing_established=False,hidden_rear_interpretation=True,coral_roughness_range=material_variation,coral_pbr_texture_inputs=3,coral_normal_strength=.35)
