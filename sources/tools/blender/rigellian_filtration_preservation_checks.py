"""RI02 assessed geometry, wear maps, UV-index variants and retained contacts."""
import hashlib
import math
import bpy
import bmesh
from verify_rigellian_filtration import structure as retained_structure,texture_evidence


def textures():
    evidence = {}
    used = {obj.data.materials[face.material_index] for obj in bpy.context.scene.objects if obj.type=='MESH' for face in obj.data.polygons}

    for material in sorted(used,key=lambda m:m.name):
        shader = material.node_tree.nodes.get('Principled BSDF')
        record = {}
        for socket in ['Base Color','Metallic','Roughness','Alpha']:
            value = shader.inputs[socket]
            if value.is_linked:
                link = value.links[0]
                node = link.from_node
                factor = 1.0
                if node.type=='MATH':
                    assert node.operation=='MULTIPLY' and node.inputs[0].is_linked and not node.inputs[1].is_linked
                    factor = float(node.inputs[1].default_value)
                    link = node.inputs[0].links[0]
                    node = link.from_node
                channel = None if socket=='Base Color' else 0
                if node.type in ['SEPARATE_COLOR','SEPRGB']:
                    channel = {'Red':0,'Green':1,'Blue':2,'R':0,'G':1,'B':2}[link.from_socket.name]
                    node = node.inputs[0].links[0].from_node
                assert node.type=='TEX_IMAGE' and node.image.packed_file,(material.name,socket,node.type)
                image = node.image
                values = image.pixels[:] if channel is None else image.pixels[:][channel::4]
                assert all(math.isfinite(v) for v in values)
                quantized = bytes(round(max(0,min(1,v))*255) for v in (value*factor for value in values))
                if channel is not None and len(set(quantized))==1:
                    record[socket] = quantized[0]
                else:
                    record[socket] = dict(size=list(image.size),colour_space=image.colorspace_settings.name,
                        pixels=hashlib.sha256(quantized).hexdigest())
            else:
                raw = value.default_value
                record[socket] = [round(float(v),6) for v in raw] if hasattr(raw,'__iter__') else round(float(raw)*255)
        name = 'RI02 | aged jade shell' if material.name.startswith('RI02 | aged jade shell.') else material.name
        if name in evidence:
            assert evidence[name]==record,(name,'Unequal exported UV-index material variants')
        evidence[name] = record
    assert len(evidence)==7
    return evidence



def structure():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    assert len(meshes)==83
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges),obj.name
            assert bm.calc_volume(signed=True)>0,obj.name
        finally:
            bm.free()
    bounds,contacts = retained_structure(meshes)
    evidence = texture_evidence()
    evidence.pop('packed_images')
    return dict(positive_closed_meshes=len(meshes),body_bounds=bounds,
        eight_cut_lower_slots=True,two_measured_dents=True,three_height_cut_side_channel=True,
        six_embedded_front_pressure_faces=True,sampled_contact_graph=contacts,
        retained_authored_wear=evidence,texture_pixels_and_uvs=textures(),
        contact_scope='Existing eight-slot/channel/dent/pressure-face ray checks and sampled vertex/face nearest-surface contact graph; not exhaustive solid-contact proof.')
