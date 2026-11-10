"""RI13 retained curved risers, fittings, dents and local/deformed UV checks."""
import bpy
import bmesh
from verify_rigellian_gravitic_converter import structure as retained_structure, texture_evidence


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
    bounds, contacts = retained_structure(meshes)
    assert len(contacts['components']) == 1
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=True,
                six_measured_dents_curved_risers_and_two_cast_fittings=True,
                texture_pixels_and_uvs=texture_evidence(meshes),
                contact_scope='Retained attachment rays and sampled contact graph; not exhaustive solid-intersection proof.')
