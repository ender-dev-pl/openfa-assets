"""Exercise rotating hierarchies and independently inspect/import their animated GLBs."""
import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_directional_catalogue import ROOT, RIG_NAME, BASE_NAME, requires_rig


def geometry(objects):
    graph = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    return {obj.name: [tuple(obj.matrix_world @ vertex.co) for vertex in obj.evaluated_get(graph).data.vertices]
            for obj in objects}


def difference(first, second):
    assert first.keys() == second.keys()
    return max(abs(a-b) for name in first for p,q in zip(first[name],second[name]) for a,b in zip(p,q))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    records = [record for record in json.loads((ROOT/'recipes.json').read_text(encoding='utf-8'))['buildings'] if requires_rig(record)]
    gameplay = json.loads((ROOT.parents[3]/'content/standard/catalogues/legacy-gameplay.json').read_text(encoding='utf-8'))
    def directional_ids(value):
        if isinstance(value,dict):
            return set(value.get('directionalBodyDefinitionIds',[])).union(
                *(directional_ids(child) for child in value.values()))
        if isinstance(value,list):
            return set().union(*(directional_ids(child) for child in value))
        return set()
    assert directional_ids(gameplay) <= {record['building_id'] for record in records}
    all_records = json.loads((ROOT/'recipes.json').read_text(encoding='utf-8'))['buildings']
    assert {record['global_type'] for record in all_records if record['definition_class'] in [3,17,18,27,40]} <= {record['global_type'] for record in records}
    if args.ids:
        ids = set(map(int,args.ids.split(',')))
        records = [record for record in records if record['global_type'] in ids]
        assert len(records) == len(ids)
    signature = hashlib.sha256((Path(__file__).parent/'build_directional_catalogue.py').read_bytes()).hexdigest()
    for record in records:
        output = ROOT/record['culture']/record['preview'].lower()
        metadata = json.loads((output/'model.json').read_text(encoding='utf-8'))
        rig = metadata['rotation_rig']
        assert rig['generator_sha256'] == signature
        bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
        scene = bpy.context.scene
        head, base = bpy.data.objects[RIG_NAME], bpy.data.objects[BASE_NAME]
        assert head.type == base.type == 'EMPTY' and head.parent is None and base.parent is None
        assert len(head.children) == len(rig['moving_meshes']) > 0
        assert len(base.children) == len(rig['static_meshes']) > 0
        assert {obj.name for obj in head.children} == set(rig['moving_meshes'])
        assert {obj.name for obj in base.children} == set(rig['static_meshes'])
        assert all(abs(head.location[i]-rig['pivot'][i]) < 1e-6 for i in range(3))
        scene.frame_set(1)
        static_start, moving_start = geometry(base.children), geometry(head.children)
        camera = scene.camera.matrix_world.copy()
        for index in range(16):
            scene.frame_set(index+1)
            assert abs(head.rotation_euler.z-index*math.tau/16) < 1e-5
            assert difference(static_start,geometry(base.children)) < 1e-6
            assert scene.camera.matrix_world == camera
        scene.frame_set(5)
        assert difference(moving_start,geometry(head.children)) > 0.1
        scene.frame_set(17)
        assert difference(moving_start,geometry(head.children)) < 1e-5
        binary = (output/'model.glb').read_bytes()
        assert binary[:4] == b'glTF'
        length, kind = struct.unpack_from('<II',binary,12)
        assert kind == 0x4E4F534A
        gltf = json.loads(binary[20:20+length])
        nodes = gltf['nodes']
        head_index = next(i for i,node in enumerate(nodes) if node.get('name') == RIG_NAME)
        base_index = next(i for i,node in enumerate(nodes) if node.get('name') == BASE_NAME)
        assert len(nodes[head_index]['children']) == len(head.children)
        assert len(nodes[base_index]['children']) == len(base.children)
        channels = [channel for animation in gltf['animations'] for channel in animation['channels']]
        assert any(channel['target']['node'] == head_index and channel['target']['path'] == 'rotation' for channel in channels)
        assert all(channel['target']['node'] != base_index for channel in channels)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
        assert bpy.data.objects[RIG_NAME].animation_data
        assert len(bpy.data.objects[RIG_NAME].children) == len(rig['moving_meshes'])
        assert len(bpy.data.objects[BASE_NAME].children) == len(rig['static_meshes'])
        imported_scene = bpy.context.scene
        imported_head, imported_base = bpy.data.objects[RIG_NAME], bpy.data.objects[BASE_NAME]
        start, end = imported_head.animation_data.action.frame_range
        def imported_pose(progress):
            frame = start + (end-start)*progress
            imported_scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))
        imported_pose(0)
        imported_static = geometry(imported_base.children)
        imported_moving = geometry(imported_head.children)
        imported_pose(0.25)
        assert difference(imported_static,geometry(imported_base.children)) < 1e-6
        assert difference(imported_moving,geometry(imported_head.children)) > 0.1
        imported_pose(1)
        assert difference(imported_moving,geometry(imported_head.children)) < 1e-5
        print('DIRECTIONAL_RIG_OK',record['global_type'],record['preview'],flush=True)
    print('DIRECTIONAL_VERIFICATION_OK',len(records),flush=True)


if __name__ == '__main__':
    main()
