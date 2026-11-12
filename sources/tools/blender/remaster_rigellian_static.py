"""Recipe-driven static Rigellian remaster; retain completed anatomy and UVs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import uuid

import bmesh
import bpy
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
from refine_rigellian_crowns import fit_camera


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    faces = [tuple(p.vertices) for p in obj.data.polygons]
    return points, BVHTree.FromPolygons(points, faces)


def closed(obj):
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        return all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True) > 0
    finally:
        bm.free()


def strip_png(path):
    sys.path.insert(0, str(ROOT / 'tools'))
    from publication_support import clean_png
    path.write_bytes(clean_png(path.read_bytes()))


def main(recipe_path):
    recipe_path = recipe_path.resolve()
    assert recipe_path.is_relative_to((ROOT / 'sources/objects/rigellian').resolve())
    case = json.loads(recipe_path.read_bytes())
    SOURCE = (ROOT / case['source']).resolve()
    OUTPUT = recipe_path.parent
    MEDIA = (ROOT / case['media']).resolve()
    assert SOURCE.is_relative_to((ROOT / 'sources').resolve())
    assert MEDIA.is_relative_to((ROOT / 'gallery/media').resolve())
    before = sha(SOURCE)
    assert before == case['source_sha256']
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.frame_set(1)
    meshes = [o for o in scene.objects if o.type == 'MESH']
    baseline = {}
    changes = []
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        # Measure the same evaluated surface that the exporter renders, including
        # pre-existing bevels, rather than comparing pre-modifier face counts.
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        assert closed(obj), obj.name
        obj.data.calc_loop_triangles()
        baseline[obj.name] = dict(triangles=len(obj.data.loop_triangles))
        if baseline[obj.name]['triangles'] < 2500 or obj.name in case['protected_parts']:
            continue
        points, tree = surface(obj)
        original = obj.data.copy()
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new('Measured game tessellation reduction', 'DECIMATE')
        modifier.ratio = .58
        modifier.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        candidate, other = surface(obj)
        error = max([other.find_nearest(p)[3] for p in points]
                    + [tree.find_nearest(p)[3] for p in candidate])
        accepted = error <= .004 and closed(obj)
        if not accepted:
            rejected = obj.data
            obj.data = original
            bpy.data.meshes.remove(rejected)
        else:
            bpy.data.meshes.remove(original)
        obj.data.calc_loop_triangles()
        changes.append(dict(name=obj.name, original_triangles=baseline[obj.name]['triangles'],
                            triangles=len(obj.data.loop_triangles),
                            bidirectional_vertex_surface_error=error, accepted=accepted))
    root = bpy.data.objects['PlacementRoot']
    root['catalogue_id'] = case['id']
    root['footprint'] = case['footprint']
    root['forward_axis'] = 'local -Y'
    root['dorsal_axis'] = 'local +Z'
    root['state_contract'] = case['state_contract']
    for obj in meshes:
        assert obj.parent == root and closed(obj)
    # Keep editable component identities for technical diagrams. Material/batch
    # consolidation is not assumed from material count or claimed as achieved.
    fit_camera((6, -13, 8), meshes)
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 32
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes + [root]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    # Windows rejects tempfile's mode-0700 chmod in this restricted runtime.
    # Use task-owned workspace folders with inherited ACLs; TemporaryDirectory
    # still cleans them normally. Never redirect another task's temporary files.
    temporary_root = ROOT / 'artifacts/rigellian-remaster-temp'
    temporary_root.mkdir(parents=True, exist_ok=True)
    original_mkdtemp = tempfile.mkdtemp

    def workspace_temp(suffix=None, prefix=None, dir=None):
        parent = Path(dir).resolve() if dir else temporary_root
        assert parent.is_relative_to(ROOT.resolve())
        path = parent / ((prefix or case['key'].lower() + '-') + uuid.uuid4().hex + (suffix or ''))
        path.mkdir()
        return str(path)

    tempfile.mkdtemp = workspace_temp
    try:
        bpy.ops.export_scene.gltf(filepath=str(OUTPUT / 'model.glb'), export_format='GLB',
                                 use_selection=True, export_apply=True, export_extras=True,
                                 export_animations=False)
    finally:
        tempfile.mkdtemp = original_mkdtemp
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / 'model.blend'), compress=True)
    sys.path.insert(0, str(ROOT / 'tools'))
    from publication_support import clean_blend
    target = OUTPUT / 'model.blend'
    target.write_bytes(clean_blend(target.read_bytes())[0])
    for view, direction in [('front-quarter', (6, -13, 8)), ('front', (0, -16, 4)),
                            ('rear-quarter', (-7, 12, 7))]:
        fit_camera(direction, meshes)
        path = MEDIA / (view + '.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
    assert sha(SOURCE) == before
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    report = dict(issue=253, id=case['id'], name=case['name'],
                  author_sha256=sha(Path(__file__)), recipe=recipe_path.relative_to(ROOT).as_posix(),
                  recipe_sha256=sha(recipe_path),
                  camera_helper_sha256=sha(Path(__file__).with_name('refine_rigellian_crowns.py')),
                  source=SOURCE.relative_to(ROOT).as_posix(), source_sha256=before,
                  binaries={ext: sha(OUTPUT / ('model.' + ext)) for ext in ('blend', 'glb')},
                  original_triangles=sum(r['triangles'] for r in baseline.values()),
                  triangles=triangles, mesh_nodes=len(meshes), changes=changes,
                  footprint=case['footprint'], definition_class=case['definition_class'], construction_updates=case['construction_updates'],
                  scope='Measured candidate tessellation reduction, existing anatomy/materials/components retained. Requires saved-native and independent GLB verification and actual visual feedback before delivery.',
                  final_artistic_acceptance=False, game_client_integration=False)
    (OUTPUT / 'model.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('STATIC_RIGELLIAN_CANONICAL_CANDIDATE', case['key'], report['original_triangles'], triangles, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--recipe', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(args.recipe)
