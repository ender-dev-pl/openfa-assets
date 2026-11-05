"""Render the saved editable scene to a hero still and a 12 fps preview."""
import json
from pathlib import Path
import bpy

root = Path(bpy.data.filepath).resolve().parent
scene = bpy.context.scene
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
scene.frame_set(37)
scene.render.resolution_x = 960
scene.render.resolution_y = 840
scene.cycles.samples = 64
scene.cycles.adaptive_threshold = 0.03
scene.cycles.adaptive_min_samples = 12
scene.render.filepath = str(root / 'hero-frame-036.png')
bpy.ops.render.render(write_still=True)
frames = root / 'rendered-frames'
frames.mkdir(exist_ok=True)
scene.render.resolution_x = 640
scene.render.resolution_y = 560
scene.cycles.samples = 24
scene.cycles.adaptive_threshold = 0.10
scene.cycles.adaptive_min_samples = 4
for frame in range(1, 97):
    scene.frame_set(frame)
    scene.render.filepath = str(frames / f'frame-{frame-1:06d}.png')
    bpy.ops.render.render(write_still=True)
    print(f'INTRO_RENDER_FRAME {frame}/96', flush=True)
(root / 'render-result.json').write_text(json.dumps({
    'hero': 'hero-frame-036.png', 'hero_resolution': [960,840],
    'preview_resolution': [640,560], 'rendered_frames':96,
    'fps':12, 'duration_seconds':8, 'engine':'Cycles CPU',
},indent=2)+'\n')
print('INTRO_SCENE_RENDER_FINISHED', flush=True)
