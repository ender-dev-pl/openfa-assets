"""Verify the complete refined Rigellian missile series in native and standalone GLB form."""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_missiles import ROOT, KEYS, VIEWS, paths, select_view, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render


def bvh(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [list(p.vertices) for p in obj.data.polygons])


def structure(meta, module):
    root = bpy.data.objects['PlacementRoot']
    assert root['catalogue_id'] == meta['id']
    assert max(abs(root.matrix_world[i][j]-(1 if i == j else 0)) for i in range(4) for j in range(4)) < 1e-6
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    trees = {}
    for obj in objects:
        assert obj.parent == root, obj.name
        data = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(e.is_manifold for e in bm.edges), (obj.name, 'Open physical surface')
        assert all(e.is_contiguous for e in bm.edges), (obj.name, 'Inconsistent surface winding')
        assert bm.calc_volume(signed=True) > 0, (obj.name, 'Empty/inverted component')
        bm.free()
        obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
        trees[obj.name] = bvh(obj)
    fork = meta['fork']
    start = module.PROFILES[module.CORE][-1][0]+.10
    witnesses = []
    for t in [.1, .5, .9]:
        y = start+(fork['high']-.02-start)*t
        assert not any(tree.ray_cast(Vector((0, y, 1)), Vector((0, 0, -1)), 2)[0] is not None
                       for tree in trees.values()), ('Fork interval is obstructed', y)
        witnesses.append(y)
    contacts = []
    prongs = [obj for obj in objects if 'rear prong' in obj.name]
    assert len(prongs) == 2
    for side, obj in zip([-1, 1], sorted(prongs, key=lambda o: o.name)):
        y = fork['low']+(fork['high']-fork['low'])*.07
        point = Vector((side*fork['outer_radius']*.48, y, 0))
        for name in [obj.name, module.CORE]:
            hit, normal, _, _ = trees[name].ray_cast(point, Vector((0, 0, 1)), 2)
            assert hit is not None and normal.z > 0, (name, 'Fork root does not intersect solid core', tuple(point))
        contacts.append(list(point))
    panel_widths = []
    for spec in meta['broad_panels']:
        obj = bpy.data.objects[spec['name']]
        points = [obj.matrix_world@v.co for v in obj.data.vertices]
        angles = [math.atan2(math.sin(math.atan2(-p.z, p.x)-spec['phi']),
                             math.cos(math.atan2(-p.z, p.x)-spec['phi'])) for p in points]
        measured = (max(angles)-min(angles))/2
        assert abs(measured-spec['width']) < 1e-4, (obj.name, 'Declared width is not present in the solid')
        if 'blue' in obj.name or 'red centre' in obj.name or 'pale body insert' in obj.name:
            assert measured > .38, (obj.name, 'Central colour field regressed to a narrow strip')
        panel_widths.append(dict(name=obj.name, angular_half_width=measured))
    collars = []
    for spec in meta['fitted_collars']:
        obj = bpy.data.objects[spec['name']]
        coords = [obj.matrix_world@v.co for v in obj.data.vertices]
        width = max(p.y for p in coords)-min(p.y for p in coords)
        assert width > spec['old_width']*1.25, (obj.name, 'Pale subdivision remains too thin')
        assert abs(width-(spec['high']-spec['low'])) < 1e-5
        collars.append(dict(name=obj.name, measured_width=width, old_width=spec['old_width']))
    if meta['id'].endswith('/detonator'):
        assert any('purple forward collar' in obj.name for obj in objects), 'Missing source purple subdivision'
    if meta['fork']['gold_outer_edges']:
        assert len([o for o in objects if 'gold rail' in o.name]) == 2
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Unverified articulated flight loop'
    return dict(positive_closed_meshes=len(objects), open_fork_witnesses=witnesses,
                solid_core_prong_contacts=contacts, broad_panels=panel_widths,
                pale_collars=collars, exhaust_excluded=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=KEYS, required=True)
    key = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model
    source, output, media = paths(key)
    meta = json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(source)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(output/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_missiles.py'))
    assert meta['parts_sha256'] == sha(Path(__file__).with_name(meta['parts_module']+'.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/missile-reference-index.json')
    for name, value in meta['dependency_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    module = importlib.import_module(meta['parts_module'])
    bpy.ops.wm.open_mainfile(filepath=str(source))
    old = snapshot()
    alignment = [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native = snapshot()
    assert set(native) == set(meta['preserved_objects']) | set(meta['modified_objects']) | set(meta['added_objects'])
    retained_error = 0
    for name in meta['preserved_objects']:
        retained_error = max(retained_error, drift(old[name]['points'], native[name]['points']))
        assert old[name]['materials'] == native[name]['materials'] and old[name]['parent'] == native[name]['parent']
    assert retained_error < 1e-6
    assert alignment == [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    native_structure = structure(meta, module)
    views = ['front-quarter', 'top', 'body-detail']
    for view in views:
        fit_camera(VIEWS[view], select_view(view))
        bpy.context.scene.render.filepath = str(media/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
    imported = snapshot()
    imported_structure = structure(meta, module)
    assert imported.keys() == native.keys()
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']), drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'], (name, 'Material binding changed')
        assert native[name]['parent'] == imported[name]['parent'], (name, 'Parent changed')
    assert error < .0001, error
    renders = {}
    for view in views:
        fit_camera(VIEWS[view], select_view(view))
        path = media/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(media/(view+'.png'), path, view != 'body-detail')
    report = dict(issue=185, model=key, blender=bpy.app.version_string, source_blend_sha256=sha(source),
                  blend_sha256=sha(output/'model.blend'), glb_sha256=sha(output/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  lore_sha256=meta['lore_sha256'], reference_sha256=meta['reference_sha256'],
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained_error,
                  maximum_native_imported_position_error=error, unchanged_uncalibrated_alignment_helper=True,
                  native_structure=native_structure, imported_structure=imported_structure, renders=renders,
                  acceptance='Verified static visible-section refinement; hidden sections, mechanisms and calibrated gameplay alignment remain open')
    (media/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RIGELLIAN_MISSILE_NATIVE_GLB_VERIFIED', key, len(native), error, flush=True)


if __name__ == '__main__':
    main()
