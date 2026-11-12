"""Verify reusable saved volume assets in a clean Blender process."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/effects/pyro'
results = []
for variant in ['compact', 'rising', 'asymmetric']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / variant / 'explosion.blend'))
    scene = bpy.context.scene
    collection = bpy.data.collections['Pyro | append this collection']
    root = next(obj for obj in collection.objects if obj.type == 'EMPTY')
    clouds = [obj for obj in collection.objects if obj.name.startswith('Pyro cloud')]
    assert len(clouds) == 10 and collection.asset_data is not None
    assert len([obj for obj in collection.objects if obj.name.startswith('Ember')]) == 32
    assert all(obj.parent == root for obj in collection.objects if obj != root)
    assert (scene.frame_start, scene.frame_end, scene.render.fps) == (1, 96, 24)
    assert (scene.render.resolution_x, scene.render.resolution_y) == (300, 300)
    assert scene.render.film_transparent and scene.render.image_settings.color_mode == 'RGBA'
    assert not any(image.source == 'FILE' and not image.packed_file for image in bpy.data.images)
    mat = clouds[0].data.materials[0]
    for frame in [1, 16, 48, 96]:
        scene.frame_set(frame)
        evaluated = mat.evaluated_get(bpy.context.evaluated_depsgraph_get())
        density = evaluated.node_tree.nodes['Density envelope / dissipate'].inputs[1].default_value
        fire = evaluated.node_tree.nodes['Flame emission envelope'].inputs[1].default_value
        if frame in [1, 96]:
            assert abs(density) < 1e-6 and abs(fire) < 1e-6
        if frame == 16:
            assert density > .5 and fire > 0
        if frame == 48:
            assert density > 0 and fire < .1
    root['fire_intensity'] = 0.0; root['density'] = .5
    root.update_tag(refresh={'OBJECT'})
    scene.frame_set(16)
    bpy.context.view_layer.update()
    evaluated = mat.evaluated_get(bpy.context.evaluated_depsgraph_get())
    assert evaluated.node_tree.nodes['Root fire intensity control'].inputs[1].default_value == 0
    assert evaluated.node_tree.nodes['Root density control'].inputs[1].default_value == .5
    assert not any(not driver.is_valid for driver in mat.node_tree.animation_data.drivers)
    root['fire_intensity'] = 1.0; root['density'] = 3.0
    root.update_tag(refresh={'OBJECT'})
    scene.frame_set(20)
    scene.camera.location = (-14, -8, 7)
    scene.camera.rotation_euler = (Vector((0, 0, 2.8)) - scene.camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(ROOT / variant / 'side-review.png')
    bpy.ops.render.render(write_still=True)
    results.append(dict(variant=variant, reopened=True, clouds=10, embers=32, root_controls=True,
                        external_dependencies=False, fire_to_smoke=True, alternate_view_rendered=True))
(ROOT / 'blender-verification.json').write_text(json.dumps(dict(blender=bpy.app.version_string, results=results), indent=2) + '\n')
print('PYRO_VERIFY_OK', len(results))
