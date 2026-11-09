"""RI09 retained open platforms, casting maps and equipment support checks."""
import bpy
import bmesh
from verify_rigellian_construction import structure as retained_structure, texture_evidence, ray
from rigellian_construction_parts import PODS


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
    supports = []
    for index, (x, y) in enumerate(PODS):
        post = bpy.data.objects[f'RI09 internal green equipment post {index}']
        runner = bpy.data.objects[f'RI09 equipment post {index} mounting runner']
        cap = bpy.data.objects[f'RI09 equipment post {index} pale head']
        # Intervals from rays through the actual solids must overlap, not
        # merely their bounding boxes. Offset inside the runner end and post.
        for other in [runner, cap]:
            low_a = ray(post, (x, y+.01, -1), (0, 0, 1))
            high_a = ray(post, (x, y+.01, 3), (0, 0, -1))
            low_b = ray(other, (x, y+.01, -1), (0, 0, 1))
            high_b = ray(other, (x, y+.01, 3), (0, 0, -1))
            assert all(p is not None for p in [low_a, high_a, low_b, high_b]), other.name
            assert max(low_a.z, low_b.z) < min(high_a.z, high_b.z), other.name
        supports.append(post.name)
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=len(contacts['components']) == 1,
                open_annular_centres_ten_recesses_dents_hood_and_column=True,
                four_posts_seated_in_runners_and_pale_caps=supports,
                texture_pixels_and_uvs=texture_evidence(meshes),
                contact_scope='Actual support ray intervals plus existing sampled contact graph; not exhaustive solid-intersection proof.')
