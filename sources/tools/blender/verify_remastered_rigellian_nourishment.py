"""Actual RI03 saved-native/imported GLB anatomy and render validation."""
import json
from pathlib import Path
import sys
import struct

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).parent))
from remaster_rigellian_nourishment import ROOT, SOURCE, OUTPUT, MEDIA, sha, strip_png, fit_camera
from verify_refined_rigellian_nourishment import structure


def snapshot():
    result = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.polygons]
        result[obj.name] = dict(points=points, tree=BVHTree.FromPolygons(points, faces),
                                triangles=len(mesh.loop_triangles),
                                materials=sorted({obj.data.materials[p.material_index].name
                                                  for p in mesh.polygons}))
        evaluated.to_mesh_clear()
    return result


def main():
    meta = json.loads((OUTPUT / 'model.json').read_bytes())
    assert meta['author_sha256'] == sha(Path(__file__).with_name('remaster_rigellian_nourishment.py'))
    assert meta['source_sha256'] == sha(SOURCE)
    for ext, digest in meta['binaries'].items():
        assert sha(OUTPUT / ('model.' + ext)) == digest
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT / 'model.blend'), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    scene.frame_set(1)
    native_form = structure()
    native = snapshot()
    native_root = [float(v) for row in bpy.data.objects['PlacementRoot'].matrix_world for v in row]
    all_points = [p for row in native.values() for p in row['points']]
    bounds = [min(p[a] for p in all_points) for a in range(3)] + [max(p[a] for p in all_points) for a in range(3)]
    assert sum(row['triangles'] for row in native.values()) == meta['triangles']
    renders = {}
    views = [('front-quarter', (6, -13, 8)), ('front', (0, -16, 4)), ('rear-quarter', (-7, 12, 7))]
    for name, direction in views:
        fit_camera(direction, [o for o in scene.objects if o.type == 'MESH'])
        path = MEDIA / ('native-' + name + '.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
        renders[path.name] = sha(path)
    for obj in list(scene.objects):
        if obj.type not in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT / 'model.glb'))
    imported_form = structure()
    imported = snapshot()
    imported_root = [float(v) for row in bpy.data.objects['PlacementRoot'].matrix_world for v in row]
    assert max(abs(a-b) for a,b in zip(native_root, imported_root)) < 1e-6
    assert native.keys() == imported.keys()
    error = 0.0
    for name, row in native.items():
        other = imported[name]
        assert row['materials'] == other['materials'], (name, row['materials'], other['materials'])
        assert row['triangles'] == other['triangles']
        error = max(error, max(other['tree'].find_nearest(p)[3] for p in row['points']),
                    max(row['tree'].find_nearest(p)[3] for p in other['points']))
    assert error < 1e-5
    for name, direction in views:
        fit_camera(direction, [o for o in scene.objects if o.type == 'MESH'])
        path = MEDIA / ('imported-' + name + '.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
        renders[path.name] = sha(path)
    for ext, digest in meta['binaries'].items():
        assert sha(OUTPUT / ('model.' + ext)) == digest
    assert sha(SOURCE) == meta['source_sha256']
    helpers = {Path(module.__file__).relative_to(ROOT).as_posix(): sha(Path(module.__file__))
               for module in list(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().is_relative_to(Path(__file__).parent.resolve())}
    raw = (OUTPUT / 'model.glb').read_bytes()
    gltf = json.loads(raw[20:20 + struct.unpack_from('<I', raw, 12)[0]])
    assert not gltf.get('animations')
    report = dict(issue=253, id=meta['id'], blender=bpy.app.version_string,
                  binaries=meta['binaries'], metadata_sha256=sha(OUTPUT / 'model.json'),
                  verifier_sha256=sha(Path(__file__)), helpers=helpers,
                  native=native_form, imported=imported_form,
                  maximum_bidirectional_surface_error=error, renders=renders,
                  triangles=meta['triangles'], meshes=len(native),
                  native_world_bounds=bounds, native_root_matrix=native_root,
                  imported_root_matrix=imported_root,
                  material_count=len(gltf.get('materials', [])),
                  embedded_images=sum('bufferView' in image for image in gltf.get('images', [])),
                  clips=[],
                  final_artistic_acceptance=False, game_client_integration=False)
    (OUTPUT / 'runtime-review.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('RI03_REMASTER_NATIVE_GLB_VERIFIED', len(native), meta['triangles'], error, flush=True)


if __name__ == '__main__':
    main()
