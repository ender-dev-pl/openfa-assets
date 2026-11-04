"""Author five original Blender building studies from documented legacy silhouettes.

Reference pixels are never imported. Parts remain editable and use native materials.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_openfa_assets import beam, box, cylinder, finish, material, setup_scene


def lathe(name, profile, surface, centre=(0, 0), segments=32):
    vertices = [(centre[0] + radius * math.cos(i * math.tau / segments),
                 centre[1] + radius * math.sin(i * math.tau / segments), z)
                for z, radius in profile for i in range(segments)]
    faces = [tuple(reversed(range(segments)))]
    for ring in range(len(profile) - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append((ring * segments + index, ring * segments + next_index,
                          (ring + 1) * segments + next_index, (ring + 1) * segments + index))
    faces.append(tuple(range((len(profile) - 1) * segments, len(profile) * segments)))
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj, name, surface, 0)
    for face in mesh.polygons[1:-1]:
        face.use_smooth = True
    return obj


def dome(name, radius, height, base, surface, centre=(0, 0), ribs=None):
    profile = [(base + height * math.sin(i * math.pi / 18),
                max(0.008, radius * math.cos(i * math.pi / 18))) for i in range(10)]
    obj = lathe(name, profile, surface, centre)
    if ribs is not None:
        def point(phi, theta):
            return (centre[0] + (radius + 0.012) * math.cos(phi) * math.cos(theta),
                    centre[1] + (radius + 0.012) * math.cos(phi) * math.sin(theta),
                    base + (height + 0.012) * math.sin(phi))
        paths = []
        for meridian in range(16):
            theta = meridian * math.tau / 16
            paths.append([point(i * math.pi / 36, theta) for i in range(19)])
        for ring in range(1, 9):
            paths.append([point(ring * math.pi / 18, i * math.tau / 64) for i in range(65)])
        for ring in range(7):
            for sector in range(16):
                paths.append([point((ring + step / 4) * math.pi / 18,
                    (sector + step / 4) * math.tau / 16) for step in range(5)])
        pipe_network(name + " triangular frame", paths, 0.008, ribs)
    return obj


def pipe(name, points, radius, surface):
    return pipe_network(name, [points], radius, surface)


def pipe_network(name, paths, radius, surface):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = radius
    data.bevel_resolution = 2
    for points in paths:
        spline = data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, xyz in zip(spline.points, points):
            point.co = (*xyz, 1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(surface)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def arc(name, radius, z, surface, centre=(0, 0), tube=0.05, start=0, end=math.tau):
    return pipe(name, [(centre[0] + radius * math.cos(start + (end - start) * i / 48),
                        centre[1] + radius * math.sin(start + (end - start) * i / 48), z)
                       for i in range(49)], tube, surface)


def materials():
    return {
        "body": material("Legacy study | grey teal alloy", (0.20, 0.30, 0.28), 0.48, 0.5),
        "purple": material("Legacy study | muted violet alloy", (0.24, 0.20, 0.33), 0.45, 0.48),
        "silver": material("Legacy study | silver structural metal", (0.39, 0.42, 0.41), 0.65, 0.4),
        "dark": material("Legacy study | dark vents", (0.018, 0.026, 0.029), 0.25, 0.6),
        "gold": material("Legacy study | gold copper caps", (0.51, 0.29, 0.055), 0.72, 0.35),
        "bronze": material("Legacy study | bronze tank casing", (0.28, 0.16, 0.07), 0.6, 0.45),
        "blue": material("Legacy study | blue service pipes", (0.015, 0.29, 0.40), 0.5, 0.28),
        "cells": material("Legacy study | violet collector plates", (0.15, 0.12, 0.25), 0.5, 0.3),
        "glass": material("Legacy study | green glazed dome", (0.09, 0.15, 0.085), 0.38, 0.30),
        "light": material("Legacy study | red status lamp", (0.7, 0.025, 0.008), 0.1, emission=1.3),
    }


def cpu(m):
    cylinder("CPU central drum", (0, 0, 0.28), 1.48, 0.56, m["silver"], 48)
    arc("CPU equatorial rim", 1.49, 0.46, m["purple"], tube=0.065)
    dome("CPU gold command dome", 1.45, 0.90, 0.52, m["gold"])
    for index in range(5):
        angle = math.radians(18) + index * math.tau / 5
        x, y = 1.82 * math.cos(angle), 1.82 * math.sin(angle)
        connector = box("CPU radial connector", (x * 0.82, y * 0.82, 0.29), (0.76, 0.40, 0.30), m["purple"], 0.025)
        connector.rotation_euler.z = angle
        cylinder("CPU peripheral pod", (x, y, 0.38), 0.40, 0.56, m["purple"], 24)
        cylinder("CPU pod roof", (x, y, 0.69), 0.43, 0.10, m["silver"], 24)
        arc("CPU pod rim", 0.39, 0.76, m["dark"], (x, y), 0.018)
        cylinder("CPU pod roof hatch", (x, y, 0.77), 0.14, 0.045, m["body"], 16)
        if index in [0, 1, 3]:
            beam("CPU antenna mast", (x, y, 0.78), (x, y, 1.42), 0.018, m["silver"])
    for x in [-0.49, 0.49]:
        cylinder("CPU service gantry foot", (x, -1.91, 0.09), 0.12, 0.18, m["silver"], 12)
        beam("CPU service gantry upright", (x, -1.91, 0.18), (x, -1.91, 0.59), 0.035, m["silver"])
    beam("CPU service gantry crossbar", (-0.63, -1.91, 0.60), (0.63, -1.91, 0.60), 0.04, m["silver"])
    box("CPU service access hatch", (0, -1.45, 0.26), (0.36, 0.09, 0.33), m["dark"], 0.01)


def solar(m):
    lathe("Solar tapered mast", [(0, 0.35), (0.18, 0.36), (2.53, 0.13), (2.72, 0.18)], m["purple"], segments=8)
    cylinder("Solar gold mast collar", (0, 0, 2.35), 0.22, 0.24, m["gold"], 16)
    cylinder("Solar tracking hub", (0, 0, 2.83), 0.37, 0.21, m["purple"], 8)
    cylinder("Solar hub gold cap", (0, 0, 2.96), 0.18, 0.04, m["gold"], 16)
    for index in range(4):
        angle = index * math.tau / 4 + math.pi / 4
        # Four broad radial collector petals, rather than the previous two-wing array.
        wing = box("Solar collector petal", (math.cos(angle) * 0.88, math.sin(angle) * 0.88, 2.85),
                   (1.33, 0.72, 0.06), m["purple"], 0.012)
        wing.rotation_euler.z = angle
        for row in range(4):
            for column in range(2):
                local_x, local_y = 0.36 + row * 0.29, (column - 0.5) * 0.32
                x = local_x * math.cos(angle) - local_y * math.sin(angle)
                y = local_x * math.sin(angle) + local_y * math.cos(angle)
                plate = box("Solar collector cell", (x, y, 2.89), (0.27, 0.30, 0.012), m["cells"], 0.002)
                plate.rotation_euler.z = angle
    for x, y in [(-0.22, -0.22), (0.22, -0.22), (0.22, 0.22), (-0.22, 0.22)]:
        beam("Solar crown pin", (x, y, 2.93), (x, y, 3.22), 0.012, m["silver"])


def air(m):
    lathe("Air processor lower body", [(0, 0.99), (0.15, 1.03), (0.94, 0.98)], m["body"], (0, 0.05))
    lathe("Air processor main tower", [(0.65, 0.89), (1.08, 0.91), (2.21, 0.66), (2.30, 0.62)], m["body"], (0, 0.32))
    dome("Air processor large bronze cap", 0.61, 0.35, 2.26, m["bronze"], (0, 0.32))
    lathe("Air processor auxiliary tower", [(0.35, 0.51), (1.24, 0.46)], m["body"], (-0.40, -0.52))
    dome("Air processor small bronze cap", 0.46, 0.44, 1.23, m["bronze"], (-0.40, -0.52))
    for z in [0.54, 0.76]:
        arc("Air processor blue curved pipe", 1.035, z, m["blue"], (0, 0.05), 0.066,
            math.radians(202), math.radians(338))
    arc("Air processor tower seam", 0.88, 1.10, m["silver"], (0, 0.32), 0.022)
    cylinder("Air processor round service port", (0.59, -0.20, 1.88), 0.16, 0.05, m["bronze"],
             rotation=(math.pi / 2, 0, 0))
    for row in range(3):
        for column in range(2):
            box("Air processor ventilation slit", (0.38 + column * 0.12, -0.44, 1.30 + row * 0.13),
                (0.06, 0.035, 0.09), m["dark"], 0.006)
    box("Air processor status light", (0.11, -0.984, 0.28), (0.055, 0.03, 0.06), m["light"], 0.005)


def hydroponics(m):
    cylinder("Hydroponics foundation ring", (0, 0, 0.12), 1.64, 0.24, m["bronze"], 48)
    arc("Hydroponics dome base rim", 1.62, 0.29, m["silver"], tube=0.045)
    dome("Hydroponics glazed hemisphere", 1.58, 1.48, 0.27, m["glass"], ribs=m["body"])
    box("Hydroponics service annex", (0, -1.66, 0.29), (1.02, 0.77, 0.47), m["body"], 0.025)
    roof = box("Hydroponics annex sloped roof", (0, -1.67, 0.59), (1.13, 0.84, 0.09), m["glass"], 0.012)
    roof.rotation_euler.x = math.radians(12)
    box("Hydroponics entry", (0, -2.05, 0.24), (0.28, 0.03, 0.37), m["dark"], 0.01)
    for x in [-0.81, 0.81]:
        cylinder("Hydroponics annex tank", (x, -1.52, 0.24), 0.24, 0.43, m["body"], 24)
        dome("Hydroponics annex tank dome", 0.24, 0.24, 0.45, m["bronze"], (x, -1.52))
        beam("Hydroponics tank aerial", (x, -1.52, 0.67), (x, -1.52, 0.99), 0.012, m["silver"])
    for angle in [math.radians(20), math.radians(150)]:
        cylinder("Hydroponics rim service stub", (1.61 * math.cos(angle), 1.61 * math.sin(angle), 0.28),
                 0.11, 0.35, m["bronze"], 16)


def hydration(m):
    cylinder("Hydration lower bronze reservoir", (0, 0, 0.78), 0.61, 1.49, m["bronze"], 32)
    for index in range(8):
        angle = index * math.tau / 8
        x, y = 0.88 * math.cos(angle), 0.88 * math.sin(angle)
        cylinder("Hydration external support column", (x, y, 0.89), 0.075, 1.78, m["silver"], 16)
        cylinder("Hydration suspended filter tube", (x * 0.77, y * 0.77, 0.94), 0.07, 0.97, m["body"], 16)
    lathe("Hydration bell shaped head", [(1.58, 0.94), (1.69, 1.01), (1.90, 1.00),
          (2.16, 0.86), (2.42, 0.68), (2.50, 0.57)], m["body"], segments=48)
    arc("Hydration head lower rim", 0.98, 1.69, m["silver"], tube=0.055)
    arc("Hydration head lower gasket", 0.98, 1.60, m["dark"], tube=0.025)
    dome("Hydration gold top cap", 0.57, 0.20, 2.49, m["gold"])
    box("Hydration reservoir instrument", (0.16, -0.619, 0.78), (0.16, 0.06, 0.34), m["dark"], 0.015)
    box("Hydration reservoir status lamp", (0.16, -0.659, 0.87), (0.05, 0.025, 0.07), m["light"], 0.005)


BUILDINGS = [
    ("cpu", cpu, 6.2, 0.80, "20", [0, 16, 38]),
    ("solar", solar, 5.3, 1.62, "04", [0, 5, 11]),
    ("air", air, 4.9, 1.26, "19", [5, 21, 48]),
    ("hydroponics", hydroponics, 5.5, 0.92, "37", [5, 27, 54]),
    ("hydration", hydration, 4.9, 1.30, "38", [0, 21, 43]),
]


def main():
    root = Path(__file__).resolve().parents[2] / "docs/assets/bootstrap-3d/buildings-inspired"
    records = []
    for name, builder, scale, target_z, preview, reference_frames in BUILDINGS:
        output = root / name
        output.mkdir(parents=True, exist_ok=True)
        scene = setup_scene(768, 48)
        scene.name = "OpenFA legacy study | " + name
        scene.camera.data.ortho_scale = scale
        collection = bpy.data.collections.new("OpenFA original " + name + " legacy study")
        scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
        builder(materials())
        collection.asset_mark()
        collection.asset_data.description = "Original editable geometry; visually studied from PB" + preview + ".VID"
        meshes = [obj for obj in collection.objects if obj.type == "MESH"]
        bpy.ops.object.select_all(action="DESELECT")
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.export_scene.gltf(filepath=str(output / "model.glb"), export_format="GLB",
                                  use_selection=True, export_apply=True)
        target = Vector((0, 0, target_z))
        cameras = [("front-quarter", (8, -12, target_z + 10.1)),
                   ("rear-quarter", (-8, 12, target_z + 10.1)), ("top", (0, 0, 16))]
        for view, position in cameras:
            scene.camera.location = position
            scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
            scene.render.filepath = str(output / (view + ".png"))
            bpy.ops.render.render(write_still=True)
        scene.camera.location = cameras[0][1]
        scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(output / "front-quarter.png")
        bpy.ops.wm.save_as_mainfile(filepath=str(output / "model.blend"), compress=True)
        records.append({"name": name, "mesh_objects": len(meshes), "preview": "PB" + preview + ".VID",
                        "reference_frames_zero_based": reference_frames, "surface_body_frame": 1,
                        "surface_shadow_frame": 0, "views": [view for view, _ in cameras]})
        print("OPENFA_BUILDING_RENDER_OK", name)
    (root / "manifest.json").write_text(json.dumps({"blender": bpy.app.version_string,
        "generator": "tools/blender/build_legacy_buildings.py", "imported_geometry_or_textures": [],
        "render": {"resolution": 768, "samples": 48, "engine": "Cycles CPU", "transparent": True},
        "buildings": records}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
