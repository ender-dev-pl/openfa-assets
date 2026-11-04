"""Reproduce the actual crossed-plate failure and verify mirrored fixes and data guards."""
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fighter_plate_topology import repair_plate
from probe_fighter_armour_tessellation import measure, SOURCE, OUTPUT


def main():
    proposal = json.loads((OUTPUT/'proposal.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'model.blend'))
    cases = []
    for name in ['Swept tessellated wing armour', 'Swept tessellated wing armour.006']:
        template = bpy.data.objects[name]
        obj = template.copy()
        obj.data = template.data.copy()
        bpy.context.scene.collection.objects.link(obj)
        points = proposal['original_vertices'][name]
        obj.data.clear_geometry()
        obj.data.from_pydata(points, [], [(0, 3, 2, 1), (7, 4, 5, 6),
            (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
        obj.data.update()
        broken = measure(obj)
        assert broken['nonadjacent_triangle_intersections'], 'Regression fixture must expose actual intersections'
        repair_plate(obj)
        repaired = measure(obj)
        assert repaired['triangle_signed_volume'] > 0 and repaired['all_edges_manifold']
        assert not repaired['nonadjacent_triangle_intersections']
        assert points == [list(vertex.co) for vertex in obj.data.vertices]
        faces = [tuple(face.vertices) for face in obj.data.polygons]
        try:
            repair_plate(obj)
        except AssertionError:
            pass
        else:
            raise AssertionError('Already repaired topology must not be rewritten by the migration helper')
        assert faces == [tuple(face.vertices) for face in obj.data.polygons]
        cases.append(repaired['triangle_signed_volume'])
    assert abs(cases[0]-cases[1]) < 1e-6, 'Mirrored geometry must enclose the same volume'
    # Existing UV data is outside this topology-only migration's permitted inputs.
    obj.data.clear_geometry()
    obj.data.from_pydata(points, [], [(0, 1, 2, 3), (7, 6, 5, 4),
        (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    obj.data.uv_layers.new(name='Keep existing UVs')
    try:
        repair_plate(obj)
    except AssertionError:
        pass
    else:
        raise AssertionError('An unreviewed UV-bearing input must be rejected')
    assert obj.data.uv_layers.get('Keep existing UVs')
    print('FIGHTER_PLATE_TOPOLOGY_REGRESSION_OK', flush=True)


if __name__ == '__main__':
    main()
