"""Source-bound shared-core, socket, geometry and real construction-motion audit."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_federal_transporter import frame
from refine_ps7c_details import refine_point, XY_REFINEMENT, MAST_SHIFT


def snapshot(objects, require_uv=True):
    result = {}
    for obj in objects:
        if obj.type != 'MESH':
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(edge.is_manifold for edge in bm.edges), (obj.name, 'open edge')
        assert abs(bm.calc_volume()) > 1e-10, (obj.name, 'zero volume')
        bm.free()
        if require_uv:
            assert obj.data.uv_layers, (obj.name, 'missing portable UVs')
        result[obj.name] = dict(points=[obj.matrix_world@v.co for v in obj.data.vertices],
                                matrix=[list(row) for row in obj.matrix_world],
                                materials=[m.name for m in obj.data.materials])
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def drift(a, b):
    tree = KDTree(len(a))
    for i, p in enumerate(a):
        tree.insert(p, i)
    tree.balance()
    return max(tree.find(p)[2] for p in b)


def sockets():
    return {o.name: [list(row) for row in o.matrix_world]
            for o in bpy.context.scene.objects if o.name.startswith('Equipment ')}


def portable_materials():
    found = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        for mat in obj.data.materials:
            if not mat.name.startswith('PS7C ') or mat.name in ['PS7C light', 'PS7C white']:
                continue
            shader = mat.node_tree.nodes.get('Principled BSDF')
            assert shader.inputs['Normal'].is_linked and shader.inputs['Roughness'].is_linked
            assert shader.inputs['Metallic'].is_linked
            found[mat.name] = dict(normal_map=True, roughness_map=True, metallic_map=True)
    assert len(found) == 6, found
    return found


def poses(scene, construction):
    result = {}
    for sample in ([1, 31, 61, 91, 121, 151, 181] if construction else [1]):
        scene.frame_set(sample)
        bpy.context.view_layer.update()
        result[sample] = {o.name: [list(row) for row in o.matrix_world]
                         for o in scene.objects if o.type in ['MESH', 'EMPTY']}
    scene.frame_set(1)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--variant', choices=['refined', 'construction'], required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root, variant = args.root.resolve(), args.variant
    sys.path.insert(0, str(root/'tools'))
    from publication_support import clean_png
    from gallery_animation_assets import glb_clips
    folder = root/'sources/objects/terran/space-dock'/variant
    media = root/'gallery/media/objects/terran/space-dock'/variant
    meta = json.loads((folder/'model.json').read_text())
    source = root/meta['source']
    assert sha(source) == meta['source_sha256']
    before = {p.name: sha(p) for p in folder.glob('model.*')}
    for suffix in ['blend', 'glb']:
        assert before['model.'+suffix] == meta[suffix+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    previous = snapshot(bpy.context.scene.objects, require_uv=False)
    expected_sockets = sockets()
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    native = snapshot(scene.objects)
    native_sockets = sockets()
    if variant == 'refined':
        for name, matrix in expected_sockets.items():
            matrix[0][3] *= XY_REFINEMENT
            matrix[1][3] *= XY_REFINEMENT
            if name == 'Equipment crown':
                matrix[2][3] -= MAST_SHIFT
    assert len(native_sockets) == len(expected_sockets) == 4
    assert max(abs(a-b) for name in native_sockets for ra, rb in zip(native_sockets[name], expected_sockets[name])
               for a, b in zip(ra, rb)) < 1e-6
    assert len(native) == meta['meshes']
    retained = meta['retained_source_parts']
    for name in retained:
        assert len(native[name]['points']) == len(previous[name]['points'])
        if variant == 'construction':
            assert native[name]['matrix'] == previous[name]['matrix'], (name, 'core pose changed')
            error = max((a-b).length for a, b in zip(native[name]['points'], previous[name]['points']))
        else:
            error = max((a-refine_point(name, b)).length for a, b in zip(native[name]['points'], previous[name]['points']))
        assert error < 1e-6, (name, error)
    native_poses = poses(scene, variant == 'construction')
    images = [im for im in bpy.data.images if im.type == 'IMAGE']
    assert len(images) >= 6 and all(im.packed_file for im in images), 'Missing portable maps'
    native_materials = portable_materials()
    mesh_objects = [o for o in scene.objects if o.type == 'MESH']
    frame(scene, mesh_objects, (5, -13, 6))
    scene.render.filepath = str(media/'verified-native.png')
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x = scene.render.resolution_y = 1024
    if variant == 'refined':
        selected = [o for o in mesh_objects if 'service' in o.name.lower() and 'lower service slot' not in o.name]
        # All four assemblies stay in the same frame; the front assembly is also cropped in review.
        frame(scene, selected, (2, -14, 5))
        scene.render.filepath = str(media/'service-detail.png')
        bpy.ops.render.render(write_still=True)
    frame(scene, mesh_objects, (5, -13, 6))
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material, do_unlink=True)
    for image in list(bpy.data.images):
        if image.users == 0:
            bpy.data.images.remove(image)
    bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
    scene.frame_set(1)
    bpy.context.view_layer.update()
    imported = snapshot(scene.objects)
    assert portable_materials() == native_materials
    assert native.keys() == imported.keys()
    error = 0
    for name, data in native.items():
        other = imported[name]
        assert data['materials'] == other['materials'], (name, 'material identity changed')
        error = max(error, drift(data['points'], other['points']), drift(other['points'], data['points']))
    assert error < 5e-6, error
    imported_sockets = sockets()
    assert imported_sockets.keys() == native_sockets.keys()
    socket_error = max(abs(a-b) for name in native_sockets for ra, rb in zip(native_sockets[name], imported_sockets[name])
                       for a, b in zip(ra, rb))
    assert socket_error < 5e-6
    imported_poses = poses(scene, variant == 'construction')
    matrix_error = 0
    for sample, objects in native_poses.items():
        for name, matrix in objects.items():
            other = imported_poses[sample][name]
            matrix_error = max(matrix_error, max(abs(a-b) for ra, rb in zip(matrix, other) for a, b in zip(ra, rb)))
    assert matrix_error < 5e-5, matrix_error
    moving = [name for name in native_poses[1] if any(native_poses[f][name] != native_poses[1][name] for f in native_poses)]
    clips = glb_clips(folder/'model.glb')
    if variant == 'construction':
        assert len(clips) == 1 and clips[0]['name'] == 'ConstructionActivity'
        assert abs(clips[0]['duration']-6) < 1e-5
        assert set(moving) == {'ConstructionWorkCarriage'} | {n for n in native if n.startswith('Space Dock construction carriage ')}
        span = max(native_poses[f]['ConstructionWorkCarriage'][0][3] for f in native_poses)-min(native_poses[f]['ConstructionWorkCarriage'][0][3] for f in native_poses)
        assert abs(span-.28*XY_REFINEMENT) < 1e-5, span
    else:
        assert not clips and not moving
    scene.render.filepath = str(media/'verified-imported.png')
    bpy.ops.render.render(write_still=True)
    for path in media.glob('*.png'):
        path.write_bytes(clean_png(path.read_bytes()))
    assert before == {p.name: sha(p) for p in folder.glob('model.*')}
    report = dict(issue=216, id='openfa:space-dock', variant=variant,
                  blend_sha256=before['model.blend'], glb_sha256=before['model.glb'], source_sha256=sha(source),
                  generator_sha256=meta['generator_sha256'], verifier_sha256=sha(Path(__file__)),
                  helper_sha256=sha(Path(__file__).with_name('verify_federal_transporter.py')),
                  closed_nonzero_meshes=len(native), preserved_core_geometry_parts=len(retained),
                  maximum_world_position_error=error, maximum_socket_matrix_error=socket_error,
                  maximum_animation_matrix_error=matrix_error, samples=list(native_poses),
                  moving_objects=moving, clips=clips, packed_images=len(images),
                  portable_materials=native_materials,
                  source_unchanged=True, renders={p.name: sha(p) for p in media.glob('*.png')},
                  scope='Fresh native reopen and independent GLB import; actual game-client integration remains separate')
    (folder/'runtime-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PS7C_DETAIL_VERIFIED', variant, len(native), error, matrix_error, flush=True)


if __name__ == '__main__':
    main()
