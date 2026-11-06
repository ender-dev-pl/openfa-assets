"""Validate RI20 visible construction, recessed geometry and native/GLB presentation."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_extractor import ROOT, SOURCE, OUTPUT, MEDIA, VIEWS, COAT, fit_camera, sha
from verify_rigellian_crowns import snapshot, drift, compare_render


def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],
                               [list(p.vertices) for p in obj.data.polygons])


def radial_hit(obj, phi, z, inward=True):
    n = Vector((math.cos(phi), math.sin(phi), 0))
    origin = n*(2 if inward else .02)+Vector((0, 0, z))
    hit = tree(obj).ray_cast(origin, -n if inward else n, 4)[0]
    assert hit is not None, (obj.name, phi, z, 'No surface at structural sample')
    return Vector((hit.x, hit.y, 0)).length


def structure():
    objects = bpy.data.objects
    root = objects['PlacementRoot']
    assert root['catalogue_id'] == 'openfa:building/legacy/059'
    assert root['footprint_width'] == root['footprint_height'] == 2
    assert max(abs(root.matrix_world[i][j]-(1 if i == j else 0)) for i in range(4) for j in range(4)) < 1e-6
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    volumes = {}
    for obj in meshes:
        assert obj.parent == root and len(obj.data.uv_layers), (obj.name, 'Unparented or missing UVs')
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(e.is_manifold for e in bm.edges), (obj.name, 'Open physical surface')
        volume = bm.calc_volume(signed=True)
        assert volume > 0, (obj.name, 'Nonpositive enclosed volume', volume)
        volumes[obj.name] = volume
        bm.free()
    body = objects['RI20 stepped main casing']
    lower = radial_hit(body, math.pi/2, .85)
    upper = radial_hit(body, math.pi/2, 1.45)
    assert lower/upper > 1.25, ('Lower shoulder regressed to a smooth capsule', lower, upper)
    rib_samples = []
    core = objects['RI20 exposed lower mechanism core']
    for i, z in enumerate([.095, .225, .355]):
        rib = objects[f'RI20 lower mechanism broad rib {i}']
        outer = radial_hit(rib, math.pi/2, z)
        inner = radial_hit(core, math.pi/2, z)
        assert outer-inner > .045, ('Lower rib is not a readable separate tier', i, outer, inner)
        rib_samples.append(dict(height=z, outer_radius=outer, core_radius=inner))
    slots = []
    for i, phi in enumerate([-1.23, -.94]):
        floor = radial_hit(body, phi, .82)
        shoulder = radial_hit(body, phi-.16 if i == 0 else phi+.16, .82)
        backing = objects[f'RI20 slot {i} recessed backing']
        face = radial_hit(backing, phi, .82)
        root_radius = radial_hit(backing, phi, .82, inward=False)
        assert shoulder-floor > .075 and shoulder-face > .065, ('Slot is a flat decal', i, floor, shoulder, face)
        assert root_radius < floor-.008, ('Slot backing floats above its casing root', root_radius, floor)
        slots.append(dict(shoulder=shoulder, cavity_floor=floor, backing_face=face, backing_root=root_radius))
    side = objects['RI20 pronounced side equipment pod']
    side_points = [side.matrix_world@v.co for v in side.data.vertices]
    assert min(p.x for p in side_points) < -.71, 'Side pod no longer changes the silhouette'
    assert len([o for o in meshes if o.name.startswith('RI20 lower green inset')]) == 3
    assert len([o for o in meshes if o.name.startswith('RI20 forward gold boss')]) == 3
    assert len([o for o in meshes if o.name.startswith('RI20 exposed upper drum contact')]) == 4
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Unfounded operating loop'
    return dict(lower_to_upper_radius_ratio=lower/upper, lower_ribs=rib_samples,
                recessed_slots=slots, side_pod_min_x=min(p.x for p in side_points),
                positive_closed_meshes=len(volumes), three_green_lower_blocks=True,
                three_front_gold_fittings=True, four_exposed_drum_contacts=True)


def main():
    meta = json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256'] == sha(SOURCE)
    assert meta['blend_sha256'] == sha(OUTPUT/'model.blend')
    assert meta['glb_sha256'] == sha(OUTPUT/'model.glb')
    assert meta['generator_sha256'] == sha(Path(__file__).with_name('refine_rigellian_extractor.py'))
    assert meta['authored_finish_sha256'] == sha(COAT)
    assert meta['lore_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json')
    assert meta['reference_sha256'] == sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json')
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native = snapshot()
    native_form = structure()
    views = ['front-quarter', 'front', 'mechanism-detail']
    for view in views:
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        selected = [o for o in meshes if any(w in o.name for w in ['lower', 'drum', 'slot'])] if view == 'mechanism-detail' else meshes
        fit_camera(VIEWS[view], selected)
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
    assert native.keys() == imported.keys(), 'GLB mesh population changed'
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']), drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'], (name, 'Material assignment changed')
        assert native[name]['parent'] == imported[name]['parent'], (name, 'Parent changed')
    assert error < 1e-4, ('Geometry changed on export', error)
    render_checks = {}
    for view in views:
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        selected = [o for o in meshes if any(w in o.name for w in ['lower', 'drum', 'slot'])] if view == 'mechanism-detail' else meshes
        fit_camera(VIEWS[view], selected)
        path = MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        render_checks[view] = compare_render(MEDIA/(view+'.png'), path, view != 'mechanism-detail')
    report = dict(issue=185, model='ri20', blender=bpy.app.version_string,
                  source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'),
                  glb_sha256=sha(OUTPUT/'model.glb'), verifier_sha256=sha(Path(__file__)),
                  generator_sha256=sha(Path(__file__).with_name('refine_rigellian_extractor.py')),
                  lore_sha256=meta['lore_sha256'], reference_sha256=meta['reference_sha256'],
                  comparison_helper_sha256=sha(Path(__file__).with_name('verify_rigellian_crowns.py')),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  maximum_native_imported_position_error=error, native_structure=native_form,
                  imported_structure=imported_form, renders=render_checks,
                  acceptance='Visible structural refinement independently checked in both formats; user artistic acceptance and game calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RI20_STRUCTURAL_NATIVE_GLB_VERIFIED', len(native), error, flush=True)


if __name__ == '__main__':
    main()
