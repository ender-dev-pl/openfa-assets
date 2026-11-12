"""RI04 source-specific anatomy, UV, crown and physical surface contract."""
import math
import bpy
import bmesh
from mathutils import Vector
from verify_rigellian_community import ray, LOWER, UPPER, DENTS, radius, audit, geometry_bounds, texture_evidence
from verify_rigellian_crowns import form

def retained_body_structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    lower=bpy.data.objects['RI04 lower rounded pod'];upper=bpy.data.objects['RI04 upper rounded pod']
    pocket=ray(lower,(.10,-2,.55),(0,1,0));outside=ray(lower,(-.30,-2,.55),(0,1,0))
    assert pocket is not None and outside is not None and pocket.y-outside.y>.06,'Service opening must cut actual pod'
    for obj,profile,(phi,z,depth) in zip([lower,upper],[LOWER,UPPER],DENTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));hit=ray(obj,normal*2+Vector((0,0,z)),-normal)
        assert depth*.75<radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.3
    waist=bpy.data.objects['RI04 solid structural waist']
    assert ray(waist,(0,0,-1),(0,0,1)).z<ray(lower,(0,0,6),(0,0,-1)).z
    assert ray(waist,(0,0,6),(0,0,-1)).z>ray(upper,(0,0,-1),(0,0,1)).z
    fittings=[(f'RI04 upper fitting {row}-{column}',upper,-math.pi/2+offset,z-(.10 if column==1 else 0))
        for row,z in enumerate([1.68,2.02]) for column,offset in enumerate([-.63,0,.63])]
    fittings += [(f'RI04 lower fitting {i}',lower,-math.pi/2-.68,z) for i,z in enumerate([.43,.72])]
    for label,body,phi,z in fittings:
        normal=Vector((math.cos(phi),math.sin(phi),0));inside=Vector((0,0,z));outside=normal*2+inside
        bezel=bpy.data.objects[label+' dark retaining bezel'];face=bpy.data.objects[label+' square brass face']
        back=ray(bezel,inside,normal);front=ray(bezel,outside,-normal);skin=ray(body,outside,-normal)
        gold_back=ray(face,inside,normal);gold_front=ray(face,outside,-normal)
        assert back.dot(normal)<skin.dot(normal)<front.dot(normal),'Bezel must embed into shell'
        assert gold_back.dot(normal)<front.dot(normal)<gold_front.dot(normal),'Brass face must embed in bezel'
    red=bpy.data.objects['RI04 vertical red equipment core'];backing=bpy.data.objects['RI04 recessed service backing']
    red_front=ray(red,(.10,-2,.55),(0,1,0));red_back=ray(red,(.10,0,.55),(0,-1,0));support=ray(backing,(.10,-2,.55),(0,1,0))
    assert red_front.y<support.y<red_back.y,'Red core must meet backing'
    foundation=bpy.data.objects['RI04 crown stepped brass foundation'];socket=bpy.data.objects['RI04 crown solid fork socket']
    assert ray(foundation,(0,0,-1),(0,0,1)).z<ray(upper,(0,0,6),(0,0,-1)).z
    assert ray(socket,(0,0,-1),(0,0,1)).z<ray(foundation,(0,0,6),(0,0,-1)).z
    contact=audit();assert len(contact['components'])==1,contact['isolated']
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,contact


def structure():
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges), obj.name
            assert bm.calc_volume(signed=True) > 0, obj.name
        finally:
            bm.free()
    bounds, contacts = retained_body_structure(meshes)
    crown = form('ri04')
    textures = texture_evidence(meshes)
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=len(contacts['components']) == 1,
                eight_seated_brass_fittings=True, actual_recess_and_two_dents=True,
                crown=crown, texture_pixels_and_uvs=textures,
                contact_scope='Existing sampled nearest-surface contact graph; not exhaustive structural intersection proof.')
