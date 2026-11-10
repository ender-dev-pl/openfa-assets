"""RI16 retained head, housings, support joints, ten dents and complete maps."""
import bpy
import bmesh
from verify_rigellian_shield_generator import structure as retained_structure, texture_evidence


def structure():
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges), obj.name
            assert bm.calc_volume(signed=True) > 0, obj.name
        finally:
            bm.free()
        for material in obj.data.materials:
            shader = material.node_tree.nodes.get('Principled BSDF')
            assert shader.inputs['Transmission Weight'].default_value == 0
            assert shader.inputs['Alpha'].default_value == 1
            assert not shader.inputs['Emission Color'].is_linked
            assert not shader.inputs['Emission Strength'].is_linked
            assert max(shader.inputs['Emission Color'].default_value[:3]) * shader.inputs['Emission Strength'].default_value == 0
    bounds, contacts = retained_structure(meshes)
    assert len(contacts['components']) == 1
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=True,
                ten_measured_dents_head_waist_grooves_and_support_joints=True,
                opaque_nontransmissive_zero_effective_emission=True,
                texture_pixels_and_uvs=texture_evidence(meshes),
                contact_scope='Retained attachment/groove rays and sampled contact graph; not exhaustive solid-intersection proof.')
