"""Verify that PB14 really uses fixed-pivot planar iris kinematics."""
from pathlib import Path
import hashlib
import json
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb14'


def check(offset):
    leaves = [o for o in bpy.context.scene.objects if o.name.startswith('Iris curved leaf')]
    assert len(leaves) == 16
    pivots = {}
    height_error = 0
    axis_error = 0
    minimum_layer_gap = 1
    openings = []
    for frame in range(1, 34):
        bpy.context.scene.frame_set(frame-offset)
        bpy.context.view_layer.update()
        bands = []
        for leaf in leaves:
            pivot = leaf.matrix_world.translation.copy()
            if frame == 1:
                pivots[leaf.name] = pivot
            assert (pivot-pivots[leaf.name]).length < 1e-6
            axis = leaf.matrix_world.to_3x3()@Vector((0, 0, 1))
            axis_error = max(axis_error, (axis-Vector((0, 0, 1))).length)
            deps = bpy.context.evaluated_depsgraph_get()
            obj = leaf.evaluated_get(deps)
            mesh = obj.to_mesh()
            zs = [(leaf.matrix_world@v.co).z for v in mesh.vertices]
            height_error = max(height_error, max(zs)-min(zs))
            bands.append((min(zs), max(zs)))
            obj.to_mesh_clear()
        bands.sort()
        minimum_layer_gap = min(minimum_layer_gap, min(b[0]-a[1] for a, b in zip(bands, bands[1:])))
        if frame in [1, 5, 9, 13, 17]:
            deps = bpy.context.evaluated_depsgraph_get()
            clear = 0
            samples = 0
            for x in range(-16, 17):
                for y in range(-16, 17):
                    px = x*.05
                    py = y*.05
                    if math.hypot(px, py) > .82:
                        continue
                    hit, *_ = bpy.context.scene.ray_cast(deps, Vector((px, py, 1.1)), Vector((0, 0, -1)), distance=.6)
                    clear += not hit
                    samples += 1
            openings.append(dict(frame=frame, clear=clear, samples=samples))
    assert axis_error < 1e-6 and height_error < .00101
    assert minimum_layer_gap > .00049, 'Overlapping blade height bands'
    assert openings[0]['clear'] == 0
    assert openings[-1]['clear'] == openings[-1]['samples']
    assert all(a['clear'] < b['clear'] for a, b in zip(openings, openings[1:])), openings
    return dict(blades=len(leaves), frames=33, fixed_pivots=True, out_of_plane_axis_error=axis_error, maximum_sheet_thickness=height_error, minimum_blade_layer_gap=minimum_layer_gap, opening_samples=openings)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'), load_ui=False, use_scripts=False)
    native = check(0)
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'))
    bpy.context.scene.render.fps = 16
    imported = check(1)
    report = dict(native=native, imported=imported, binaries={suffix: hashlib.sha256((FOLDER/('model.'+suffix)).read_bytes()).hexdigest() for suffix in ['blend', 'glb']}, verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (FOLDER/'diaphragm-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PLANAR_DIAPHRAGM_VERIFIED', json.dumps(report))


if __name__ == '__main__':
    main()
