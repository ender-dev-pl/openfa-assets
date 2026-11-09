"""Preserve RI10 geometry and deliver descriptor controls in one animated GLB."""
import json
from pathlib import Path
import sys
import struct
import tempfile
import uuid
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from remaster_rigellian_static import ROOT, sha, strip_png, closed
from rigellian_shaft_preview import asset_meshes, surface_points, ground_mask
from catalogue_rendering import fit_camera
from export_rigellian_ground_deck_states import pose_controls

FOLDER = ROOT / 'sources/objects/rigellian/ground-deck'
MEDIA = ROOT / 'gallery/media/objects/rigellian/ground-deck'
CYCLE = 'GroundDeckCoverCycle'
STATES = 'GroundDeckDescriptorStates'
TARGETS = ['CoverLeft', 'CoverRight', 'CoverLeftInner', 'CoverLeftOuter', 'CoverRightInner', 'CoverRightOuter']


def select_clip(name, frame):
    for obj in bpy.context.scene.objects:
        if not obj.animation_data:
            continue
        obj.animation_data.action = None
        for track in obj.animation_data.nla_tracks:
            track.is_solo = False
            track.mute = track.name != name
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()


def main():
    recipe_path = FOLDER / 'recipe.json'
    case = json.loads(recipe_path.read_bytes())
    source = ROOT / case['source']
    assert sha(source) == case['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.frame_set(1)
    meshes = asset_meshes(scene)
    assert len(meshes) == 45
    for obj in meshes:
        assert closed(obj), obj.name
    original = json.loads((ROOT / case['mechanism_evidence']).read_bytes())
    measurements = {row['index']: row for row in original['measurements']}
    cycle_actions = {name: bpy.data.objects[name].animation_data.nla_tracks[CYCLE].strips[0].action for name in TARGETS}
    states = []
    for descriptor in range(2, 18):
        widths = [half['projected_width'] for half in measurements[descriptor]['halves']] if descriptor < 15 else None
        fractions = pose_controls(widths)
        states.append(dict(descriptor=descriptor, clip=STATES, frame=descriptor,
                           fractions=fractions, cover_overlay_empty=descriptor in [15, 16],
                           lower_structure_shadow_composition_verified=False if descriptor == 17 else None))
    for name in TARGETS:
        obj = bpy.data.objects[name]
        for track in obj.animation_data.nla_tracks:
            track.mute = True
        obj.animation_data.action = None
        for state in states:
            side = 0 if 'Left' in name else 1
            fraction = state['fractions'][side]
            if name in ['CoverLeft', 'CoverRight']:
                obj.location.z = 1.02 if fraction == 0 else 1.055
            else:
                sign = -1 if side == 0 else 1
                obj.location.x = sign * (.88 if name.endswith('Inner') else .46) * fraction
            obj.keyframe_insert(data_path='location', frame=state['frame'])
        action = obj.animation_data.action
        action.name = name + ' descriptor controls'
        for curve in action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = 'CONSTANT'
        track = obj.animation_data.nla_tracks.new()
        track.name = STATES
        track.strips.new(STATES, 2, action)
        obj.animation_data.action = None
        assert obj.animation_data.nla_tracks[CYCLE].strips[0].action == cycle_actions[name]
    root = bpy.data.objects['PlacementRoot']
    root['forward_axis'] = 'local -Y'
    root['dorsal_axis'] = 'local +Z'
    root['state_contract'] = case['state_contract']
    FOLDER.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    scene.frame_start = 1
    scene.frame_end = 61
    # Export all named tracks; the exporter isolates each track during sampling.
    for name in TARGETS:
        for track in bpy.data.objects[name].animation_data.nla_tracks:
            track.mute = False
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH', 'EMPTY'] and not obj.get('preview_only'):
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    temporary_root = ROOT / 'artifacts/rigellian-remaster-temp'
    temporary_root.mkdir(parents=True, exist_ok=True)
    previous = tempfile.mkdtemp

    def workspace_temp(suffix=None, prefix=None, dir=None):
        parent = Path(dir).resolve() if dir else temporary_root
        assert parent.is_relative_to(ROOT.resolve())
        path = parent / ((prefix or 'ri10-') + uuid.uuid4().hex + (suffix or ''))
        path.mkdir()
        return str(path)

    tempfile.mkdtemp = workspace_temp
    try:
        bpy.ops.export_scene.gltf(filepath=str(FOLDER / 'model.glb'), export_format='GLB', use_selection=True,
                                 export_apply=True, export_extras=True, export_animations=True,
                                 export_animation_mode='NLA_TRACKS', export_frame_range=True)
    finally:
        tempfile.mkdtemp = previous
    # The exporter samples object tracks as LINEAR. Descriptor poses are a
    # discrete lookup, so retain the native CONSTANT semantics in glTF too.
    raw = (FOLDER / 'model.glb').read_bytes()
    json_length = struct.unpack_from('<I', raw, 12)[0]
    document = json.loads(raw[20:20+json_length])
    descriptor_clip = next(clip for clip in document['animations'] if clip['name'] == STATES)
    for sampler in descriptor_clip['samplers']:
        sampler['interpolation'] = 'STEP'
    text = json.dumps(document, separators=(',', ':')).encode()
    text += b' ' * (-len(text) % 4)
    binary_chunk = raw[20+json_length:]
    output = struct.pack('<III', 0x46546c67, 2, 20+len(text)+len(binary_chunk))
    output += struct.pack('<II', len(text), 0x4e4f534a) + text + binary_chunk
    (FOLDER / 'model.glb').write_bytes(output)
    select_clip(CYCLE, 1)
    fit_camera(scene, surface_points(meshes), (0, -16, 7))
    bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER / 'model.blend'), compress=True)
    sys.path.insert(0, str(ROOT / 'tools'))
    from publication_support import clean_blend
    target = FOLDER / 'model.blend'
    target.write_bytes(clean_blend(target.read_bytes())[0])
    renders = {}
    for name, clip, frame, direction in [('front-quarter', CYCLE, 1, (6, -13, 8)),
                                          ('front', CYCLE, 1, (0, -16, 7)),
                                          ('rear-quarter', CYCLE, 1, (-7, 12, 7)),
                                          ('half-open', CYCLE, 16, (0, -16, 7)),
                                          ('open', CYCLE, 31, (0, -16, 7)),
                                          ('open-top', CYCLE, 31, (0, 0, 20))]:
        select_clip(clip, frame)
        fit_camera(scene, surface_points(meshes), direction)
        path = MEDIA / (name + '.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
        renders[path.name] = sha(path)
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    animation = dict(cycle_clip=CYCLE, cycle_frames=[1, 61], closed_frame=1, open_frame=31,
                     descriptor_clip=STATES, descriptor_frames=[2, 17], fps=scene.render.fps,
                     scale_animated=False, target_nodes=TARGETS,
                     interpolation='Descriptor controls are discrete STEP; cycle retains original inferred timing.')
    for state in states:
        state['time_seconds'] = state['frame'] / scene.render.fps
    metadata = dict(issue=253, id=case['id'], name=case['name'], author_sha256=sha(Path(__file__)),
                    recipe=recipe_path.relative_to(ROOT).as_posix(), recipe_sha256=sha(recipe_path),
                    source=case['source'], source_sha256=sha(source),
                    binaries={kind: sha(FOLDER / ('model.' + kind)) for kind in ['blend', 'glb']},
                    triangles=triangles, mesh_nodes=len(meshes), original_triangles=triangles,
                    changes=[], footprint=[3, 3], definition_class=26, construction_updates=18,
                    animation=animation, states=states,
                    mechanism_evidence=case['mechanism_evidence'], mechanism_sha256=sha(ROOT / case['mechanism_evidence']),
                    no_attached_ship_descriptor=2, altitude_bands=original['legacy_mapping']['signed_altitude_bands'],
                    final_artistic_acceptance=False, game_client_integration=False)
    (FOLDER / 'model.json').write_bytes((json.dumps(metadata, indent=2)+'\n').encode())
    assert sha(source) == case['source_sha256']
    print('RI10_CANONICAL_ANIMATED_CANDIDATE', len(meshes), triangles, flush=True)


if __name__ == '__main__':
    main()
