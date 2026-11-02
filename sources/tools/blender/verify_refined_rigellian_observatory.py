"""Verify visible RI4C equipment and independent native/GLB presentation."""
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_observatory import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, selected_view, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render, pixels


def structure():
    root = bpy.data.objects['PlacementRoot']
    assert root['catalogue_id'] == 'openfa:ship/rigellian/observatory'
    assert max(abs(root.matrix_world[i][j]-(1 if i == j else 0)) for i in range(4) for j in range(4)) < 1e-6
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    planform = bpy.data.objects['Authored station planform fit']
    assert planform.parent == root
    for obj in meshes:
        assert obj.parent == planform, (obj.name, 'Detached component')
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data = evaluated.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(e.is_manifold for e in bm.edges), (obj.name, 'Open physical surface')
        assert bm.calc_volume(signed=True) > 0, (obj.name, 'Inverted/empty physical component')
        bm.free()
        evaluated.to_mesh_clear()
    bands = [o for o in meshes if o.name.startswith('RI4C equatorial equipment band')]
    points = [o.matrix_world@v.co for o in bands for v in o.data.vertices]
    height = max(p.z for p in points)-min(p.z for p in points)
    assert height > .31, 'Equipment belt regressed to a thin rim'
    insets = [o for o in meshes if 'bright inset' in o.name]
    assert len(insets) == 20 and all(len(o.data.uv_layers) for o in insets)
    for i in range(4):
        assert len([o for o in insets if o.name.startswith(f'RI4C bay {i} ')]) == 5
    assert len([o for o in meshes if o.name.startswith('RI4C central pale inset')]) == 6
    assert len([o for o in meshes if o.name.startswith('RI4C chamber pale bar')]) == 6
    assert len([o for o in meshes if o.name.startswith('RI4C fork lateral prong')]) == 6
    assert len([o for o in meshes if o.name.startswith('RI4C lower axial side terminal')]) == 2
    assert len([o for o in meshes if o.name.startswith('Observatory pointed fin')]) == 8
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Unverified wireframe deployment loop'
    # The legacy view leaves the forward green chamber face visible. Test
    # actual fin geometry rather than merely counting pointed objects.
    chamber_visibility = []
    for z in [.96, -1.20]:
        obstructed = []
        for obj in meshes:
            if not obj.name.startswith('Observatory pointed fin'):
                continue
            tree = BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                                       [list(p.vertices) for p in obj.data.polygons])
            hit = tree.ray_cast(Vector((0, -4, z)), Vector((0, 1, 0)), 3.5)[0]
            if hit is not None:
                obstructed.append(obj.name)
        assert not obstructed, ('Fin occludes the centre of a forward equipment face', z, obstructed)
        chamber_visibility.append(z)
    return dict(positive_closed_meshes=len(meshes), belt_height=height, equipment_bays=4,
                bright_bay_insets=len(insets), pale_central_insets=6, chamber_bars=6,
                three_prong_upper_terminal=True, two_lower_side_terminals=True,
                front_chamber_faces_clear_of_fins=chamber_visibility)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_observatory.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    for name, value in meta['dependencies_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    original = snapshot()
    alignment = [list(row) for row in bpy.data.objects['AlignmentAxis'].matrix_world]
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    error_preserved = 0
    for name in meta['preserved_objects']:
        expected = [(p[0]*meta['planform_scale'], p[1]*meta['planform_scale'], p[2]) for p in original[name]['points']]
        error_preserved = max(error_preserved, drift(expected, native[name]['points']))
        assert original[name]['materials'] == native[name]['materials']
        assert native[name]['parent'] == 'Authored station planform fit'
    assert error_preserved < 3e-6, error_preserved
    assert set(native) == set(meta['preserved_objects']) | set(meta['modified_objects']) | set(meta['added_objects'])
    assert alignment == [list(row) for row in bpy.data.objects['AlignmentAxis'].matrix_world]
    collections = [c for c in bpy.data.collections if c.asset_data]
    assert len(collections) == 1 and all(o.name in collections[0].objects for o in bpy.context.scene.objects if o.type in ['MESH', 'EMPTY'])
    native_form = structure()
    views = ['front-quarter', 'front', 'belt-detail']
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        bpy.context.scene.render.filepath = str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    alpha = pixels(MEDIA/'front.png')[:, :, 3] > .5
    ys, xs = alpha.nonzero()
    frontal_aspect = (int(xs.max())-int(xs.min())+1)/(int(ys.max())-int(ys.min())+1)
    assert abs(frontal_aspect-94/126) < .06, ('Frontal planform is too narrow/tall relative to the source', frontal_aspect)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'))
    imported = snapshot()
    imported_form = structure()
    assert imported.keys() == native.keys()
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']), drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'], (name, 'Material binding drift')
        assert native[name]['parent'] == imported[name]['parent'], (name, 'Hierarchy drift')
    assert error < 1e-4, error
    renders = {}
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        path = MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(MEDIA/(view+'.png'), path, view != 'belt-detail')
    report = dict(issue=185, model='observatory', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  lore_sha256=meta['lore_sha256'], dependencies_sha256=meta['dependencies_sha256'],
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  retained_unrotated_components=len(meta['preserved_objects']),
                  authored_planform_scale=meta['planform_scale'], maximum_expected_planform_fit_error=error_preserved,
                  frontal_render_aspect=frontal_aspect, original_fixed_state_aspect=94/126,
                  modified_existing_fins=len(meta['modified_objects']), unchanged_authored_alignment_axis=True,
                  native_asset_collection_contains_complete_model=True, maximum_native_imported_position_error=error,
                  native_structure=native_form, imported_structure=imported_form, renders=renders,
                  acceptance='Verified visible equipment refinement; exact radial arrangement, second state and calibrated equipment mounts remain unresolved')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RI4C_VISIBLE_EQUIPMENT_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
