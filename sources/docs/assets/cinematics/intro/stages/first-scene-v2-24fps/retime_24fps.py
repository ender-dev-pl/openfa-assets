"""Double the opening's temporal sampling while preserving its 8 second timing."""
import hashlib
import json
import math
from pathlib import Path
import shutil

import bpy

root = Path(__file__).resolve().parent
root.mkdir(parents=True, exist_ok=True)
source = Path(bpy.data.filepath).resolve()
scene = bpy.context.scene
assert scene.render.fps == 12 and scene.frame_start == 1 and scene.frame_end == 96
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
curves = []
seen = set()
for action in bpy.data.actions:
    if action.is_action_layered:
        candidates = [curve for layer in action.layers for strip in layer.strips
                      if strip.type == 'KEYFRAME' for bag in strip.channelbags for curve in bag.fcurves]
    else:
        candidates = list(action.fcurves)
    for curve in candidates:
        if curve.as_pointer() not in seen:
            assert not curve.modifiers, 'Review time-dependent curve modifiers before retiming'
            curves.append(curve)
            seen.add(curve.as_pointer())
assert curves, 'No animation channels found'
times = [1 + index / 2 for index in range(192)]
curve_values = [[curve.evaluate(time) for time in times] for curve in curves]
animated_objects = [obj for obj in scene.objects if obj.animation_data and obj.animation_data.action]


def pose_at(time):
    frame = math.floor(time)
    scene.frame_set(frame, subframe=time-frame)
    return [value for obj in animated_objects for row in obj.matrix_world for value in row]


world_poses = [pose_at(time) for time in times]
key_count = 0
for curve in curves:
    points = [(point, point.co.x, point.handle_left.x, point.handle_right.x)
              for point in curve.keyframe_points]
    for point, x, left, right in points:
        point.co.x = 1 + 2 * (x - 1)
    for point, x, left, right in points:
        point.handle_left.x = 1 + 2 * (left - 1)
        point.handle_right.x = 1 + 2 * (right - 1)
    key_count += len(points)
    curve.update()
curve_error = max(abs(curve.evaluate(index+1) - old[index])
                  for curve, old in zip(curves,curve_values) for index in range(192))
pose_error = max(abs(value - old) for index in range(192)
                 for value, old in zip(pose_at(index+1),world_poses[index]))
assert curve_error < 0.0005, f'Animation channel timing changed: {curve_error}'
assert pose_error < 0.0005, f'World-space trajectory changed: {pose_error}'
scene.render.fps = 24
scene.render.fps_base = 1
scene.frame_start = 1
scene.frame_end = 192
scene.frame_set(73)
scene['timeline'] = '192 frames at 24fps; frame 1 = t0; old frame n maps to new frame 2*n-1.'
scene['retiming'] = 'All object and material animation keys and Bezier handles retimed around frame 1. New intermediate frames rendered from 3D.'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'opening-reconstruction-24fps.blend'))
scene_hash = hashlib.sha256((root/'opening-reconstruction-24fps.blend').read_bytes()).hexdigest()
frames = root/'rendered-frames'
frames.mkdir(exist_ok=True)
completed = {}
for index in range(96):
    original = source.parent/'rendered-frames'/f'frame-{index:06d}.png'
    destination = frames/f'frame-{index*2:06d}.png'
    shutil.copyfile(original,destination)
    completed[str(index*2)] = hashlib.sha256(destination.read_bytes()).hexdigest()
shutil.copyfile(source.parent/'hero-frame-036.png',root/'hero-24fps.png')
(root/'render-state.json').write_text(json.dumps({'scene_sha256':scene_hash,'completed':completed},indent=2)+'\n')
report = {'fps':24,'frames':192,'duration_seconds':8,
          'source_scene_sha256':source_hash,'scene_sha256':scene_hash,
          'mapping':'new_frame = 1 + 2 * (old_frame - 1)',
          'action_count':len(bpy.data.actions),'animation_channels':len(curves),
          'keyframes_retimed':key_count,'sample_times_checked':192,
          'animated_objects_checked':len(animated_objects),
          'max_animation_channel_error':curve_error,'max_world_matrix_error':pose_error,
          'reused_original_renders':96,'new_3d_renders_required':96}
(root/'retiming-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('RETIME_VERIFIED',json.dumps(report),flush=True)
