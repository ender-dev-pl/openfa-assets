"""Verify RI10 source preservation, both clips and actual imported descriptor poses."""
import json
from pathlib import Path
import struct
import sys
import bpy
import bmesh
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).parent))
from remaster_rigellian_ground_deck import ROOT, FOLDER, MEDIA, CYCLE, STATES, TARGETS, select_clip, sha, strip_png
from rigellian_shaft_preview import asset_meshes, surface_points, ground_mask
from verify_rigellian_ground_deck import inspect, texture_evidence, tree, moving, clear_shaft, indicator_visibility
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values
from catalogue_rendering import fit_camera


def geometry():
    result = {}
    deps = bpy.context.evaluated_depsgraph_get()
    for obj in asset_meshes(bpy.context.scene):
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        result[obj.name] = dict(points=points, triangles=len(mesh.loop_triangles),
                               materials=sorted({mesh.materials[p.material_index].name for p in mesh.polygons}),
                               tree=BVHTree.FromPolygons(points, [tuple(p.vertices) for p in mesh.polygons]))
        evaluated.to_mesh_clear()
    return result


def compare(a, b):
    assert a.keys() == b.keys()
    error = 0.0
    for name, item in a.items():
        other = b[name]
        assert item['triangles'] == other['triangles'] and item['materials'] == other['materials'], name
        error = max(error, max(other['tree'].find_nearest(p)[3] for p in item['points']),
                    max(item['tree'].find_nearest(p)[3] for p in other['points']))
    assert error < 1e-5, error
    return error


def descriptor_pose(meshes, descriptor, strip_offset):
    assert abs(strip_offset-round(strip_offset)) < 1e-5
    select_clip(STATES, descriptor-int(round(strip_offset)))
    check_meshes(meshes, allow_packed_images=True)
    movers = [o for o in meshes if moving(o)]
    fixed = [o for o in meshes if not moving(o)]
    shapes = {o.name: tree(o) for o in meshes}
    for obj in movers:
        for other in fixed:
            assert not shapes[obj.name].overlap(shapes[other.name]), (descriptor, obj.name, other.name)
    for index, obj in enumerate(movers):
        for other in movers[index+1:]:
            if obj.parent != other.parent:
                assert not shapes[obj.name].overlap(shapes[other.name]), (descriptor, obj.name, other.name)
    assert len(movers) == 8 and all(tuple(o.scale) == (1, 1, 1) for o in meshes)
    if descriptor in [2, 15]:
        indicator_visibility(meshes, descriptor == 15)
    if descriptor >= 15:
        clear_shaft(meshes)
    return {o.name: [float(v) for row in o.matrix_world for v in row] for o in meshes}


def render(label, direction, meshes):
    ground_mask()
    fit_camera(bpy.context.scene, surface_points(meshes), direction)
    path = MEDIA / (label+'.png')
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    strip_png(path)
    return sha(path)


def validate(label, metadata):
    scene = bpy.context.scene
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    meshes = asset_meshes(scene)
    assert len(meshes) == 45
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges), obj.name
            assert bm.calc_volume(signed=True) > 0, obj.name
        finally:
            bm.free()
    # Blender's GLB importer places each NLA strip at frame one even when
    # glTF input times begin at frame two. Sample its existing strip using
    # the measured action/strip offset; do not alter keys or the GLB payload.
    offsets = []
    for name in TARGETS:
        strip = bpy.data.objects[name].animation_data.nla_tracks[STATES].strips[0]
        assert abs(strip.action_frame_start-2) < 1e-5 and abs(strip.action_frame_end-17) < 1e-5
        offsets.append(strip.action_frame_start-strip.frame_start)
    assert max(offsets)-min(offsets) < 1e-5
    strip_offset = offsets[0]
    select_clip(CYCLE, 1)
    snapshots, sweep = inspect(meshes)
    pixels = texture_evidence(meshes)
    materials = material_values(meshes)
    select_clip(CYCLE, 1)
    shapes = geometry()
    bounds = geometry_bounds(meshes)
    descriptors = {}
    renders = {}
    prefix = label+'-'
    for name, frame, direction in [('front-quarter', 1, (6, -13, 8)), ('front', 1, (0, -16, 7)),
                                   ('rear-quarter', 1, (-7, 12, 7)), ('half-open', 16, (0, -16, 7)),
                                   ('open', 31, (0, -16, 7)), ('open-top', 31, (0, 0, 20))]:
        select_clip(CYCLE, frame)
        renders[prefix+name+'.png'] = render(prefix+name, direction, meshes)
    for state in metadata['states']:
        descriptor = state['descriptor']
        descriptors[str(descriptor)] = descriptor_pose(meshes, descriptor, strip_offset)
        if descriptor <= 15:
            name = prefix+f'descriptor-{descriptor:02}'
            renders[name+'.png'] = render(name, (0, -16, 7), meshes)
    return dict(positive_closed_meshes=len(meshes), sweep=sweep, descriptors=descriptors,
                snapshots=snapshots, pixels=pixels, materials=materials, geometry=shapes,
                bounds=bounds, renders=renders, descriptor_strip_offset=strip_offset)


