"""RI12 retained profile, measured dents, spindle, fittings and authored map checks."""
import bpy
import bmesh
from verify_rigellian_deep_space_probes import structure as retained_structure, texture_evidence


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
                five_measured_dents_spindle_overlap_and_cast_fitting=True,
                texture_pixels_and_uvs=texture_evidence(meshes),
                contact_scope='Retained local attachment rays and sampled contact graph; not exhaustive solid-intersection proof.')
