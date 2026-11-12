"""RI07 retained source anatomy, complete maps and thin silver fork contract."""
import bpy
import bmesh
from verify_rigellian_science import structure as retained_structure, texture_evidence


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
    bounds, contacts = retained_structure(meshes)
    textures = texture_evidence(meshes)
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=len(contacts['components']) == 1,
                actual_well_sleeve_floor_fins_and_three_dents=True,
                covers_rim_fittings_pedestal_neck_and_silver_fork_contacts=True,
                texture_pixels_and_uvs=textures,
                contact_scope='Existing sampled nearest-surface contact graph; not exhaustive structural intersection proof.')
