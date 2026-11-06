"""Build original editable OpenFA models and an orthographic transparent sprite rig.

Run with the portable launcher: -Background -PythonScript this_file -ScriptArguments @('--configure')
All geometry/materials are authored here; no legacy or external assets are read.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def material(name, colour, metal=0.0, roughness=0.4, emission=0.0):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*colour, 1)
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*colour, 1)
    shader.inputs["Metallic"].default_value = metal
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Emission Color"].default_value = (*colour, 1)
    shader.inputs["Emission Strength"].default_value = emission
    return result


def finish(obj, name, surface, bevel=0.04):
    obj.name = name
    obj.data.materials.append(surface)
    if bevel:
        modifier = obj.modifiers.new("Manufactured edge bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def box(name, location, dimensions, surface, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, surface, bevel)


def cylinder(name, location, radius, depth, surface, vertices=32, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                      location=location, rotation=rotation)
    return finish(bpy.context.object, name, surface, min(0.035, radius / 5))


def beam(name, start, end, radius, surface):
    delta = Vector(end) - Vector(start)
    obj = cylinder(name, (Vector(start) + Vector(end)) / 2, radius, delta.length, surface, 12)
    obj.rotation_euler = delta.to_track_quat("Z", "Y").to_euler()
    return obj


def materials():
    return {
        "teal": material("OpenFA | teal enamel", (0.045, 0.22, 0.25), 0.65),
        "dark": material("OpenFA | graphite frame", (0.025, 0.04, 0.055), 0.75),
        "silver": material("OpenFA | brushed alloy", (0.48, 0.57, 0.59), 0.8),
        "copper": material("OpenFA | copper fittings", (0.48, 0.20, 0.055), 0.8),
        "amber": material("OpenFA | amber status lights", (1.0, 0.32, 0.025), 0.2, emission=2),
        "blue": material("OpenFA | photovoltaic cells", (0.015, 0.07, 0.24), 0.6, 0.22),
        "glass": material("OpenFA | cyan console glass", (0.015, 0.5, 0.62), 0.45, 0.18, 0.3),
    }


def cpu(m):
    cylinder("Octagonal foundation", (0, 0, 0.16), 1.85, 0.32, m["dark"], 8)
    cylinder("Teal service deck", (0, 0, 0.45), 1.63, 0.4, m["teal"], 8)
    cylinder("Copper deck rim", (0, 0, 0.67), 1.58, 0.08, m["copper"], 8)
    cylinder("Central control drum", (0, 0, 1.0), 0.85, 0.65, m["silver"], 12)
    cylinder("Command glass crown", (0, 0, 1.39), 0.76, 0.22, m["glass"], 12)
    cylinder("Crown roof", (0, 0, 1.55), 0.9, 0.13, m["teal"], 12)
    cylinder("Antenna mast", (0, 0, 2.05), 0.055, 0.95, m["silver"], 12)
    cylinder("Mast signal light", (0, 0, 2.56), 0.095, 0.08, m["amber"], 16)
    for index in range(6):
        angle = index * math.tau / 6
        x, y = math.cos(angle), math.sin(angle)
        module = box("Peripheral service module", (x * 1.28, y * 1.28, 0.9), (0.6, 0.65, 0.5), m["teal"])
        module.rotation_euler.z = angle
        cylinder("Service vent", (x * 1.28, y * 1.28, 1.23), 0.16, 0.22, m["silver"], 16)
        cylinder("Vent cap", (x * 1.28, y * 1.28, 1.37), 0.19, 0.08, m["dark"], 16)
        lamp = box("Service status strip", (x * 1.55, y * 1.55, 0.87), (0.08, 0.3, 0.1), m["amber"], 0.01)
        lamp.rotation_euler.z = angle
    for index in range(4):
        box("Access step", (0, -1.72 - index * 0.13, 0.28 - index * 0.055), (0.7, 0.15, 0.12), m["silver"], 0.015)


def solar(m):
    cylinder("Solar foundation", (0, 0, 0.1), 0.65, 0.2, m["dark"], 8)
    cylinder("Tracking pedestal", (0, 0, 0.65), 0.18, 1.0, m["silver"], 16)
    box("Tracking gearbox", (0, 0, 1.18), (0.5, 0.5, 0.35), m["teal"])
    beam("Panel crossarm", (-2, 0, 1.38), (2, 0, 1.38), 0.06, m["copper"])
    for sign in [-1, 1]:
        centre = sign * 1.25
        wing = box("Solar wing frame", (centre, 0, 1.42), (1.85, 1.8, 0.12), m["silver"], 0.025)
        tilt = math.radians(18)
        wing.rotation_euler.x = tilt
        for column in range(4):
            for row in range(4):
                local_y = (row - 1.5) * 0.42
                x = centre + (column - 1.5) * 0.43
                cell = box("Photovoltaic cell", (x, local_y * math.cos(tilt) - 0.09 * math.sin(tilt),
                           1.42 + local_y * math.sin(tilt) + 0.09 * math.cos(tilt)),
                           (0.405, 0.395, 0.025), m["blue"], 0.008)
                cell.rotation_euler.x = tilt
        beam("Solar support strut", (0, 0, 0.7), (centre, 0, 1.32), 0.04, m["silver"])
    box("Tracking controller", (0, -0.27, 1.16), (0.26, 0.08, 0.16), m["amber"], 0.01)


def transporter(m):
    box("Transport spine", (0, 0, 0.8), (4.3, 0.65, 0.55), m["dark"], 0.15)
    box("Forward crew module", (1.6, 0, 1.05), (1.25, 1.15, 0.65), m["teal"], 0.25)
    box("Forward console glazing", (2.09, 0, 1.25), (0.24, 0.8, 0.25), m["glass"], 0.08)
    for side in [-1, 1]:
        for index in range(3):
            x = -1.1 + index * 0.9
            box("Independent cargo pod", (x, side * 0.62, 0.91), (0.8, 0.65, 0.85), m["silver"], 0.1)
            for offset in [-0.28, 0.28]:
                box("Cargo restraint band", (x + offset, side * 0.62, 0.93), (0.08, 0.71, 0.9), m["copper"], 0.025)
            box("Pod identifier light", (x, side * 0.96, 1.13), (0.28, 0.025, 0.09), m["amber"], 0.005)
        rotation = (0, math.pi / 2, 0)
        cylinder("Drive nacelle", (-1.91, side * 0.57, 0.9), 0.28, 0.8, m["teal"], rotation=rotation)
        cylinder("Drive nozzle", (-2.36, side * 0.57, 0.9), 0.3, 0.16, m["dark"], rotation=rotation)
        cylinder("Drive core", (-2.46, side * 0.57, 0.9), 0.19, 0.02, m["glass"], rotation=rotation)
        for x in [-1.1, 1.2]:
            beam("Landing leg", (x, side * 0.4, 0.7), (x, side * 0.8, 0.25), 0.05, m["silver"])
            box("Landing pad", (x, side * 0.8, 0.16), (0.5, 0.35, 0.1), m["dark"], 0.03)


def setup_scene(resolution, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("OpenFA ambient")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.19, 0.24, 0.3, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    target = Vector((0, 0, 1))
    bpy.ops.object.camera_add(location=(8, -12, 1 + math.hypot(8, 12) * math.tan(math.radians(30))))
    camera = bpy.context.object
    camera.name = "OpenFA orthographic 30 degree camera"
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 6.4
    scene.camera = camera
    for name, position, energy, colour, size in [
        ("Soft key", (-3, -5, 8), 1100, (1, 0.91, 0.78), 5),
        ("Cool fill", (5, -1, 5), 650, (0.65, 0.83, 1), 4),
        ("Copper rim", (1, 5, 6), 900, (1, 0.66, 0.35), 3),
    ]:
        bpy.ops.object.light_add(type="AREA", location=position)
        light = bpy.context.object
        light.name = name
        light.data.energy, light.data.color, light.data.size = energy, colour, size
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    return scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "docs/assets/bootstrap-3d")
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--configure", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for folder in ["models", "renders", "exports"]:
        (output / folder).mkdir(exist_ok=True)
    setup_scene(args.resolution, args.samples)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "openfa-sprite-template.blend"), compress=True)
    if args.configure:
        preferences = bpy.context.preferences
        preferences.filepaths.save_version = 0
        library = preferences.filepaths.asset_libraries.get("OpenFA original models")
        if library is None:
            library = preferences.filepaths.asset_libraries.new(name="OpenFA original models")
        library.path = str(output / "models")
        bpy.ops.wm.save_userpref()
        bpy.ops.wm.save_homefile()
    records = []
    for name, builder in [("cpu", cpu), ("solar", solar), ("transporter", transporter)]:
        scene = setup_scene(args.resolution, args.samples)
        scene.name = "OpenFA | " + name
        collection = bpy.data.collections.new("OpenFA original " + name)
        scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        builder(materials())
        collection.asset_mark()
        collection.asset_data.description = "Original editable OpenFA " + name + "; generated by build_openfa_assets.py"
        meshes = [obj for obj in collection.objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action="DESELECT")
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        scene.render.filepath = str(output / "renders" / (name + ".png"))
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "models" / (name + ".blend")), compress=True)
        bpy.ops.export_scene.gltf(filepath=str(output / "exports" / (name + ".glb")),
                                  export_format="GLB", use_selection=True, export_apply=True)
        bpy.ops.render.render(write_still=True)
        records.append({"name": name, "mesh_objects": len(meshes), "blend": "models/" + name + ".blend",
                        "gltf": "exports/" + name + ".glb", "sprite": "renders/" + name + ".png"})
    (output / "manifest.json").write_text(json.dumps({"blender": bpy.app.version_string,
        "generator": "tools/blender/build_openfa_assets.py", "external_inputs": [],
        "camera": {"projection": "orthographic", "elevation_degrees": 30, "scale": 6.4},
        "render": {"engine": "Cycles CPU", "samples": args.samples, "resolution": args.resolution,
                   "transparent": True}, "assets": records}, indent=2) + "\n", encoding="utf-8")
    print("OPENFA_ASSET_BUILD_OK", output)


if __name__ == "__main__":
    main()
