"""Read-only, in-memory UV repair proposal. Never saves or exports a model."""
import hashlib
import importlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repair_detail_uvs import bind_detail_uvs, verify_detail_uvs
from build_refined_terran import render_to

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/detail-uv-proposal'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def geometry():
    """Exact native topology, positions, normals, assignments and hierarchy, excluding UVs."""
    result = {}
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        row = dict(type=obj.type, parent=obj.parent.name if obj.parent else None,
                   matrix=[list(r) for r in obj.matrix_world])
        if obj.type == 'MESH':
            def data(mesh):
                return dict(vertices=[list(v.co) for v in mesh.vertices],
                            edges=[list(e.vertices) for e in mesh.edges],
                            faces=[(list(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
                            normals=[list(n.vector) for n in mesh.corner_normals],
                            materials=[m.name if m else None for m in mesh.materials])
            row['native'] = digest(data(obj.data))
            evaluated = obj.evaluated_get(graph)
            mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
            try:
                row['evaluated'] = digest(data(mesh))
            finally:
                evaluated.to_mesh_clear()
        result[obj.name] = row
    return result


def images():
    return {image.name: hashlib.sha256(image.packed_file.data).hexdigest()
            for image in bpy.data.images if image.source == 'FILE'}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    previews = OUTPUT/'previews'
    previews.mkdir(parents=True, exist_ok=True)
    reports = []
    for slug, revision in [('bunker', 2), ('ultrathermal_lance', 1)]:
        builder = importlib.import_module('build_rigellian_' + slug)
        folder = builder.ROOT
        meta = json.loads((folder/'model.json').read_text())
        assert meta['revision'] == revision, 'Proposal only covers recorded original revisions'
        sources = {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        for ext in ['blend', 'glb']:
            assert sources['model.'+ext] == meta[ext+'_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
        before = geometry()
        packed = images()
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        scene = bpy.context.scene
        render_to(scene, previews/(folder.name+'-before.png'))
        changes = bind_detail_uvs(meshes)
        assert len(changes) == (1 if slug == 'bunker' else 2)
        assert not bind_detail_uvs(meshes), 'Proposal must be idempotent'
        uv_checks = verify_detail_uvs(meshes)
        assert before == geometry(), 'UV proposal altered geometry, normals, assignments or hierarchy'
        assert packed == images(), 'UV proposal altered packed textures'
        render_to(scene, previews/(folder.name+'-proposed.png'))
        assert sources == {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        report = dict(issue=1111, id=meta['id'], source_revision=meta['revision'], changes=changes,
                      source_files_sha256=sources, proposal_script_sha256=sha(Path(__file__)),
                      helper_sha256=sha(Path(__file__).with_name('repair_detail_uvs.py')),
                      exact_native_geometry_before_and_after=before,
                      packed_images_before_and_after=packed, idempotent=True,
                      uv_checks=uv_checks, saved_source_files_unchanged=True,
                      exported_or_saved_model=False, final_visual_acceptance=False,
                      preview_files={str(p.relative_to(REPO)).replace(chr(92), '/'): sha(p)
                                     for p in sorted(previews.glob(folder.name+'-*.png'))},
                      scope='In-memory UV proposal only; no repaired export or final art acceptance')
        (OUTPUT/(folder.name+'.json')).write_text(json.dumps(report, indent=2)+'\n')
        reports.append(meta['id'])
    print('RIGELLIAN_DETAIL_UV_PROPOSAL_OK', reports, flush=True)


if __name__ == '__main__':
    main()
