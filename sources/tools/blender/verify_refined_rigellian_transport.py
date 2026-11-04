"""Reopen RI3C and independently verify its curved sections and standalone GLB."""
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_transport import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, FRONT, AFT, section, skin, old, selected_view, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render


def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [list(p.vertices) for p in obj.data.polygons])


def inside(bvh, point):
    direction = Vector((.173, .291, .941)).normalized()
    point = Vector(point)
    hit, normal, _, _ = bvh.ray_cast(point, direction, 10)
    return hit is not None and normal.dot(direction) > 0


def structure():
    root = bpy.data.objects['PlacementRoot']
    assert root['catalogue_id'] == 'openfa:ship/rigellian/transportation'
    assert max(abs(root.matrix_world[i][j]-(1 if i == j else 0)) for i in range(4) for j in range(4)) < 1e-6
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    trees = {}
    for obj in objects:
        assert obj.parent == root, (obj.name, 'Detached component')
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data = evaluated.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges), (obj.name, 'Open/inconsistently wound surface')
        assert bm.calc_volume(signed=True) > 0, (obj.name, 'Inverted/empty surface')
        bm.free()
        evaluated.to_mesh_clear()
        trees[obj.name] = tree(obj)
    for name in [FRONT, AFT, 'Transportation ventral connecting saddle']:
        assert inside(trees[name], (0, -.30, -.05)), (name, 'Inline connection gap')
    for name in [FRONT, 'Transportation copper terminal']:
        assert inside(trees[name], (0, -2.01, .03)), (name, 'Forward terminal gap')
    measured = []
    rounded = []
    for name, knot in [(FRONT, -1.35), (AFT, .45)]:
        bvh = trees[name]
        for y in [old.PROFILES[name][0][0]+.12, knot-.20, knot, knot+.20, old.PROFILES[name][-1][0]-.12]:
            width, z, _ = section(name, y)
            hit = bvh.ray_cast(Vector((3, y, z)), Vector((-1, 0, 0)), 4)[0]
            assert hit is not None and abs(hit.x-width) < .0008, (name, y, 'Unexpected actual body section')
            measured.append(dict(name=name, y=y, half_width=hit.x))
        samples = []
        for y in [knot-.012, knot, knot+.012]:
            z = section(name, y)[1]
            samples.append(bvh.ray_cast(Vector((3, y, z)), Vector((-1, 0, 0)), 4)[0].x)
        jump = abs((samples[2]-samples[1])/.012-(samples[1]-samples[0])/.012)
        old_jump = abs((old.section(name, knot+.012)[0]-old.section(name, knot)[0])/.012
                       -(old.section(name, knot)[0]-old.section(name, knot-.012)[0])/.012)
        assert jump < old_jump*.35, (name, 'Linear corner still present', jump, old_jump)
        rounded.append(dict(name=name, measured_slope_change=jump, old_slope_change=old_jump))
    patch = bpy.data.objects['Transportation gold forward patch']
    points = [patch.matrix_world@v.co for v in patch.data.vertices]
    patch_width = max(p.x for p in points)-min(p.x for p in points)
    assert patch_width > .52
    contacts = []
    for name, owner, x, y in [('Transportation gold forward patch', FRONT, 0, -1.22),
                              ('RI3C pale aft upper field', AFT, 0, .35)]:
        point = (x, y, skin(owner, x, y)-.003)
        assert inside(trees[name], point) and inside(trees[owner], point), (name, 'Skin attachment gap')
        contacts.append(dict(name=name, point=point))
    for side in [-1, 1]:
        point = (side*.56, .55, .035)
        name = 'RI3C copper shoulder pod '+str(side)
        assert inside(trees[name], point) and inside(trees[AFT], point), (name, 'Shoulder pod gap')
        y = .55
        x = side*section(AFT, y)[0]*.65
        point = (x, y, skin(AFT, x, y)-.003)
        name = 'Transportation copper aft trim '+str(side)
        assert inside(trees[name], point) and inside(trees[AFT], point), (name, 'Broad copper trim gap')
        contacts.append(dict(name=name, point=point))
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Unverified process/flight loop'
    return dict(positive_closed_meshes=len(objects), actual_sections=measured, rounded_profile_joins=rounded,
                gold_patch_width=patch_width, skin_contacts=contacts, two_bodies_joined=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_transport.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json')
    for name, value in meta['dependency_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    original = snapshot()
    alignment = [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    retained = 0
    for name in meta['preserved_objects']:
        retained = max(retained, drift(original[name]['points'], native[name]['points']))
        assert original[name]['materials'] == native[name]['materials'] and original[name]['parent'] == native[name]['parent']
    assert retained < 1e-6
    assert set(native) == set(meta['preserved_objects']+meta['modified_objects']+meta['added_objects'])
    assert alignment == [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    collections = [c for c in bpy.data.collections if c.asset_data]
    assert len(collections) == 1 and all(o.name in collections[0].objects for o in bpy.context.scene.objects if o.type in ['MESH', 'EMPTY'])
    native_structure = structure()
    views = ['front-quarter', 'top', 'body-detail']
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        bpy.context.scene.render.filepath = str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'))
    imported = snapshot()
    assert set(native) == set(imported)
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']), drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'] and native[name]['parent'] == imported[name]['parent']
    assert error < .0001
    assert max(abs(alignment[i][j]-bpy.data.objects['AlignmentForward'].matrix_world[i][j]) for i in range(4) for j in range(4)) < 1e-6
    imported_structure = structure()
    renders = {}
    for view in views:
        fit_camera(VIEWS[view], selected_view(view))
        path = MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(MEDIA/(view+'.png'), path, True)
    report = dict(issue=185, model='transportation', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained,
                  maximum_native_imported_position_error=error, native_structure=native_structure,
                  imported_structure=imported_structure, renders=renders,
                  acceptance='Verified source-bound static body refinement; final artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RI3C_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
