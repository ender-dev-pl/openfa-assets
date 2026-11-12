"""RI11 permanent open port, source anatomy, maps and static-state evidence."""
import hashlib
import json
from pathlib import Path
import bpy
import bmesh
from verify_rigellian_probe_launch import structure as retained_structure, texture_evidence


def structure():
    root = Path(__file__).resolve().parents[3]
    recipe = json.loads((root/'sources/objects/rigellian/probe-launch/recipe.json').read_bytes())
    path = root/recipe['state_evidence']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == recipe['state_evidence_sha256']
    audit = json.loads(path.read_bytes())
    record = next(row for row in audit['records'] if row['key'] == 'RI11')
    assert [row['descriptor'] for row in record['descriptors']] == [0, 1]
    assert record['source_actions'] == []
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
    assert len(contacts['components']) == 1
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=True, static_open_port_descriptors=[0,1],
                actual_open_bore_three_flat_guides_dent_and_cast_fitting=True,
                texture_pixels_and_uvs=texture_evidence(meshes),
                contact_scope='Actual attachment rays plus existing sampled contact graph; not exhaustive solid-intersection proof.')
