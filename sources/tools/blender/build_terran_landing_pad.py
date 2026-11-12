"""Add a reversible PB26 telescopic-cover study; never overwrite earlier studies."""
import hashlib
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'sources/docs/assets/bootstrap-3d/terran-refined/pb26/model.blend'
OUT = ROOT / 'sources/docs/assets/reconstruction/buildings/terran/landing-pad'
MEDIA = ROOT / 'gallery/media/docs/assets/reconstruction/buildings/terran/landing-pad'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(name, location, dimensions, material, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if parent:
        obj.parent = parent
    return obj


def material(name, colour, roughness=.8):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*colour, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = .35
    return result


def render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    rim = bpy.data.objects['Foundation slab'].data.materials[0]
    deck = bpy.data.objects['Landing pad inset'].data.materials[0]
    red = bpy.data.objects['Landing pad runway stripe'].data.materials[0]
    for obj in list(scene.objects):
        if obj.name.startswith(('Foundation slab', 'Landing pad inset', 'Landing pad runway stripe',
                                'Landing deck joint', 'Landing deck cross joint')):
            bpy.data.objects.remove(obj, do_unlink=True)
    dark = material('PB26 | recessed shaft and joint grime', (.025, .022, .02))
    scratch = material('PB26 | rubbed metal edges', (.31, .29, .25), .65)
    stain = material('PB26 | lubricant stains', (.09, .065, .037))
    root = bpy.data.objects.new('PlacementRoot', None)
    scene.collection.objects.link(root)
    root['catalogue_id'] = 'terran:landing-pad'
    root['footprint_width'] = root['footprint_height'] = 2
    for obj in list(scene.objects):
        if obj.type == 'MESH':
            obj.parent = root
    for sign in [-1, 1]:
        box('Static rim side', (sign * 1.0075, 0, .075), (.225, 2.24, .15), rim, root)
        box('Static rim end', (0, sign * 1.0075, .075), (1.79, .225, .15), rim, root)
        box('Shaft wall', (sign * .89, 0, .105), (.018, 1.77, .21), dark, root)
        box('Shaft end wall', (0, sign * .89, .105), (1.77, .018, .21), dark, root)
    box('Recessed dark shaft floor', (0, 0, .008), (1.77, 1.77, .016), dark, root)
    movers = []
    width = .885 / 6
    for sign, side in [(-1, 'Left'), (1, 'Right')]:
        for index in range(6):
            x = sign * width * (index + .5)
            control = bpy.data.objects.new(f'Cover{side}{index}', None)
            scene.collection.objects.link(control)
            control.parent = root
            movers.append(control)
            box(f'{side} telescopic leaf {index}', (x, 0, .18), (width - .004, 1.77, .016), deck, control)
            for stripe in [-.38, 0, .38]:
                lo = max(abs(x) - width / 2 + .003, abs(stripe) - .08)
                hi = min(abs(x) + width / 2 - .003, abs(stripe) + .08)
                if hi > lo:
                    box('Worn red runway marking', (sign * (hi + lo) / 2, 0, .189), (hi - lo, 1.35, .002), red, control)
            # Small authored scuffs, oil spots and edge grime export as real geometry/materials.
            for mark in range(4):
                y = -.65 + mark * .4 + index * .013
                box('Door edge abrasion', (x + sign * width * .3, y, .1905), (.013, .09, .001), scratch, control)
            box('Hydraulic oil stain', (x, .69 - index * .15, .1908), (.026, .055, .001), stain, control)
            for frame, fraction in [(1, 0), (31, 1), (61, 0)]:
                control.location = (sign * (.976 + (.06 if index == 5 else 0) - abs(x)) * fraction, 0, -.018 * index * fraction)
                control.keyframe_insert(data_path='location', frame=frame)
            action = control.animation_data.action
            for curve in action.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'LINEAR'
            action.name = f'{side} leaf {index} retraction'
            track = control.animation_data.nla_tracks.new()
            track.name = 'GroundDeckCoverCycle'
            track.strips.new('GroundDeckCoverCycle', 1, action)
            control.animation_data.action = None
    # Existing service covers belong to the outer leaves rather than floating over the aperture.
    for obj in scene.objects:
        if obj.name.startswith('Pad hydraulic service'):
            side = 'Left' if obj.location.x < 0 else 'Right'
            obj.parent = bpy.data.objects[f'Cover{side}5']
    scene.frame_start = 1
    scene.frame_end = 61
    scene.render.fps = 30
    scene.render.resolution_x = scene.render.resolution_y = 640
    scene.cycles.samples = 24
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH', 'EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'), export_format='GLB',
        use_selection=True, export_extras=True, export_apply=True, export_animations=True,
        export_animation_mode='NLA_TRACKS', export_frame_range=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'))
    for name, frame in [('front-quarter', 1), ('half-open', 16), ('open', 31), ('closed-again', 61)]:
        scene.frame_set(frame)
        render(scene, MEDIA / (name + '.png'))
    meta = dict(id='terran:landing-pad', issue=177, footprint=[2, 2],
        source_study=str(SOURCE.relative_to(ROOT)), source_blend_sha256=sha(SOURCE),
        blend_sha256=sha(OUT/'model.blend'), glb_sha256=sha(OUT/'model.glb'),
        generator_sha256=sha(Path(__file__)), blender=bpy.app.version_string,
        animation=dict(clip='GroundDeckCoverCycle', closed_frame=1, open_frame=31, end_frame=61,
                       mechanism='paired six-stage telescopic covers'),
        observed=['PB26 red-striped retracting covers; altitude-driven legacy descriptor 2..17'],
        inferred=['Telescopic leaf construction, shallow shaft depth, wear and preview timing'],
        legacy_evidence=['PB26.VID paletted preview', 'FRAGILE.LE UpdateLandingPadActivitySpriteFrame 0x44BE0'],
        wear='Explicit edge abrasions and lubricant spots on newly authored leaves',
        runtime='deck: first half of closed/open/closed clip selected by attached ship altitude')
    (OUT/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('PB26_ANIMATED_SOURCE_OK', flush=True)


if __name__ == '__main__':
    main()

