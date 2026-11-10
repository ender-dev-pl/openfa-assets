"""RI21 retained housings, cradle/face contacts, twelve caps and opaque faces."""
import bpy
import bmesh
from verify_rigellian_storage_racks import structure as retained_structure,texture_evidence
from rigellian_storage_racks_parts import PROFILES,FACE_KEYS
from rigellian_extractor_remaster_checks import uv_snapshot,compare_uv


def textures():
    return texture_evidence([o for o in bpy.context.scene.objects if o.type=='MESH'])


def structure():
    meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==32 and len(PROFILES)==6 and len(FACE_KEYS)==5
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
            assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0,obj.name
        finally:
            bm.free()
    bounds,contacts = retained_structure(meshes)
    assert len(contacts['components'])==1 and not contacts['isolated']
    green = bpy.data.materials['RI21 | green oval faces'].node_tree.nodes.get('Principled BSDF')
    assert green.inputs['Transmission Weight'].default_value==0
    assert green.inputs['Emission Strength'].default_value==0
    assert green.inputs['Alpha'].default_value==1 and green.inputs['Roughness'].default_value>=.5
    assert len([o for o in meshes if o.name.startswith('RI21 green oval face ')])==5
    assert len([o for o in meshes if o.name.startswith('RI21 front guide ') and 'tie' not in o.name])==2
    return dict(positive_closed_meshes=len(meshes),body_bounds=bounds,
        one_sampled_contact_component=True,sampled_contact_graph=contacts,
        six_measured_dents_and_housing_cradle_contacts=True,
        five_oval_rim_roots_and_face_contacts=True,two_front_guides_seated=True,
        opaque_non_emissive_green_faces=5,texture_pixels_and_uvs=textures(),
        contact_scope='Retained cradle/spine/guide containment and 160 flange/25 face rays plus sampled contact graph; not exhaustive solid intersection proof.')
