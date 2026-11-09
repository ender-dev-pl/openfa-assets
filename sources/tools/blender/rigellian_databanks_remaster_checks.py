"""RI08 original body anatomy plus refined perforated-head and actual UV contracts."""
import hashlib
import math
import bpy
from verify_rigellian_databanks import structure as retained_structure
from verify_refined_rigellian_databanks import structure as refined_structure

def retained_body_textures(meshes):
    evidence={}
    for name,size in [('RI08 | aged jade shell',1024),('RI08 | worn planar end caps',512)]:
        material=bpy.data.materials[name];shader=material.node_tree.nodes.get('Principled BSDF')
        texture=shader.inputs['Base Color'].links[0].from_node;colour=texture.image
        assert list(colour.size)==[size,size] and colour.packed_file
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert rough.type=='TEX_IMAGE' and rough.image.packed_file
        evidence[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
            roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    cap_planes=0
    for obj in meshes:
        if not (obj.name in ['RI08 lower intake drum','RI08 solid connecting neck','RI08 flared middle housing']): continue
        vertices=[obj.matrix_world @ v.co for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name=='RI08 | worn planar end caps'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=='RI08 | aged jade shell'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/5.2)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==6
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def texture_evidence(meshes):
    result = retained_body_textures(meshes)
    material = bpy.data.materials['RI08 | worn pale upper equipment shell']
    shader = material.node_tree.nodes.get('Principled BSDF')
    colour = shader.inputs['Base Color'].links[0].from_node.image
    rough = shader.inputs['Roughness'].links[0].from_node
    channel = 0
    if rough.type in ['SEPARATE_COLOR', 'SEPRGB']:
        channel = 1
        rough = rough.inputs[0].links[0].from_node
    assert colour.packed_file and list(colour.size) == [512, 512]
    assert rough.type == 'TEX_IMAGE' and rough.image.packed_file
    result['materials'][material.name] = dict(
        colour=hashlib.sha256(bytes(round(max(0, min(1, v))*255) for v in colour.pixels[:])).hexdigest(),
        roughness=hashlib.sha256(bytes(round(max(0, min(1, v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    projected = {}
    for obj in meshes:
        if obj.name not in ['RI08 rounded upper head', 'RI08 pale perforated equipment casing'] and not obj.name.startswith('RI08 broad equipment port'):
            continue
        chart = obj.data.uv_layers.active
        assert chart is not None, obj.name
        for face in obj.data.polygons:
            # The refined source uses local box projection before triangulation.
            # A resulting triangle must retain one consistent original plane;
            # its own normal need not have the same dominant axis as its parent.
            valid_planes = 0
            for omitted in range(3):
                axes = [i for i in range(3) if i != omitted]
                valid = True
                for index in face.loop_indices:
                    point = obj.data.vertices[obj.data.loops[index].vertex_index].co
                    uv = chart.data[index].uv
                    valid &= all(abs(uv[j]-(.5+point[axis]*.65)) < 1e-5 for j, axis in enumerate(axes))
                valid_planes += bool(valid)
            assert valid_planes, (obj.name, 'Refined local projected UV chart changed')
        projected[obj.name] = len(obj.data.polygons)
    assert len(projected) == 10
    result['refined_projected_faces'] = projected
    return result


def structure():
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bounds, contacts = retained_structure(meshes)
    refined = refined_structure()
    textures = texture_evidence(meshes)
    return dict(positive_closed_meshes=refined['positive_closed_meshes'], body_bounds=bounds,
                one_sampled_contact_component=len(contacts['components']) == 1,
                retained_body_and_cast_bezel_contacts=True, refined_head=refined,
                texture_pixels_and_uvs=textures,
                contact_scope='Existing sampled nearest-surface contact graph; not exhaustive structural intersection proof.')
