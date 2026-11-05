"""Render missing 24fps frames; matching original renders can be reused exactly."""
import hashlib
import json
from pathlib import Path
import bpy

root = Path(bpy.data.filepath).resolve().parent
scene = bpy.context.scene
assert scene.render.fps == 24 and scene.frame_end == 192
scene_hash = hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
state_path = root/'render-state.json'
state = json.loads(state_path.read_text()) if state_path.exists() else {}
if state.get('scene_sha256') != scene_hash:
    state = {'scene_sha256':scene_hash,'completed':{}}
frames = root/'rendered-frames'
frames.mkdir(exist_ok=True)
scene.render.resolution_x = 640
scene.render.resolution_y = 560
scene.render.resolution_percentage = 100
scene.cycles.samples = 24
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.10
scene.cycles.adaptive_min_samples = 4
scene.cycles.use_denoising = True
nebula = next(o for o in scene.objects if o.name.startswith('Following shot — nebula'))
scene.frame_set(177)
scene.render.resolution_x=960
scene.render.resolution_y=840
scene.cycles.samples=32
scene.cycles.adaptive_threshold=0.05
scene.cycles.adaptive_min_samples=8
scene.render.filepath=str(root/'hero-ship-fit.png')
bpy.ops.render.render(write_still=True)
scene.render.resolution_x=640
scene.render.resolution_y=560
scene.cycles.samples=24
scene.cycles.adaptive_threshold=0.10
scene.cycles.adaptive_min_samples=4
rendered = 0
for index in range(192):
    path = frames/f'frame-{index:06d}.png'
    if path.is_file() and state['completed'].get(str(index)) == hashlib.sha256(path.read_bytes()).hexdigest():
        continue
    scene.frame_set(index+1)
    # Exactly zero emission plus transparent surface: skip the invisible procedural card.
    nebula.hide_render = index < 132
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    state['completed'][str(index)] = hashlib.sha256(path.read_bytes()).hexdigest()
    temporary = state_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state,indent=2)+'\n')
    temporary.replace(state_path)
    rendered += 1
    print(f'RENDER_24FPS_COMPLETE {len(state["completed"])}/192 new={rendered}',flush=True)
(root/'render-result.json').write_text(json.dumps({'fps':24,'frames':192,'duration_seconds':8,
    'resolution':[640,560],'new_frames_rendered_this_run':rendered,
    'verified_completed_frames':len(state['completed']),'scene_sha256':scene_hash},indent=2)+'\n')
print('ANIMATION_24FPS_RENDER_FINISHED',flush=True)
