"""Reopen RI0A visible lobes and independently verify its curved sections and standalone GLB."""
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_lazzaro_visible_forms import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, HULL, CROWN, CROWN_ROWS, interpolate, section, selected_view, fit_camera, sha
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
    assert root['catalogue_id'] == 'openfa:ship/rigellian/lazzaro-research'
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
    lobes = [o for o in objects if 'grey lobe' in o.name]
    assert len(lobes) == 4
    contacts, thicknesses = [], []
    for obj in lobes:
        side, end = [int(v) for v in obj.name.split()[-2:]]
        p = (side*.40, end*.42, .02)
        assert inside(trees[obj.name], p) and inside(trees[HULL], p), (obj.name, 'Lobe/body gap')
        contacts.append(p)
        top = trees[obj.name].ray_cast(Vector((side*.70, end*.47, 2)), Vector((0, 0, -1)), 4)[0]
        bottom = trees[obj.name].ray_cast(Vector((side*.70, end*.47, -2)), Vector((0, 0, 1)), 4)[0]
        assert top is not None and bottom is not None
        depth = top.z-bottom.z
        assert depth > .16, (obj.name, 'Regressed to a thin plate', depth)
        thicknesses.append(depth)
        tips = [face for face in obj.data.polygons if 'aged bronze' in obj.data.materials[face.material_index].name]
        assert tips and all(abs(sum(obj.data.vertices[i].co.x for i in f.vertices)/len(f.vertices)) > .80 for f in tips)
    # Two side intervals remain genuinely open outside the green body.
    for side in [-1, 1]:
        assert not any(bvh.ray_cast(Vector((side*.90, 0, 2)), Vector((0, 0, -1)), 4)[0] is not None for bvh in trees.values())
    crown = bpy.data.objects[CROWN]
    pts = [crown.matrix_world@v.co for v in crown.data.vertices]
    width = max(p.x for p in pts)-min(p.x for p in pts)
    assert width > .81, 'Central gold region is too narrow'
    for y in [-.50, -.10, .40]:
        w, z, h = interpolate(CROWN_ROWS, y)
        hit = trees[CROWN].ray_cast(Vector((2, y, z)), Vector((-1, 0, 0)), 4)[0]
        assert hit is not None and abs(hit.x-w*1.25) < .001, 'Crown still has sparse straight profile segments'
    p = (0, -.35, .12)
    assert inside(trees[CROWN], p) and inside(trees[HULL], p), 'Crown/body attachment gap'
    sections = []
    for y in [-.65, -.20, .25, .55]:
        w, z, h = section(y)
        hit = trees[HULL].ray_cast(Vector((2, y, z)), Vector((-1, 0, 0)), 4)[0]
        assert hit is not None and abs(hit.x-w) < .0015
        sections.append(dict(y=y, width=hit.x*2))
    for mat_name in ['RI0A | worn slate lateral shells', 'RI0A | worn gold crown finish']:
        mat = bpy.data.materials[mat_name]
        shader = mat.node_tree.nodes.get('Principled BSDF')
        image = shader.inputs['Base Color'].links[0].from_node.image
        assert image.packed_file and list(image.size) == [512, 512]
        assert shader.inputs['Roughness'].links, 'Authored roughness lost'
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Unverified operational loop'
    return dict(positive_closed_meshes=len(objects), lobe_root_contacts=contacts,
                lobe_thickness=thicknesses, gold_crown_width=width, body_sections=sections,
                copper_lobe_ends=True, open_lateral_intervals=True, packed_authored_wear=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_lazzaro_visible_forms.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/ship-reference-index.json')
    for name, value in meta['dependency_sha256'].items():
        assert value == sha(Path(__file__).with_name(name))
    for path, value in meta['texture_sha256'].items():
        assert sha(ROOT/path) == value
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
    assert set(original)-set(meta['removed_objects']) == set(native), 'Unexpected model population change'
    assert alignment == [list(row) for row in bpy.data.objects['AlignmentForward'].matrix_world]
    collections = [c for c in bpy.data.collections if c.asset_data]
    assert len(collections) == 1 and all(o.name in collections[0].objects for o in bpy.context.scene.objects if o.type in ['MESH', 'EMPTY'])
    native_structure = structure()
    views = ['front-quarter', 'top', 'lobe-detail']
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
    report = dict(issue=185, model='lazzaro-research', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=retained,
                  maximum_native_imported_position_error=error, native_structure=native_structure,
                  imported_structure=imported_structure, renders=renders,
                  acceptance='Verified source-bound static body refinement; final artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('LAZZARO_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
