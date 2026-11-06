"""Original mesh study of the PS05 transporter silhouette; no source pixels or meshes are imported."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_openfa_assets import beam, box, cylinder, finish, material, setup_scene


def loft(name, sections, surface, bevel=0.012):
    # Clockwise clipped-rectangle cross sections (x, half-width, bottom, top).
    vertices = []
    for x, width, bottom, top in sections:
        height = top - bottom
        vertices.extend((x, y, z) for y, z in [
            (-width * 0.72, bottom), (width * 0.72, bottom),
            (width, bottom + height * 0.22), (width, top - height * 0.26),
            (width * 0.66, top), (-width * 0.66, top),
            (-width, top - height * 0.26), (-width, bottom + height * 0.22),
        ])
    faces = [tuple(reversed(range(8))), tuple(range((len(sections) - 1) * 8, len(sections) * 8))]
    for ring in range(len(sections) - 1):
        for corner in range(8):
            following = (corner + 1) % 8
            faces.append((ring * 8 + corner, ring * 8 + following,
                          (ring + 1) * 8 + following, (ring + 1) * 8 + corner))
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    finish(obj, name, surface, 0)
    if bevel:
        modifier = obj.modifiers.new("Narrow planar edge chamfer", "BEVEL")
        modifier.width = bevel
        modifier.segments = 1
        obj.modifiers.new("Weighted panel normals", "WEIGHTED_NORMAL")
    return obj


def engine(name, x, y, z, radius, m):
    rotation = (0, math.pi / 2, 0)
    cylinder(name + " mounting", (x + 0.12, y, z), radius * 1.22, 0.22, m["rim"], rotation=rotation)
    cylinder(name + " dark throat", (x - 0.04, y, z), radius, 0.18, m["dark"], rotation=rotation)
    for offset, ring_radius in [(0, radius), (-0.09, radius * 0.75), (-0.11, radius * 0.44)]:
        bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=8,
            major_radius=ring_radius, minor_radius=radius * 0.12,
            location=(x + offset - 0.13, y, z), rotation=rotation)
        finish(bpy.context.object, name + " copper nozzle ring", m["orange"], 0)
    cylinder(name + " inner core", (x - 0.18, y, z), radius * 0.24, 0.02, m["ember"], rotation=rotation)


def forward_opening(hull, m):
    cutter = box("Temporary forward cavity cutter", (0.92, 0, 1.32), (1.44, 1.04, 0.92), m["dark"], 0)
    bpy.context.view_layer.objects.active = hull
    modifier = hull.modifiers.new("True forward undercut", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.ops.object.modifier_move_to_index(modifier=modifier.name, index=0)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    box("Recessed forward bulkhead", (0.23, 0, 1.12), (0.04, 1.0, 0.50), m["cavity"], 0.01)
    box("Recessed forward floor", (0.72, 0, 0.86), (0.94, 1.0, 0.035), m["cavity"], 0.008)
    box("Forward overhang spine", (0.74, 0, 1.46), (0.94, 0.26, 0.18), m["panel"], 0.025)
    box("Forward spine copper cap", (1.17, 0, 1.47), (0.12, 0.28, 0.20), m["orange"], 0.015)


def build():
    m = {
        "hull": material("Inspired | warm grey alloy", (0.18, 0.17, 0.22), 0.4, 0.55),
        "panel": material("Inspired | light service panels", (0.29, 0.28, 0.34), 0.4, 0.5),
        "dark": material("Inspired | graphite recesses", (0.022, 0.027, 0.034), 0.5),
        "rim": material("Inspired | dark steel rims", (0.15, 0.16, 0.19), 0.8),
        "red": material("Inspired | vermilion identification stripe", (0.63, 0.055, 0.035), 0.3),
        "orange": material("Inspired | copper engine baffles", (0.72, 0.29, 0.035), 0.75),
        "ember": material("Inspired | low engine glow", (0.9, 0.24, 0.015), 0.1, emission=0.5),
        "cavity": material("Inspired | deep unglazed service recess", (0.008, 0.007, 0.009), 0.0, 0.85),
    }
    hull = loft("Broad tapered cargo hull", [(-1.85, 1.39, 0.51, 1.47), (-1.35, 1.46, 0.48, 1.53),
         (0.6, 1.18, 0.52, 1.39), (1.05, 0.96, 0.58, 1.25)], m["hull"])
    loft("Raised longitudinal spine", [(-1.8, 0.56, 1.36, 1.7), (-0.7, 0.59, 1.38, 1.64),
         (0.53, 0.43, 1.25, 1.48)], m["panel"])
    loft("Lower keel", [(-1.9, 0.68, 0.34, 0.65), (0.9, 0.54, 0.42, 0.69)], m["dark"])
    for sign in [-1, 1]:
        # A continuous red belt, not separate container pods.
        stripe = box("Continuous red side stripe", (-0.37, sign * 1.315, 0.91), (2.85, 0.035, 0.17), m["red"], 0.01)
        stripe.rotation_euler.z = -sign * math.radians(5.9)
        for index in range(4):
            x = -1.25 + index * 0.53
            y = sign * (1.35 - (x + 1.25) * 0.10)
            panel = box("Inset sloped side plate", (x, y, 1.22), (0.43, 0.055, 0.33), m["panel"], 0.018)
            panel.rotation_euler.x = sign * math.radians(27)
            panel.rotation_euler.z = -sign * math.radians(5.9)
            beam("Service seam", (x - 0.22, y, 1.04), (x - 0.22, y - sign * 0.12, 1.38), 0.012, m["rim"])
        box("Top copper utility rail", (-0.62, sign * 0.66, 1.56), (1.9, 0.08, 0.055), m["orange"], 0.012)
    # Short recessed neck and separate flattened prow reproduce the distinctive outline.
    loft("Recessed forward neck", [(0.7, 0.32, 0.62, 0.82), (1.66, 0.28, 0.66, 0.85)], m["rim"])
    forward_opening(hull, m)
    loft("Flattened separate nose cap", [(1.35, 0.31, 0.72, 0.91), (1.65, 0.60, 0.64, 1.04),
         (2.15, 0.53, 0.67, 0.97), (2.50, 0.18, 0.75, 0.85), (2.60, 0.03, 0.78, 0.82)], m["hull"])
    hatch = box("Prow service hatch", (1.89, 0, 1.015), (0.37, 0.30, 0.022), m["panel"], 0.008)
    hatch.rotation_euler.y = math.radians(8)
    for sign in [-1, 1]:
        beam("Prow sensor whisker", (2.26, sign * 0.18, 0.88), (2.68, sign * 0.23, 0.9), 0.018, m["rim"])
        box("Nose identification slash", (2.12, sign * 0.39, 0.98), (0.21, 0.06, 0.025), m["red"], 0.01)
    loft("Rear engine bridge", [(-2.30, 1.16, 0.61, 1.66), (-1.55, 1.29, 0.62, 1.72)], m["hull"])
    for sign in [-1, 1]:
        shoulder = loft("Faceted rear drive shoulder", [(-2.43, 0.44, 0.70, 1.49),
            (-2.18, 0.62, 0.62, 1.69), (-1.55, 0.55, 0.68, 1.62)], m["hull"])
        shoulder.location.y = sign * 0.83
        engine("Auxiliary drive", -2.40, sign * 0.70, 1.10, 0.16, m)
    engine("Main drive", -2.45, 0, 0.98, 0.43, m)
    for x in [-1.22, -0.96, -0.70, -0.44]:
        box("Dorsal cooling slit", (x, 0, 1.666), (0.12, 0.5, 0.022), m["dark"], 0.008)
    beam("Dorsal aerial", (0.1, 0, 1.54), (-0.03, 0, 1.98), 0.018, m["rim"])
    box("Dorsal transmitter", (0.05, 0, 1.54), (0.25, 0.24, 0.12), m["rim"], 0.04)


def main():
    output = Path(__file__).resolve().parents[2] / "docs/assets/bootstrap-3d/transporter-inspired"
    output.mkdir(parents=True, exist_ok=True)
    scene = setup_scene(768, 64)
    scene.name = "OpenFA | original-inspired transporter"
    scene.camera.data.ortho_scale = 7.0
    collection = bpy.data.collections.new("OpenFA transporter silhouette study")
    scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    build()
    collection.asset_mark()
    collection.asset_data.description = "Original geometry inspired by observed PS05 outline. No legacy pixels or meshes."
    meshes = [obj for obj in collection.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.export_scene.gltf(filepath=str(output / "transporter.glb"), export_format="GLB",
                              use_selection=True, export_apply=True)
    target = Vector((0, 0, 1))
    views = [("front-quarter", (9, -12, 9)), ("rear-quarter", (-9, -12, 9)),
             ("side", (0, -15, 5)), ("front", (15, 0, 5)),
             ("rear", (-15, 0, 5)), ("top", (0, 0, 16))]
    for name, location in views:
        scene.camera.location = location
        scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(output / (name + ".png"))
        bpy.ops.render.render(write_still=True)
    scene.camera.location = views[0][1]
    scene.camera.rotation_euler = (target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(output / "front-quarter.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "transporter.blend"), compress=True)
    (output / "manifest.json").write_text(json.dumps({"blender": bpy.app.version_string,
        "generator": "tools/blender/build_transporter_inspired.py", "reference_only": ["PS05.VID", "PS5C.256"],
        "imported_geometry_or_textures": [], "mesh_objects": len(meshes), "views": [name for name, _ in views],
        "reference_frames_zero_based": {"forward_opening": 12, "rear_exhausts": 35},
        "geometry_revision": 3, "main_nozzles": 1, "auxiliary_nozzles": 2,
        "body_style": "flat-faced hull, faceted rear shoulders, wedge prow, narrow single-segment chamfers",
        "resolution": 768, "samples": 64, "engine": "Cycles CPU", "transparent": True}, indent=2) + "\n", encoding="utf-8")
    print("OPENFA_TRANSPORTER_STUDY_OK", output)


if __name__ == "__main__":
    main()
