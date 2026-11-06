"""Fresh native reopen and independent GLB geometry/material/render verification."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(objects):
    result = {}
    for obj in objects:
        if obj.type != 'MESH':
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
        assert all(e.is_manifold for e in bm.edges), (obj.name, 'open/nonmanifold edge')
        assert abs(bm.calc_volume()) > 1e-10, (obj.name, 'zero-volume part')
        bm.free()
        assert obj.data.uv_layers, (obj.name, 'missing UVs')
        result[obj.name] = dict(points=[obj.matrix_world@v.co for v in obj.data.vertices],
                                materials=[m.name for m in obj.data.materials],
                                matrix=[list(r) for r in obj.matrix_world])
    return result


def exhaust_visibility(scene):
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    for z in [-.50, .07, .64]:
        hit, _, _, _, obj, _ = scene.ray_cast(graph, Vector((-8, 0, z)), Vector((1, 0, 0)))
        assert hit and obj.name == f'Engine red pilot {z}', (z, 'exhaust hidden', obj.name if hit else None)
    return 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root = args.root.resolve()
    sys.path.insert(0, str(root/'tools'))
    from publication_support import clean_png
    source = root/'sources/objects/shared/federal-transporter/refined'
    media = root/'gallery/media/objects/shared/federal-transporter/refined'
    script = root/'sources/tools/blender/build_federal_transporter.py'
    spec = importlib.util.spec_from_file_location('federal_authoring', script)
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    meta = json.loads((source/'model.json').read_text())
    before = {p.name: sha(p) for p in source.glob('model.*')}
    bpy.ops.wm.open_mainfile(filepath=str(source/'model.blend'), load_ui=False, use_scripts=False)
    assert bpy.data.objects['FederalTransporterRoot']['catalogue_id'] == 'openfa:federal-transporter'
    assert tuple(bpy.data.objects['FederalTransporterRoot'].scale) == (1, 1, 1)
    native = snapshot(bpy.context.scene.objects)
    assert exhaust_visibility(bpy.context.scene) == 3
    assert len(native) == meta['meshes']
    assert len([n for n in native if 'pressure hull' in n]) == 4  # 3 cargo + separate flattened stern.
    assert len([n for n in native if 'External truss diagonal' in n]) == 112
    images = {im.name: (list(im.size), sha(Path(bpy.path.abspath(im.filepath))))
              for im in bpy.data.images if im.type == 'IMAGE'}
    assert len(images) == 7 and all(im.packed_file for im in bpy.data.images if im.type == 'IMAGE')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    scene = bpy.context.scene
    author.frame(scene, meshes, (0, -14, 5))
    scene.render.filepath = str(media/'verified-native-side.png')
    bpy.ops.render.render(write_still=True)
    scene.render.resolution_x, scene.render.resolution_y = 1024, 1024
    for name, chosen in [('cargo-detail', [o for o in meshes if o.name.startswith('Cargo 2')]),
                         ('bridge-detail', [o for o in meshes if any(k in o.name.lower() for k in ['prow', 'bridge'])])]:
        author.frame(scene, chosen, (4, -12, 6))
        scene.render.filepath = str(media/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    scene.render.resolution_x, scene.render.resolution_y = 1536, 640
    author.frame(scene, meshes, (0, -14, 5))
    # Preserve the exact studio; completely discard native mesh/material/image data.
    for obj in list(meshes)+[bpy.data.objects['FederalTransporterRoot']]:
        bpy.data.objects.remove(obj, do_unlink=True)
    for data in [bpy.data.meshes, bpy.data.materials, bpy.data.images]:
        for item in list(data):
            if item.users == 0:
                data.remove(item)
    bpy.ops.import_scene.gltf(filepath=str(source/'model.glb'))
    imported = snapshot(scene.objects)
    assert exhaust_visibility(scene) == 3
    assert native.keys() == imported.keys(), (set(native)-set(imported), set(imported)-set(native))
    maximum = 0
    for name, a in native.items():
        b = imported[name]
        assert a['materials'] == b['materials'], (name, 'material mismatch')
        # UV seams split vertices; compare both directions without requiring equal counts.
        for first, second in [(a['points'], b['points']), (b['points'], a['points'])]:
            tree = KDTree(len(first))
            for i, p in enumerate(first):
                tree.insert(p, i)
            tree.balance()
            maximum = max(maximum, max(tree.find(p)[2] for p in second))
    assert maximum < 5e-6, maximum
    maps = [im for im in bpy.data.images if im.type == 'IMAGE']
    assert len(maps) == 7 and all(im.packed_file for im in maps)
    shader_colours = {}
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        tex = [n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE']
        shader_colours[mat.name] = dict(textures=len(tex), metallic=bsdf.inputs['Metallic'].default_value,
                                       roughness=bsdf.inputs['Roughness'].default_value)
    assert len(shader_colours) == 9
    assert sum(r['textures'] for r in shader_colours.values()) == 7
    scene.render.filepath = str(media/'verified-imported-side.png')
    bpy.ops.render.render(write_still=True)
    for path in media.glob('*.png'):
        path.write_bytes(clean_png(path.read_bytes()))
    assert before == {p.name: sha(p) for p in source.glob('model.*')}, 'Verifier modified source'
    report = dict(issue=215, id='openfa:federal-transporter', blender=bpy.app.version_string,
                  blend_sha256=before['model.blend'], glb_sha256=before['model.glb'],
                  generator_sha256=sha(script), verifier_sha256=sha(Path(__file__)),
                  meshes=len(native), closed_nonzero_meshes=len(native), packed_colour_maps=7,
                  visible_exhaust_throats_native=3, visible_exhaust_throats_imported=3,
                  maximum_bidirectional_world_position_error=maximum, materials=shader_colours,
                  source_unchanged=True, renders={p.name: sha(p) for p in media.glob('*.png')},
                  scope='Native Blender reopen and independent portable GLB; client integration pending')
    (source/'runtime-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FEDERAL_TRANSPORTER_VERIFIED', json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
