"""Check RI03's visible equipment, retained body proportions and independent GLB renders."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_nourishment import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, MODULE_STARTS, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render


def ray(obj, x, z):
    tree = BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [list(p.vertices) for p in obj.data.polygons])
    hit = tree.ray_cast(Vector((x, -2, z)), Vector((0, 1, 0)), 4)[0]
    assert hit is not None, (obj.name, x, z)
    return hit


def structure():
    root = bpy.data.objects['PlacementRoot']
    assert root['catalogue_id'] == 'openfa:building/legacy/042'
    assert root['footprint_width'] == root['footprint_height'] == 2
    assert max(abs(root.matrix_world[i][j]-(1 if i == j else 0)) for i in range(4) for j in range(4)) < 1e-6
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for obj in meshes:
        assert obj.parent == root, (obj.name, 'Detached from placement root')
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(e.is_manifold for e in bm.edges), (obj.name, 'Open physical surface')
        assert bm.calc_volume(signed=True) > 0, (obj.name, 'Inverted or zero volume')
        bm.free()
    stack = []
    for i, start in enumerate(MODULE_STARTS):
        body = bpy.data.objects[f'RI03 renewed process vessel {i}']
        points = [body.matrix_world@v.co for v in body.data.vertices]
        width = max(p.x for p in points)-min(p.x for p in points)
        height = max(p.z for p in points)-min(p.z for p in points)
        assert abs(width-.98) < .0001 and abs(height-.90) < .0001, ('Established vessel proportions changed', i, width, height)
        frame = bpy.data.objects[f'RI03 broad pale service frame {i}']
        coords = [frame.matrix_world@v.co for v in frame.data.vertices]
        frame_width = max(p.x for p in coords)-min(p.x for p in coords)
        assert .395 < frame_width < .405, ('Broad pale equipment regressed to tiny trim', i, frame_width)
        clearances = []
        for x, z in [(.08, .75), (.08, .15), (-.075, .45), (.235, .45)]:
            frame_front = ray(frame, x, start+z)
            casing_front = ray(body, x, start+z)
            clearances.append(casing_front.y-frame_front.y)
        assert min(clearances) > .018, ('Casing cuts through the visible equipment frame', i, clearances)
        centre = ray(body, .08, start+.45)
        shoulder = ray(body, -.25, start+.45)
        backing = bpy.data.objects[f'RI03 broad service recess backing {i}']
        back = ray(backing, .08, start+.45)
        assert centre.y-shoulder.y > .07, ('Actual service recess missing', centre.y, shoulder.y)
        assert shoulder.y < back.y < centre.y, ('Backing is not recessed in the casing', shoulder.y, back.y, centre.y)
        # Backing rear face extends past the actual carved floor into solid
        # material; its visible face remains in front of that floor.
        bounds = [backing.matrix_world@v.co for v in backing.data.vertices]
        assert max(p.y for p in bounds) > centre.y+.01, 'Backing floats off casing root'
        insert = bpy.data.objects[f'RI03 pale recessed upright insert {i}']
        insert_points = [insert.matrix_world@v.co for v in insert.data.vertices]
        assert min(p.y for p in insert_points) > shoulder.y, 'Inset equipment protrudes beyond body face'
        stack.append(dict(vessel_width=width, vessel_height=height, pale_frame_width=frame_width,
                          minimum_frame_front_clearance=min(clearances),
                          body_front_y=shoulder.y, cavity_floor_y=centre.y, backing_face_y=back.y))
    spine = bpy.data.objects['RI03 continuous flat equipment spine']
    points = [spine.matrix_world@v.co for v in spine.data.vertices]
    width, height = max(p.x for p in points)-min(p.x for p in points), max(p.z for p in points)-min(p.z for p in points)
    assert width > .09 and height > 3.8, 'Broad continuous vertical equipment spine lost'
    assert len([o for o in meshes if o.name.startswith('RI03 interstage spine bridge')]) == 3
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Invented process animation'
    return dict(positive_closed_meshes=len(meshes), stack=stack, spine_width=width, spine_height=height,
                three_interstage_spine_bridges=True)


def select_view(view):
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if view == 'service-detail':
        return [o for o in meshes if any(w in o.name for w in ['frame 1', 'insert 1', 'backing 1'])]
    return meshes


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    for kind in ['blend', 'glb']:
        assert meta[kind+'_sha256'] == sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_nourishment.py'))
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    for name, digest in meta['dependencies_sha256'].items():
        assert digest == sha(Path(__file__).with_name(name))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    previous = snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    preserved_error = 0
    for name in meta['preserved_objects']:
        preserved_error = max(preserved_error, drift(previous[name]['points'], native[name]['points']))
        assert previous[name]['materials'] == native[name]['materials'] and previous[name]['parent'] == native[name]['parent']
    assert preserved_error < 1e-6, 'Retained foundation/interstage geometry changed'
    assert set(native) == set(meta['preserved_objects']) | set(meta['added_objects'])
    native_form = structure()
    views = ['front-quarter', 'front', 'service-detail']
    for view in views:
        fit_camera(VIEWS[view], select_view(view))
        bpy.context.scene.render.filepath = str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'))
    imported = snapshot()
    imported_form = structure()
    assert native.keys() == imported.keys()
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']), drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'], (name, 'Material binding changed')
        assert native[name]['parent'] == imported[name]['parent'], (name, 'Parent changed')
    assert error < 1e-4, error
    renders = {}
    for view in views:
        fit_camera(VIEWS[view], select_view(view))
        path = MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(MEDIA/(view+'.png'), path, view != 'service-detail')
    report = dict(issue=185, model='ri03', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  dependencies_sha256=meta['dependencies_sha256'], lore_sha256=meta['lore_sha256'],
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(meta['preserved_objects']), preserved_body_position_error=preserved_error,
                  maximum_native_imported_position_error=error, native_structure=native_form,
                  imported_structure=imported_form, renders=renders,
                  acceptance='Verified visible equipment refinement; user artistic acceptance and calibrated gameplay integration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RI03_VISIBLE_EQUIPMENT_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
