"""Render the authored ship at the runtime's 32 heading positions."""
import json
import hashlib
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_refined_terran import render_to
from catalogue_rendering import evaluated_points,fit_camera

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/ships/terran/assault-fighter'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
scene=bpy.context.scene
meshes=[obj for obj in scene.objects if obj.type=='MESH']
points=evaluated_points(meshes)
(ROOT/'directions').mkdir(exist_ok=True)
for heading in range(32):
    angle=heading*math.tau/32
    fit_camera(scene,points,(math.sin(angle)*14,-math.cos(angle)*14,10))
    # Constant framing scale across headings, not a per-frame size change.
    scene.camera.data.ortho_scale=7.3
    render_to(scene,ROOT/'directions'/f'{heading:02}.png')
(ROOT/'directions.json').write_text(json.dumps(dict(count=32,axis='+Z',model_forward='-Y',
    blend_sha256=hashlib.sha256((ROOT/'model.blend').read_bytes()).hexdigest(),
    sampling='camera orbit; model remains static',camera_elevation_degrees=math.degrees(math.atan2(10,14)),
    ortho_scale=7.3,gameplay_alignment='not yet calibrated against projection/runtime heading offsets'),indent=2)+'\n')
print('ASSAULT_FIGHTER_DIRECTIONS_OK 32',flush=True)
