"""RI05 retained anatomy, UVs, crown and physical inspection-well contract."""
import math
import bpy
import bmesh
from mathutils import Vector
from verify_rigellian_health import ray, BASE, HEAD, VENTS, DENTS, radius, audit, geometry_bounds, texture_evidence
from verify_rigellian_crowns import form

def retained_body_structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    base=bpy.data.objects['RI05 flared mounting pedestal'];neck=bpy.data.objects['RI05 narrow structural neck'];head=bpy.data.objects['RI05 rounded vented head']
    for index,(phi,width) in enumerate(VENTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0))
        hit=ray(head,normal*2+Vector((0,0,2.05)),-normal)
        assert hit is not None and math.hypot(hit.x,hit.y)<.44,'Grille must penetrate actual head shell'
        backing=bpy.data.objects[f'RI05 vent {index} recessed backing']
        louvres=[obj for obj in meshes if obj.name.startswith(f'RI05 vent {index} paired cooling louvre')]
        assert len(louvres)==(10 if index==1 else 5)
        for louvre in louvres:
            centre=louvre.matrix_world.translation;axis=centre-normal*centre.dot(normal)
            back=ray(louvre,axis,normal);front=ray(louvre,axis+normal*2,-normal);support=ray(backing,axis+normal*2,-normal)
            assert back is not None and front is not None and support is not None
            assert back.dot(normal)<support.dot(normal)<front.dot(normal),'Louvre must meet actual backing'
    for obj,profile,(phi,z,depth) in zip([base,head],[BASE,HEAD],DENTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));hit=ray(obj,normal*2+Vector((0,0,z)),-normal)
        assert depth*.75<radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.3
    assert ray(neck,(0,0,-1),(0,0,1)).z<ray(base,(0,0,6),(0,0,-1)).z
    assert ray(neck,(0,0,6),(0,0,-1)).z>ray(head,(0,0,-1),(0,0,1)).z
    face=bpy.data.objects['RI05 pedestal circular inspection face'];centre=face.matrix_world.translation
    normal=face.matrix_world.to_3x3() @ Vector((0,0,1))
    tangent=face.matrix_world.to_3x3() @ Vector((1,0,0));edge=centre+tangent*.10
    skin=ray(base,edge+normal*2,-normal);front=ray(face,edge+normal*2,-normal);back=ray(face,edge-normal*2,normal)
    assert back.dot(normal)<skin.dot(normal)<front.dot(normal),'Circular foot fitting must embed into real base'
    assert ray(face,centre+normal*2,-normal) is None,'Inspection face centre must be an actual opening'
    bottom=ray(base,centre+normal*2,-normal)
    floor=bpy.data.objects['RI05 recessed circular inspection floor']
    floor_front=ray(floor,centre+normal*2,-normal);floor_back=ray(floor,centre-normal*2,normal)
    assert floor_back.dot(normal)<bottom.dot(normal)<floor_front.dot(normal),'Inspection floor must embed in cut base'
    assert (front-floor_front).dot(normal)>.06,'Inspection centre must be visibly recessed'
    stem=bpy.data.objects['RI05 crown solid mounting stem'];bowl=bpy.data.objects['RI05 crown flared fork bowl']
    assert ray(stem,(0,0,-1),(0,0,1)).z<ray(head,(0,0,6),(0,0,-1)).z
    assert ray(bowl,(0,0,-1),(0,0,1)).z<ray(stem,(0,0,6),(0,0,-1)).z
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
    crown = form('ri05')
    textures = texture_evidence(meshes)
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=len(contacts['components']) == 1,
                three_open_grilles_twenty_seated_louvres=True, recessed_inspection_well_and_two_dents=True,
                crown=crown, texture_pixels_and_uvs=textures,
                contact_scope='Existing sampled nearest-surface contact graph; not exhaustive structural intersection proof.')
