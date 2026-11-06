"""Reopen both formats, preserve body geometry and check actual tapered crown arms."""
import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_crowns import CASES, ROOT, VIEWS, fit_camera, folders, sha, source


def snapshot():
    deps = bpy.context.evaluated_depsgraph_get()
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        points = sorted(set(tuple(round(v, 6) for v in obj.matrix_world@vertex.co)
                            for vertex in mesh.vertices))
        assert all(math.isfinite(v) for p in points for v in p), obj.name
        result[obj.name] = dict(points=points, materials=sorted({mesh.materials[p.material_index].name for p in mesh.polygons}),
                                parent=obj.parent.name if obj.parent else None)
        evaluated.to_mesh_clear()
    return result


def drift(a, b):
    assert len(a) == len(b), ('Geometric vertex count changed', len(a), len(b))
    tree = KDTree(len(b))
    for index, p in enumerate(b):
        tree.insert(p, index)
    tree.balance()
    return max(tree.find(p)[2] for p in a)


def form(key):
    _, _, centre, height, spread = CASES[key]
    root = bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i == j else 0))
               for i in range(4) for j in range(4)) < 1e-6, 'Placement root changed'
    stats = {}
    for side, sign in [('left', -1), ('right', 1)]:
        obj = bpy.data.objects[key.upper()+' refined crown arm '+side]
        assert obj.parent == root and len(obj.data.uv_layers), obj.name
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        # GLB legitimately splits vertices at UV/normal seams. Validate the
        # welded physical surface in both formats, retaining all actual faces.
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(edge.is_manifold for edge in bm.edges), (obj.name, 'Open arm topology')
        volume = bm.calc_volume(signed=True)
        assert volume > 0, (obj.name, 'Inverted or empty arm', volume)
        bm.free()
        points = [obj.matrix_world@v.co for v in obj.data.vertices]
        # Sample the real evaluated solid at its broad middle and narrow tip.
        widths = []
        for z in [.41, .80]:
            layer = [sign*(p.x-centre[0]) for p in points
                     if abs(p.z-(centre[2]+z*height)) < height*.008]
            assert len(layer) >= 4, (obj.name, 'Missing actual cross-section', z)
            widths.append(max(layer)-min(layer))
        assert widths[0] > spread*.40, ('Crown regressed to thin wire', widths)
        assert widths[0]/widths[1] > 2.6, ('Untapered prong', widths)
        # Root penetrates the existing seating region while upper arms stay
        # laterally clear of the original middle stem, rather than a solid fan.
        upper = [sign*(p.x-centre[0]) for p in points if p.z > centre[2]+height*.56]
        assert min(upper) > spread*.56, (obj.name, 'Upper fork interval closed')
        assert min(p.z for p in points) <= centre[2]+height*.005
        stats[side] = dict(volume=volume, middle_width=widths[0], tip_width=widths[1],
                           taper_ratio=widths[0]/widths[1], minimum_upper_gap=min(upper))
    assert not any('crown outer conductor' in o.name or 'crown side terminal' in o.name
                   for o in bpy.context.scene.objects), 'Thin wire assembly retained'
    assert not any(o.animation_data for o in bpy.context.scene.objects), 'Invented motion'
    return stats


def pixels(path):
    image = bpy.data.images.load(str(path), check_existing=False)
    data = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(data)
    array = data.reshape((image.size[1], image.size[0], 4)).copy()
    bpy.data.images.remove(image)
    return array


def compare_render(native, imported, whole):
    a, b = pixels(native), pixels(imported)
    assert a.shape == b.shape == (768, 768, 4)
    foreground_a, foreground_b = a[:, :, 3] > .5, b[:, :, 3] > .5
    union = foreground_a | foreground_b
    intersection = foreground_a & foreground_b
    overlap = int(intersection.sum())/int(union.sum())
    difference = float(np.abs(a[intersection, :3]-b[intersection, :3]).mean()*255)
    assert overlap > .995 and difference < 2.0, (native, overlap, difference)
    if whole:
        ys, xs = np.where(union)
        assert min(xs.min(), ys.min(), 767-xs.max(), 767-ys.max()) > 20, 'Clipped whole model'
    return dict(silhouette_iou=overlap, foreground_rgb_mean_difference_255=difference,
                native_sha256=sha(native), imported_sha256=sha(imported))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=CASES, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    key = args.model
    output, media = folders(key)
    meta = json.loads((output/'model.json').read_text())
    assert meta['blend_sha256'] == sha(output/'model.blend')
    assert meta['glb_sha256'] == sha(output/'model.glb')
    assert meta['source_blend_sha256'] == sha(source(key))
    bpy.ops.wm.open_mainfile(filepath=str(source(key)))
    original = snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native = snapshot()
    native_form = form(key)
    preserved = set(original)-set(meta['removed_objects'])
    assert set(native) == preserved | set(meta['added_objects']), 'Unexpected geometry population'
    preservation_error = 0
    for name in preserved:
        preservation_error = max(preservation_error, drift(original[name]['points'], native[name]['points']))
        assert native[name]['materials'] == original[name]['materials'], (name, 'Body material changed')
        assert native[name]['parent'] == original[name]['parent'], (name, 'Body hierarchy changed')
    assert preservation_error < 1e-6, 'Existing body moved or changed'
    native_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for view in ['front-quarter', 'crown-detail']:
        selected = [o for o in native_meshes if 'crown' in o.name.lower()] if view == 'crown-detail' else native_meshes
        fit_camera(VIEWS[view], selected)
        bpy.context.scene.render.filepath = str(media/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
    imported = snapshot()
    imported_form = form(key)
    assert native.keys() == imported.keys(), 'GLB objects differ'
    error = 0
    for name in native:
        error = max(error, drift(native[name]['points'], imported[name]['points']),
                    drift(imported[name]['points'], native[name]['points']))
        assert native[name]['materials'] == imported[name]['materials'], (name, 'GLB material binding changed', native[name]['materials'], imported[name]['materials'])
        assert native[name]['parent'] == imported[name]['parent'], (name, 'GLB hierarchy changed')
    assert error < 1e-4, ('GLB geometry drift', error)
    renders = {}
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for view in ['front-quarter', 'crown-detail']:
        selected = [o for o in meshes if 'crown' in o.name.lower()] if view == 'crown-detail' else meshes
        fit_camera(VIEWS[view], selected)
        target = media/('imported-'+view+'.png')
        bpy.context.scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        renders[view] = compare_render(media/(view+'.png'), target, view != 'crown-detail')
    report = dict(issue=185, model=key, blender=bpy.app.version_string,
                  blend_sha256=sha(output/'model.blend'), glb_sha256=sha(output/'model.glb'),
                  source_blend_sha256=sha(source(key)), verifier_sha256=sha(Path(__file__)),
                  generator_sha256=sha(Path(__file__).with_name('refine_rigellian_crowns.py')),
                  native_mesh_count=len(native), imported_mesh_count=len(imported),
                  preserved_body_objects=len(preserved), preserved_body_position_error=preservation_error,
                  maximum_native_imported_position_error=error, native_form=native_form,
                  imported_form=imported_form, renders=renders,
                  acceptance='Native/imported technical checks and actual renders; final artistic acceptance open')
    (media/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('RIGELLIAN_CROWN_NATIVE_GLB_VERIFIED', key, len(native), error, flush=True)


if __name__ == '__main__':
    main()
