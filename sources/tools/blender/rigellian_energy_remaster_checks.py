"""RI14 current broad casings plus retained bowl, conduit, dents and mapped profiles."""
import hashlib
import json
from pathlib import Path
import finish_rigellian_energy_uvs
import bpy
from mathutils import Vector
from verify_rigellian_energy_gatherer import (PROFILES, DENTS, profile_radius, ray, geometry_bounds, audit, texture_evidence)
from verify_refined_rigellian_energy_casings import structure as casing_structure
import math


def retained_body_structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==root for obj in meshes)
    for name,profile in PROFILES.items():
        phi,z,depth=DENTS[name];normal=Vector((math.cos(phi),math.sin(phi),0))
        hit=ray(bpy.data.objects[name],normal*2+Vector((0,0,z)),-normal)
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.45,(name,'Geometric dent missing')
    for a,b,z in [('RI14 twin chamber lower body','RI14 tapered grey connector',1.56),('RI14 tapered grey connector','RI14 bronze upper vessel',2.03),('RI14 bronze upper vessel','RI14 crown floor',2.80),('RI14 crown floor','RI14 central crown probe',2.79)]:
        assert ray(bpy.data.objects[a],(0,0,z),(1,0,0)) is not None and ray(bpy.data.objects[b],(0,0,z),(1,0,0)) is not None,(a,b,'Missing assembly overlap')
    crown=bpy.data.objects['RI14 open upturned crown'];floor=bpy.data.objects['RI14 crown floor']
    assert ray(crown,(2,0,2.785),(-1,0,0)).x>ray(floor,(0,0,2.785),(1,0,0)).x>ray(crown,(0,0,2.785),(1,0,0)).x
    for i,phi in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
        n=Vector((math.cos(phi),math.sin(phi),0));post=bpy.data.objects[f'RI14 crown upright {i}']
        point=n*2+Vector((0,0,3.00));outer=ray(crown,point,-n);inner=ray(crown,Vector((0,0,3.00)),n)
        assert ray(post,point,-n).dot(n)>inner.dot(n) and ray(post,Vector((0,0,3.00)),n).dot(n)<outer.dot(n)
    # Clear bowl above the floor, away from the central probe and crown uprights.
    for radius in [.12,.20,.28]:
        hit=ray(crown,(radius,0,4),(0,0,-1));floor_hit=ray(floor,(radius,0,4),(0,0,-1))
        assert floor_hit is not None and (hit is None or hit.z<floor_hit.z),'Crown must not close the aperture above its floor'
    body=bpy.data.objects['RI14 twin chamber lower body'];pipe=bpy.data.objects['RI14 silver front conduit']
    for i,z in enumerate([.20,.59,1.09,1.43]):
        shoe=bpy.data.objects[f'RI14 conduit retaining shoe {i}']
        skin=ray(body,(.20,-2,z),(0,1,0)).y
        assert ray(shoe,(.20,2,z),(0,-1,0)).y>skin>ray(shoe,(.20,-2,z),(0,1,0)).y
        assert ray(pipe,(.20,2,z),(0,-1,0)).y>ray(shoe,(.20,-2,z),(0,1,0)).y
    vessel=bpy.data.objects['RI14 bronze upper vessel']
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        n=Vector((math.cos(phi),math.sin(phi),0));panel=bpy.data.objects[f'RI14 upper vessel alloy inset {i}']
        for z in [2.37,2.45,2.53]:
            p=n*2+Vector((0,0,z));skin=ray(vessel,p,-n).dot(n)
            assert ray(panel,p,-n).dot(n)>skin>ray(panel,-n*2+Vector((0,0,z)),n).dot(n)
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001 and abs(bounds[5]-3.40)<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def structure():
    root = Path(__file__).resolve().parents[3]
    meta = json.loads((root/'sources/objects/rigellian/energy-gatherer/model.json').read_bytes())
    finish = meta['casing_uv_finish']
    assert hashlib.sha256((root/finish['tool']).read_bytes()).hexdigest() == finish['sha256']
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    bounds, contacts = retained_body_structure(meshes)
    assert len(contacts['components']) == 1
    casing = casing_structure()
    # New casing faces retain their established local planar projections.
    for obj in meshes:
        if 'refined casing' not in obj.name:
            continue
        uv = obj.data.uv_layers.active
        for face in obj.data.polygons:
            axis = max(range(3), key=lambda i: abs(face.normal[i]))
            a, b = [i for i in range(3) if i != axis]
            for index in face.loop_indices:
                point = obj.data.vertices[obj.data.loops[index].vertex_index].co
                actual = uv.data[index].uv
                assert abs(actual.x-(.5+point[a]*.65)) < 1e-5
                assert abs(actual.y-(.5+point[b]*.65)) < 1e-5
    textures = texture_evidence(meshes)
    shader = bpy.data.materials['RI14 | worn recessed bronze casing'].node_tree.nodes.get('Principled BSDF')
    colour = shader.inputs['Base Color'].links[0].from_node.image
    rough = shader.inputs['Roughness'].links[0].from_node
    channel = 0
    if rough.type in ['SEPARATE_COLOR', 'SEPRGB']:
        channel = 1
        rough = rough.inputs[0].links[0].from_node
    assert rough.type == 'TEX_IMAGE' and rough.image.packed_file
    textures['materials']['RI14 | worn recessed bronze casing'] = dict(
        colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
        roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    return dict(positive_closed_meshes=casing['positive_closed_meshes'], body_bounds=bounds,
                one_sampled_contact_component=True, casing=casing,
                four_measured_dents_open_bowl_conduit_shoes_and_vessel_insets=True,
                texture_pixels_and_uvs=textures,
                contact_scope='Retained body rays plus solid casing contacts and sampled contact graph; not exhaustive intersection proof.')
