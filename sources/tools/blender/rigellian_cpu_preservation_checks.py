"""Preserve assessed RI01 body, repaired roof equipment and refined crown."""
import hashlib
import math
import bpy
import bmesh
from mathutils import Matrix
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_crowns import form
from audit_rigellian_cpu_contacts import audit


def textures():
    evidence = {}
    used = {slot.material for obj in bpy.context.scene.objects if obj.type=='MESH' for slot in obj.material_slots}
    assert len(used)==7
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
        evidence[material.name] = record
    return evidence


def retained_body_structure(meshes):
    bpy.context.view_layer.update()
    root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[r][c]-Matrix.Identity(4)[r][c]) for r in range(4) for c in range(4))<1e-6
    lookup={obj.name:obj for obj in meshes}
    seating=ray(lookup['CPU crown brass seating ring'],(.16,0,5),(0,0,-1))
    socket=ray(lookup['CPU crown solid mounting socket'],(.16,0,5),(0,0,-1))
    assert seating is not None and socket is not None and seating.z-socket.z>.01,'Crown socket and rim must not share coplanar top faces'
    roof=lookup['CPU broad upper saucer']
    floor=ray(roof,(-.55,-.12,4),(0,0,-1))
    surround=ray(roof,(-.83,-.12,4),(0,0,-1))
    assert floor is not None and surround is not None and surround.z-floor.z>.15,'Roof well must be cut into saucer'
    assert ray(lookup['CPU roof well inner sleeve'],(-.55,-.12,4),(0,0,-1)) is None
    sleeve=lookup['CPU roof well inner sleeve'];insert=lookup['CPU roof well recessed floor']
    bottom=ray(insert,(-.55,-.12,0),(0,0,1));top=ray(insert,(-.55,-.12,4),(0,0,-1))
    assert bottom.z<floor.z<top.z,'Well floor must embed into the actual cut bottom'
    wall=ray(roof,(-.55,-.12,2.53),(1,0,0))
    outside=ray(sleeve,(1,-.12,2.53),(-1,0,0))
    assert outside.x>wall.x,'Well sleeve must embed radially into the saucer'
    inside=ray(sleeve,(-.55,-.12,2.47),(1,0,0))
    floor_edge=ray(insert,(1,-.12,2.47),(-1,0,0))
    assert floor_edge.x>inside.x,'Floor must extend into sleeve wall'
    for obj in meshes:
        if not obj.name.startswith('CPU well interior cooling fin'): continue
        x,y,_=obj.matrix_world.translation
        foot=ray(obj,(x,y,0),(0,0,1));support=ray(insert,(x,y,4),(0,0,-1))
        assert foot is not None and support is not None and foot.z<support.z,'Cooling fin must meet floor'
    neck=ray(lookup['CPU neck with actual grille opening'],(0,-2,1.65),(0,1,0))
    assert neck is not None and neck.y>0,'Front grille aperture must penetrate neck shell'
    assert len([obj for obj in meshes if obj.name.startswith('CPU grille horizontal structural fin')])==5
    assert ray(lookup['CPU crown central terminal'],(0,0,5),(0,0,-1)).z>4
    cap=lookup['CPU pale conformal roof service cap'];top=[];back=[]
    normals=cap.matrix_world.to_3x3().inverted().transposed()
    for face in cap.data.polygons:
        normal=(normals @ face.normal).normalized()
        if abs(normal.z)<.6: continue
        point=cap.matrix_world @ face.center
        skin=ray(roof,(point.x,point.y,4),(0,0,-1))
        assert skin is not None
        (top if normal.z>0 else back).append(point.z-skin.z)
    assert top and back
    assert min(top)>.001 and max(top)<.015,(min(top),max(top))
    assert min(back)>-.025 and max(back)<-.003,(min(back),max(back))
    assert not any(obj.animation_data for obj in meshes)
    bounds=geometry_bounds(meshes)
    assert bounds[0]>=-1.5 and bounds[1]>=-1.5 and bounds[3]<=1.5 and bounds[4]<=1.5
    assert -.001<=bounds[2]<=.001
    return bounds



def structure():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    assert len(meshes)==75
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges),obj.name
            assert bm.calc_volume(signed=True)>0,obj.name
        finally:
            bm.free()
    bounds = retained_body_structure(meshes)
    crown = form('ri01')
    contacts = audit()
    assert len(contacts['components'])==1 and not contacts['isolated']
    return dict(positive_closed_meshes=len(meshes),body_bounds=bounds,
        retained_cut_roof_well_and_seated_cooling_fins=True,
        retained_conformal_cap_and_open_neck_grille=True,
        crown=crown,sampled_contact_graph=contacts,texture_pixels_and_uvs=textures(),
        clean_body_and_existing_crown_finish_preserved=True,
        contact_scope='Existing ray checks and sampled vertex/face nearest-surface contact graph, not exhaustive solid or continuous-state proof.')
