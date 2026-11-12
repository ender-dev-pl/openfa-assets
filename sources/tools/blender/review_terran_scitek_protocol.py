"""Read-only retrospective renders of the user-selected Terran SciTek sources."""
import argparse
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_destructor_protocol as renderer


def evaluated_geometry():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            result[obj.name] = {
                'triangles': len(mesh.loop_triangles),
                'bounds': [min(p[a] for p in points) for a in range(3)]
                          + [max(p[a] for p in points) for a in range(3)],
            }
        finally:
            evaluated.to_mesh_clear()
    return result


@bpy.app.handlers.persistent
def fit_view(scene):
    bpy.context.view_layer.update()
    inverse = scene.camera.matrix_world.inverted()
    extent = 0.0
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        for corner in obj.bound_box:
            point = inverse @ (obj.matrix_world @ Vector(corner))
            extent = max(extent, abs(point.x), abs(point.y))
    scene.camera.data.ortho_scale = max(5.5, extent * 2.2)


def main(slug, output):
    helper = Path(renderer.__file__)
    helper_before = renderer.sha(helper)
    renderer.MODEL = renderer.ROOT / 'sources/objects/terran' / slug / 'refined'
    # GLB contains modifier results, so compare evaluated native geometry to it.
    renderer.geometry = evaluated_geometry
    bpy.app.handlers.render_pre.append(fit_view)
    try:
        renderer.main(output)
    finally:
        bpy.app.handlers.render_pre.remove(fit_view)
    report_path = output / 'runtime-review.json'
    report = json.loads(report_path.read_bytes())
    assert report['verifier_sha256'] == helper_before == renderer.sha(helper)
    report['renderer_sha256'] = report.pop('verifier_sha256')
    report['renderer'] = helper.relative_to(renderer.ROOT).as_posix()
    report['verifier_sha256'] = renderer.sha(Path(__file__))
    report['id'] = 'openfa:' + slug
    report['bounds_contract'] = 'Evaluated dependency-graph geometry in both native and imported scenes, including native bevel modifiers.'
    report['framing_contract'] = 'Each actual camera fitted to projected physical bounds with ten percent margin; complete object views.'
    report['pose'] = 'Frame 1, presentation rotation disabled by fixed pose; not client integration acceptance.'
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('TERRAN_SCITEK_PROTOCOL_RENDERED', slug, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--slug', choices=['terminator', 'fleet-battleship', 'command-cruiser'], required=True)
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    main(arguments.slug, arguments.output.resolve())
