"""Reopen and render the self-contained airburst; exercise its native controls."""
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/effects/pyro/airborne'
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'explosion.blend'))
scene = bpy.context.scene
collection = bpy.data.collections['Pyro | append this collection']
root = next(obj for obj in collection.objects if obj.type == 'EMPTY')
lobes = [obj for obj in collection.objects if obj.name.startswith('Airborne gas lobe')]
sparks = [obj for obj in collection.objects if obj.name.startswith('Radial spark')]
shell = bpy.data.objects['Expanding fragmented spherical shell']
assert len(lobes) == 9 and len(sparks) == 40
assert collection.asset_data and all(obj.parent == root for obj in collection.objects if obj != root)
assert (scene.frame_start, scene.frame_end, scene.render.fps) == (1, 40, 30)
assert (scene.render.resolution_x, scene.render.resolution_y) == (300, 300)
assert scene.render.film_transparent and scene.render.image_settings.color_mode == 'RGBA'
assert not any(image.source == 'FILE' and not image.packed_file for image in bpy.data.images)
assert shell.modifiers['Irregular spherical wavefront'].texture.type == 'CLOUDS'
material = lobes[0].data.materials[0]
shell_material = shell.data.materials[0]
for frame in [1, 10, 23, 40]:
    scene.frame_set(frame)
    gas = material.evaluated_get(bpy.context.evaluated_depsgraph_get()).node_tree.nodes
    rim = shell_material.evaluated_get(bpy.context.evaluated_depsgraph_get()).node_tree.nodes
    if frame in [1, 40]:
        assert gas['Gas envelope'].inputs[1].default_value == 0
        assert gas['Flame envelope'].inputs[1].default_value == 0
        assert rim['Shell envelope'].inputs[1].default_value == 0
    if frame == 10:
        assert gas['Flame envelope'].inputs[1].default_value > 3
    if frame == 23:
        assert rim['Shell envelope'].inputs[1].default_value > .5
root['fire_intensity'] = 0; root['density'] = 0; root['shell_opacity'] = 0
root.update_tag(refresh={'OBJECT'}); scene.frame_set(16); bpy.context.view_layer.update()
gas = material.evaluated_get(bpy.context.evaluated_depsgraph_get()).node_tree.nodes
rim = shell_material.evaluated_get(bpy.context.evaluated_depsgraph_get()).node_tree.nodes
assert gas['Root fire control'].inputs[1].default_value == 0
assert gas['Root density control'].inputs[1].default_value == 0
assert rim['Root shell opacity'].inputs[1].default_value == 0
for mat in [material, shell_material]:
    assert all(driver.is_valid for driver in mat.node_tree.animation_data.drivers)
root['fire_intensity'] = 1; root['density'] = 2.5; root['shell_opacity'] = 1
root.update_tag(refresh={'OBJECT'}); scene.frame_set(23)
scene.camera.location = (-12, -7, 4)
scene.camera.rotation_euler = (-scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(ROOT / 'side-review.png'); bpy.ops.render.render(write_still=True)
(ROOT / 'blender-verification.json').write_text(json.dumps(dict(blender=bpy.app.version_string,
    reopened=True, native_controls=True, gas_lobes=9, sparks=40, spatial_shell=True,
    alternate_view_rendered=True, external_dependencies=False), indent=2) + '\n')
print('AIRBURST_VERIFY_OK')
