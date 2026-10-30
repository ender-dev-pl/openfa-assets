"""Regression checks on the actual three details; sources are opened but never saved."""
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repair_detail_uvs import LAYER, DETAILS, bind_detail_uvs, verify_detail_uvs

REPO = Path(__file__).resolve().parents[2]


def charts(meshes):
    return {obj.name: {chart.name: [tuple(loop.uv) for loop in chart.data]
                       for chart in obj.data.uv_layers} for obj in meshes}


def main():
    tested = set()
    for slug in ['strategic-bunker', 'ultrathermal-lance']:
        path = REPO/'docs/assets/reconstruction/buildings/rigellian'/slug/'model.blend'
        bpy.ops.wm.open_mainfile(filepath=str(path))
        meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        verify_detail_uvs(meshes)
        # Reproduce each confirmed missing named chart in memory; retain the base fitting UVMap.
        for obj in meshes:
            if obj.name in DETAILS and obj.data.uv_layers.get(LAYER):
                obj.data.uv_layers.remove(obj.data.uv_layers[LAYER])
        original = charts(meshes)
        for obj in meshes:
            if obj.name not in DETAILS:
                continue
            try:
                verify_detail_uvs([obj])
            except AssertionError:
                tested.add(obj.name)
            else:
                raise AssertionError('Reproduced missing-chart regression was not detected: '+obj.name)
        changes = bind_detail_uvs(meshes)
        assert {row['object'] for row in changes} == {obj.name for obj in meshes if obj.name in DETAILS}
        verify_detail_uvs(meshes)
        proposed = charts(meshes)
        assert all(obj.data.uv_layers[0].name == LAYER for obj in meshes if obj.name in DETAILS)
        for name, layers in original.items():
            for chart, values in layers.items():
                assert proposed[name][chart] == values, 'An existing UV chart was altered'
            if name not in DETAILS:
                assert proposed[name] == layers, 'Untargeted mesh changed'
            elif layers:
                assert proposed[name][LAYER] == next(iter(layers.values())), 'Existing coordinates not copied exactly'
        assert not bind_detail_uvs(meshes)
        assert charts(meshes) == proposed, 'Second invocation altered charts'
    assert tested == DETAILS
    print('DETAIL_UV_PROPOSAL_REGRESSION_OK', len(tested), flush=True)


if __name__ == '__main__':
    main()