def main():
    meta = json.loads((FOLDER / 'model.json').read_bytes())
    case = json.loads((FOLDER / 'recipe.json').read_bytes())
    assert sha(ROOT / meta['source']) == meta['source_sha256']
    assert meta['author_sha256'] == sha(Path(__file__).with_name('remaster_rigellian_ground_deck.py'))
    assert meta['recipe_sha256'] == sha(FOLDER / 'recipe.json')
    for kind, digest in meta['binaries'].items():
        assert sha(FOLDER / ('model.'+kind)) == digest
    raw = (FOLDER / 'model.glb').read_bytes()
    size = struct.unpack_from('<I', raw, 12)[0]
    document = json.loads(raw[20:20+size])
    clips = {clip['name']: clip for clip in document['animations']}
    assert set(clips) == {CYCLE, STATES}
    assert len(document['meshes']) == 45
    for name, clip in clips.items():
        assert len(clip['channels']) == 6
        assert {document['nodes'][c['target']['node']]['name'] for c in clip['channels']} == set(TARGETS)
        assert all(c['target']['path'] == 'translation' for c in clip['channels'])
        if name == STATES:
            assert all(s['interpolation'] == 'STEP' for s in clip['samplers'])
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / meta['source']), load_ui=False, use_scripts=False)
    bpy.context.scene.frame_set(1)
    original = geometry()
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER / 'model.blend'), load_ui=False, use_scripts=False)
    select_clip(CYCLE, 1)
    preserved = compare(original, geometry())
    native = validate('native', meta)
    scene = bpy.context.scene
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER / 'model.glb'))
    imported = validate('imported', meta)
    error = compare(native['geometry'], imported['geometry'])
    for label, snapshot in [('native',native['geometry']),('imported',imported['geometry'])]:
        assert sum(part['triangles'] for part in snapshot.values())==meta['triangles'],label
    raw_export_triangles = sum(document['accessors'][primitive['indices']]['count']//3
        for mesh in document['meshes'] for primitive in mesh['primitives'])
    assert raw_export_triangles==meta['triangles']

    assert native['pixels'] == imported['pixels']
    assert native['materials'].keys() == imported['materials'].keys()
    for name, value in native['materials'].items():
        other = imported['materials'][name]
        assert max(abs(a-b) for a, b in zip(value[0]+value[1:], other[0]+other[1:])) < 1/255+.00001
    matrix_error = 0.0
    for key in ['snapshots', 'descriptors']:
        for frame, objects in native[key].items():
            for name, matrix in objects.items():
                matrix_error = max(matrix_error, max(abs(a-b) for a, b in zip(matrix, imported[key][frame][name])))
    assert matrix_error < .00003, matrix_error
    helpers = {Path(module.__file__).relative_to(ROOT).as_posix(): sha(Path(module.__file__))
               for module in list(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().is_relative_to(Path(__file__).parent.resolve())}
    report = dict(issue=253, id=meta['id'], blender=bpy.app.version_string,
                  binaries=meta['binaries'], metadata_sha256=sha(FOLDER / 'model.json'),
                  verifier_sha256=sha(Path(__file__)), helpers=helpers,
                  native=dict(positive_closed_meshes=45, sweep=native['sweep']),
                  imported=dict(positive_closed_meshes=45, sweep=imported['sweep']),
                  maximum_bidirectional_surface_error=error, protected_surface_error=preserved,
                  maximum_animation_matrix_error=matrix_error, triangles=meta['triangles'], meshes=45,
                  native_world_bounds=native['bounds'],
                  native_root_matrix=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
                  imported_root_matrix=[float(v) for row in bpy.data.objects['PlacementRoot'].matrix_world for v in row],
                  material_count=len(document['materials']), embedded_images=sum('bufferView' in i for i in document['images']),
                  clips=sorted(clips), descriptor_domain=list(range(2,18)),
                  animation_validation=dict(cycle_integer_frames=61, descriptor_poses=16, channels_per_clip=6,
                                            translation_only=True, descriptor_step=True, duplicate_state_meshes=False,
                                            continuous_sweep_proven=False, descriptor17_composition_verified=False),
                  descriptor_strip_offsets=dict(native=native['descriptor_strip_offset'], imported=imported['descriptor_strip_offset']),
                  renders={**native['renders'], **imported['renders']},
                  final_artistic_acceptance=False, game_client_integration=False)
    (FOLDER / 'runtime-review.json').write_bytes((json.dumps(report, indent=2)+'\n').encode())
    print('RI10_CANONICAL_BOTH_CLIPS_NATIVE_GLB_VERIFIED', error, matrix_error, flush=True)


if __name__ == '__main__':
    main()
