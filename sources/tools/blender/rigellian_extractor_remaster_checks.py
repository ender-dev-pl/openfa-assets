"""RI20 retained refined anatomy, complete used-map pixels and UV corners."""
import hashlib
import math
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from verify_refined_rigellian_extractor import structure as refined_structure,tree
from refine_rigellian_extractor import PROFILE
from audit_rigellian_cpu_contacts import audit
from verify_nuclear_missile import geometry_bounds


def image_node(material,socket):
    node = material.node_tree.nodes.get('Principled BSDF').inputs[socket].links[0].from_node
    channel = None if socket=='Base Color' else 0
    if node.type in ['SEPARATE_COLOR','SEPRGB']:
        channel = 1
        node = node.inputs[0].links[0].from_node
    assert node.type=='TEX_IMAGE' and node.image.packed_file
    return node,channel


def mapped_uv(obj,node):
    vector = node.inputs['Vector']
    if vector.is_linked:
        coord = vector.links[0].from_node
        assert coord.type=='UVMAP',coord.type
        layer = obj.data.uv_layers.get(coord.uv_map)
    else:
        layer = obj.data.uv_layers.active
    assert layer is not None,obj.name
    return layer


def textures():
    evidence = {}
    for name,colour_size in [('RI20 refined | bronze and green surface finish',512),('RI20 | aged green lower alloy',1024)]:
        material = bpy.data.materials[name]
        record = {}
        for socket,key,size in [('Base Color','colour',colour_size),('Roughness','roughness',1024)]:
            node,channel = image_node(material,socket)
            assert list(node.image.size)==[size,size]
            values = node.image.pixels[:] if channel is None else node.image.pixels[:][channel::4]
            record[key] = hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in values)).hexdigest()
        evidence[name] = record
    return evidence


def uv_snapshot():
    records = {}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':
            continue
        groups = {}
        for polygon in obj.data.polygons:
            material = obj.data.materials[polygon.material_index]
            shader = material.node_tree.nodes.get('Principled BSDF')
            if not shader.inputs['Base Color'].is_linked:
                continue
            colour,_ = image_node(material,'Base Color')
            rough,_ = image_node(material,'Roughness')
            layer = mapped_uv(obj,colour)
            assert mapped_uv(obj,rough)==layer
            corners = groups.setdefault(material.name,[])
            for index in polygon.loop_indices:
                point = obj.matrix_world@obj.data.vertices[obj.data.loops[index].vertex_index].co
                uv = layer.data[index].uv.copy()
                assert all(math.isfinite(v) for v in uv)
                corners.append((point,uv))
        records[obj.name] = groups
    return records


def compare_uv(left,right):
    assert left.keys()==right.keys()
    maximum = 0.0
    count = 0
    for name in left:
        assert left[name].keys()==right[name].keys(),name
        for material in left[name]:
            for first,second in [(left[name][material],right[name][material]),(right[name][material],left[name][material])]:
                kd = KDTree(len(second))
                for i,(point,uv) in enumerate(second):
                    kd.insert(point,i)
                kd.balance()
                for point,uv in first:
                    candidates = kd.find_range(point,1e-5)
                    assert candidates,(name,material,'Missing corresponding UV corner')
                    error = min(max(abs(uv[k]-second[i][1][k]) for k in range(2)) for _,i,_ in candidates)
                    assert error<1e-5,(name,material,error)
                    maximum = max(maximum,error)
                    count += 1
    return dict(maximum_uv_corner_error=maximum,matched_directed_corners=count,position_tolerance=1e-5,
                scope='All used colour/roughness material corners matched bidirectionally by world position and UV, including split seams.')


def structure():
    form = refined_structure()
    contacts = audit()
    assert len(contacts['components'])==1 and not contacts['isolated']
    body = bpy.data.objects['RI20 stepped main casing']
    normal = Vector((math.cos(4.6),math.sin(4.6),0))
    dent_rows = []
    for name,centre,profile in [(body.name,(0,0),PROFILE),('RI20 pronounced side equipment pod',(-.53,-.10),[(.64,.19),(1.04,.19)])]:
        obj = bpy.data.objects[name]
        origin = Vector((*centre,.86))+normal*2
        point = tree(obj).ray_cast(origin,-normal,4)[0]
        assert point is not None
        radius = math.hypot(point.x-centre[0],point.y-centre[1])
        expected = next(a+(b-a)*(.86-za)/(zb-za) for (za,a),(zb,b) in zip(profile,profile[1:]) if za<=.86<=zb)
        depth = expected-radius
        assert .0003<depth<.004,(name,'Retained dent missing',depth)
        dent_rows.append(dict(name=name,depth=depth))
    bounds = geometry_bounds([o for o in bpy.context.scene.objects if o.type=='MESH'])
    assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2]-.02)<.001 and abs(bounds[5]-1.94)<.001
    form.update(body_bounds=bounds,retained_two_casing_dents=dent_rows,
        sampled_contact_graph=contacts,texture_pixels_and_uvs=textures(),
        contact_scope='Retained shoulder/rib/slot rays plus one sampled contact component; not exhaustive solid intersection proof.')
    return form
