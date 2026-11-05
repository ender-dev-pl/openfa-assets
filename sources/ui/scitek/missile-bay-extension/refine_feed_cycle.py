"""Correct ST14's visible magazine/feed/loading sequence without replacing meshes.

Blender CLI: -- INPUT_BLEND OUTPUT_DIRECTORY. Legacy phase indices are zero based.
Dimensions and trajectories are interpreted; ordering follows _MA/ST14.VID.
"""
import bpy
import sys
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

source = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out = Path(sys.argv[sys.argv.index('--') + 2]).resolve()
out.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
s = bpy.context.scene
root = bpy.data.objects['MissileBayRig']
carriage = bpy.data.objects['HydraulicTransferCarriage']
missile = bpy.data.objects['MissileTransferPivot']
metadata = json.loads((source.parent / 'model.json').read_text())
solid = [bpy.data.objects[n] for ns in metadata['components'].values() for n in ns]

def digest(ob):
    return hashlib.sha256(repr(([(tuple(v.co)) for v in ob.data.vertices],
                               [tuple(p.vertices) for p in ob.data.polygons])).encode()).hexdigest()

before = {ob.name: digest(ob) for ob in solid}
s.frame_set(1)
for ob in [carriage, missile]:
    ob.animation_data_clear()
feeder = bpy.data.objects.new('MissileFeederCradle', None)
s.collection.objects.link(feeder)
feeder.parent = root
bed = bpy.data.objects['Hydraulic transport lower bed']
bed.parent = feeder
rocket = [ob for ob in solid if ob.name.startswith('Lifted missile')]
for ob in rocket:
    ob.location -= Vector((.10, -.38, .62))

def keys(ob, rows):
    for index, loc, angle in rows:
        ob.location = loc
        ob.rotation_euler = (0, math.radians(angle), 0)
        ob.keyframe_insert('location', frame=index + 1)
        ob.keyframe_insert('rotation_euler', frame=index + 1)
    for fc in ob.animation_data.action.fcurves:
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'

# Rocket starts below the annular rim, rises at the right magazine outlet,
# traverses onto the inclined feed lane, then enters the mast before reset.
keys(missile, [
    (0, (.50, -.40, -.56), 0), (32, (.50, -.40, -.56), 0),
    (54, (.50, -.40, .39), 0), (64, (.50, -.40, .39), 0),
    (84, (.30, -.42, .39), -7), (105, (.10, -.44, .39), -15),
    (120, (.08, -.44, .39), -15),
    (133, (.04, -.29, 1.10), -8), (141, (0, .04, 1.75), 0),
    (151, (0, .04, 1.75), 0), (164, (0, .04, -.56), 0),
    (174, (.50, -.40, -.56), 0), (180, (.50, -.40, -.56), 0),
])
# The saddle travels to receive the missile and follows its transfer. It
# returns empty after handoff; it is not owned by the overhead loading head.
keys(feeder, [
    (0, (0, 0, 0), 0), (30, (0, 0, 0), 0),
    (54, (.50, -.01, -.07), 0), (64, (.50, -.01, -.07), 0),
    (84, (.30, -.03, -.07), -7), (105, (.10, -.05, -.07), -15),
    (120, (.08, -.05, -.07), -15), (133, (.04, .10, .40), -8),
    (145, (0, 0, 0), 0), (180, (0, 0, 0), 0),
])
keys(carriage, [
    (0, (0, 0, 0), 0), (125, (0, 0, 0), 0),
    (140, (0, 0, -.35), 0), (151, (0, 0, -.62), 0),
    (166, (0, 0, -.62), 0), (180, (0, 0, 0), 0),
])
nodes = [ob for ob in solid if ob.parent in [missile, feeder, carriage]]
s.frame_start = 1
s.frame_end = 181
s.render.fps = 15
frames = []
for f in range(1, 181):
    s.frame_set(f)
    bpy.context.view_layer.update()
    frames.append(dict(frame=f-1, mesh_root_matrices={ob.name: [v for row in
        (root.matrix_world.inverted() @ ob.matrix_world) for v in row] for ob in nodes}))
s.frame_set(1)
bpy.context.view_layer.update()
blend = out / source.name
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.object.select_all(action='DESELECT')
for ob in solid + [root, missile, carriage, feeder]:
    ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(blend.with_suffix('.glb')), use_selection=True,
    export_apply=True, export_animations=True, export_animation_mode='ACTIVE_ACTIONS',
    export_format='GLB')
timeline = json.loads((source.parent / 'solid-animation-timeline.json').read_text())
timeline.update(animated_mesh_nodes=[ob.name for ob in nodes], timeline=frames,
    bind_root_matrices=frames[0]['mesh_root_matrices'],
    source_blend_sha256=hashlib.sha256(blend.read_bytes()).hexdigest(),
    source_glb_sha256=hashlib.sha256(blend.with_suffix('.glb').read_bytes()).hexdigest(),
    choreography='Magazine rise -> lateral feeder handoff and tilt -> mast insertion -> loader down/return',
    phases=[dict(name=n, first=a, last=b) for n,a,b in [
        ('magazine-ejection',33,54), ('feeder-transfer',65,105),
        ('mast-insertion',121,141), ('loader-descent',126,151),
        ('empty-return',152,179)]])
(out / 'solid-animation-timeline.json').write_text(json.dumps(timeline, separators=(',', ':'))+'\n')
assert before == {ob.name: digest(ob) for ob in solid}, 'Mesh geometry changed'
(out / 'feed-cycle-provenance.json').write_text(json.dumps(dict(
    original_blend_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    corrected_blend_sha256=timeline['source_blend_sha256'],
    corrected_glb_sha256=timeline['source_glb_sha256'],
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    unchanged_mesh_geometry=before, original_reference='_MA/ST14.VID',
    reference_frames=180, trajectories='authored interpretation of observed phases'), indent=2)+'\n')
print('ST14_FEED_CYCLE_REBUILT')
