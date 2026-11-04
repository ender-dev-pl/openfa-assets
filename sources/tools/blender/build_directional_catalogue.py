"""Post-process catalogue recipes into fixed bases and independently rotating heads."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene, material, beam
from build_legacy_buildings import dome
from catalogue_rendering import assemble, evaluated_points, fit_camera
from directional_catalogue_rules import requires_rig


ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/bootstrap-3d/full-catalogue'
RIG_NAME = 'DirectionalHead'
BASE_NAME = 'StaticBase'


def parent_preserving_world(objects, parent):
    bpy.context.view_layer.update()
    for obj in objects:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    bpy.context.view_layer.update()


def create_rig(record, collection):
    meshes = [obj for obj in collection.objects if obj.type == 'MESH']
    weapon = [obj for obj in meshes if obj.name.startswith('Weapon pivot')]
    if weapon:
        pivot = tuple(weapon[0].location)
        moving = [obj for obj in meshes if obj.name.startswith(('Weapon ', 'Turret sloped reflector'))]
        kind = 'weapon head'
    elif record['global_type'] in [31, 33]:
        # Legacy PB31/PB33 carry a small directional defensive cap, not a rotating building.
        z = 3.1 if record['global_type'] == 31 else 3.2
        surface = material('Authored defensive cap', (0.42, 0.25, 0.07), 0.5, 0.4)
        before = set(collection.objects)
        dome('Defensive head cupola', 0.24, 0.18, z - 0.10, surface)
        beam('Defensive head barrel', (0, -0.12, z), (0, -0.64, z + 0.18), 0.055, surface)
        moving = list(set(collection.objects) - before)
        moving += [obj for obj in meshes if obj.name.startswith('Aerial ')]
        pivot, kind = (0, 0, z), 'defensive cap'
    elif record['global_type'] == 61:
        moving = [obj for obj in meshes if obj.name.startswith(('Radial collector panel', 'Rotor pivot'))]
        pivot, kind = (0, 0, 2.2), 'rotor'
    elif record['global_type'] == 106:
        # MK21 is a directional crystal emitter, rather than a conventional barrel turret.
        moving = [obj for obj in meshes if not obj.name.startswith('Foundation ')]
        pivot, kind = (0, 0, 0.15), 'crystal emitter body'
    else:
        raise ValueError(record['preview'])
    all_meshes = [obj for obj in collection.objects if obj.type == 'MESH']
    static = [obj for obj in all_meshes if obj not in moving]
    assert moving and static, record['preview']
    head = bpy.data.objects.new(RIG_NAME, None)
    collection.objects.link(head)
    head.location = pivot
    head.empty_display_type = 'ARROWS'
    head.empty_display_size = 0.4
    head['role'] = 'heading-driven rotating assembly'
    head['axis'] = 'local +Z'
    base = bpy.data.objects.new(BASE_NAME, None)
    collection.objects.link(base)
    base['role'] = 'stationary foundation and housing'
    parent_preserving_world(moving, head)
    parent_preserving_world(static, base)
    return head, base, kind


def animate_head(scene, head):
    scene.frame_start, scene.frame_end = 1, 17
    scene.render.fps = 16
    for frame, angle in [(1, 0), (17, math.tau)]:
        head.rotation_euler.z = angle
        head.keyframe_insert(data_path='rotation_euler', index=2, frame=frame)
    action = head.animation_data.action
    action.name = 'HeadingPreview_360'
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'
    scene.frame_set(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', help='Optional global types for targeted authoring')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    recipes = json.loads((ROOT/'recipes.json').read_text(encoding='utf-8'))['buildings']
    records = [record for record in recipes if requires_rig(record)]
    expected = {record['global_type'] for record in records}
    if args.ids:
        requested = set(map(int, args.ids.split(',')))
        assert requested <= expected
        records = [record for record in records if record['global_type'] in requested]
    signature = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for record in records:
        output = ROOT/record['culture']/record['preview'].lower()
        metadata = json.loads((output/'model.json').read_text(encoding='utf-8'))
        if args.resume and metadata.get('rotation_rig', {}).get('generator_sha256') == signature:
            if all((output/'directions'/f'{index:02}.png').is_file() for index in range(16)):
                print('DIRECTIONAL_CACHED', record['preview'], flush=True)
                continue
        scene = setup_scene(512, 32)
        scene.name = f"{record['global_type']:03} | {record['name']}"
        collection = bpy.data.collections.new(record['preview']+' | '+record['name'])
        scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        assemble(record)
        collection.asset_mark()
        collection.asset_data.description = record['building_id']+'; independent Z-axis heading rig'
        for key in ['building_id', 'global_type', 'footprint']:
            collection[key] = record[key]
        head, base, kind = create_rig(record, collection)
        animate_head(scene, head)
        meshes = [obj for obj in collection.objects if obj.type == 'MESH']
        # Fit every view to the union of all headings: fixed camera, scale and sprite anchor.
        points = []
        for index in range(16):
            scene.frame_set(index+1)
            points.extend(evaluated_points(meshes))
        scene.frame_set(1)
        views = [('front-quarter',(8,-12,10.1)),('rear-quarter',(-8,12,10.1)),('top',(0,0,20))]
        for name, direction in views:
            fit_camera(scene, points, direction)
            scene.render.filepath = str(output/(name+'.png'))
            bpy.ops.render.render(write_still=True)
        fit_camera(scene, points, views[0][1])
        direction_dir = output/'directions'
        direction_dir.mkdir(exist_ok=True)
        for index in range(16):
            scene.frame_set(index+1)
            scene.render.filepath = str(direction_dir/f'{index:02}.png')
            bpy.ops.render.render(write_still=True)
        scene.frame_set(1)
        low, high = fit_camera(scene, evaluated_points(meshes), views[0][1])
        # Restore the fixed all-heading camera after recording neutral-pose bounds.
        fit_camera(scene, points, views[0][1])
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collection.objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = head
        bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'), export_format='GLB',
            use_selection=True, export_apply=True, export_animations=True,
            export_animation_mode='ACTIVE_ACTIONS', export_frame_range=True)
        scene.render.filepath = str(output/'front-quarter.png')
        bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'), compress=True)
        metadata.update(mesh_objects=len(meshes), bounds_min=list(low), bounds_max=list(high))
        metadata['rotation_rig'] = dict(generator_sha256=signature, head=RIG_NAME, base=BASE_NAME,
            kind=kind, pivot=list(head.location), axis='+Z', zero_forward='-Y', positive='counterclockwise',
            moving_meshes=sorted(obj.name for obj in head.children),
            static_meshes=sorted(obj.name for obj in base.children),
            animation='HeadingPreview_360', frame_start=1, frame_end=17,
            direction_count=16, direction_step_degrees=22.5,
            camera_location=list(scene.camera.location), ortho_scale=scene.camera.data.ortho_scale,
            runtime_heading_registration='separate integration step; exported indices are model-local angles')
        (output/'model.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
        print('DIRECTIONAL_MODEL_OK', record['global_type'], record['preview'], len(head.children), flush=True)
    print('DIRECTIONAL_GENERATION_OK', len(records), flush=True)


if __name__ == '__main__':
    main()
