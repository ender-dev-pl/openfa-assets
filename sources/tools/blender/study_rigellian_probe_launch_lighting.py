"""Diagnostic RI11 lighting study; references remain outside authored deliverables."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_rigellian_probe_launch import ROOT,REPO
from build_refined_terran import render_to
from catalogue_rendering import evaluated_points,fit_camera

out=ROOT/'lighting-study';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
scene=bpy.context.scene
for obj in list(scene.objects):
    if obj.type=='LIGHT': bpy.data.objects.remove(obj,do_unlink=True)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.10
meshes=[o for o in scene.objects if o.type=='MESH']
fit_camera(scene,evaluated_points(meshes),(0,-16,10))
scene.render.resolution_x=scene.render.resolution_y=600
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.data.energy=3;sun.data.angle=math.radians(1)
for elevation in [25,40,55]:
    direction=Vector((1,-.35,math.tan(math.radians(elevation))))
    sun.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    render_to(scene,out/f'right-key-{elevation}.png')
(out/'study.json').write_text(json.dumps(dict(source_blend='docs/assets/reconstruction/buildings/rigellian/probe-launch/model.blend',source_blend_sha256=hashlib.sha256((ROOT/'model.blend').read_bytes()).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),render_sha256={f'right-key-{v}.png':hashlib.sha256((out/f'right-key-{v}.png').read_bytes()).hexdigest() for v in [25,40,55]},purpose='Test whether an upper port casts the observed left dark region; lighting alone cannot establish hidden geometry',elevations=[25,40,55],camera=[0,-16,10]),indent=2)+'\n')
print('RI11_LIGHTING_STUDY_OK')
