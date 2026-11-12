"""Render unchanged native/independent GLB for retrospective concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / 'sources/docs/assets/reconstruction/ships/terran/destructor'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_render_metadata(path):
    raw = path.read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    clean = bytearray(raw[:8])
    position = 8
    while position < len(raw):
        length = struct.unpack_from('>I', raw, position)[0]
        end = position + length + 12
        assert end <= len(raw)
        if raw[position + 4:position + 8] not in {b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME'}:
            clean.extend(raw[position:end])
        position = end
    path.write_bytes(clean)


def geometry():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        obj.data.calc_loop_triangles()
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        result[obj.name] = {
            'triangles': len(obj.data.loop_triangles),
            'bounds': [min(p[a] for p in points) for a in range(3)]
                      + [max(p[a] for p in points) for a in range(3)],
        }
    return result


def main(output):
    assert output.resolve().is_relative_to(ROOT.resolve())
    output.mkdir(parents=True, exist_ok=True)
    before = {ext: sha(MODEL / ('model.' + ext)) for ext in ['blend', 'glb']}
    bpy.ops.wm.open_mainfile(filepath=str(MODEL / 'model.blend'), load_ui=False, use_scripts=False)
    bpy.context.scene.frame_set(1)
    native = geometry()
    # Preserve only the native lighting/camera rig, never its geometry.
    views = [('front-quarter', (7, -10, 8)), ('rear-quarter', (7, 10, 8))]
    images = {}
    for phase in ['native', 'imported']:
        if phase == 'imported':
            for obj in list(bpy.context.scene.objects):
                if obj.type in {'MESH', 'EMPTY'}:
                    bpy.data.objects.remove(obj, do_unlink=True)
            assert not any(o.type == 'MESH' for o in bpy.context.scene.objects)
            bpy.ops.import_scene.gltf(filepath=str(MODEL / 'model.glb'))
        bpy.context.view_layer.update()
        current = geometry()
        assert current.keys() == native.keys()
        error = max(abs(a - b) for name in current for a, b in zip(current[name]['bounds'], native[name]['bounds']))
        assert error < 1e-5
        scene = bpy.context.scene
        scene.render.resolution_x = scene.render.resolution_y = 640
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.render.film_transparent = True
        if scene.render.engine == 'CYCLES':
            scene.cycles.samples = 32
        cam = scene.camera
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = 5.5
        target = Vector((0, -.2, .05))
        for name, direction in views:
            cam.location = target + Vector(direction).normalized() * 15
            cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
            path = output / (phase + '-' + name + '.png')
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            strip_render_metadata(path)
            images[path.name] = sha(path)
    assert before == {ext: sha(MODEL / ('model.' + ext)) for ext in before}
    report = dict(issue=248, blender=bpy.app.version_string, verifier_sha256=sha(Path(__file__)),
                  blend= (MODEL / 'model.blend').relative_to(ROOT).as_posix(),
                  glb=(MODEL / 'model.glb').relative_to(ROOT).as_posix(), binaries=before,
                  mesh_count=len(native), triangles=sum(v['triangles'] for v in native.values()),
                  maximum_same_name_world_bounds_error=error, images=images,
                  model_bytes_unchanged=True, final_artistic_acceptance=False,
                  scope='Actual frame-1 native/independent GLB renders and name/bounds smoke. No topology, UV, client scale, mounts or final artistic acceptance inferred.')
    (output / 'runtime-review.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('DESTRUCTOR_PROTOCOL_RENDERED', len(native), error, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]).output.resolve())
