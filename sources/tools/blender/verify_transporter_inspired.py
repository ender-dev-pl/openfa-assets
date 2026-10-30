"""Reopen the authored transporter study and its self-contained interchange export."""
import json
from pathlib import Path

import bpy
from mathutils import Vector


root = Path(__file__).resolve().parents[2] / "docs/assets/bootstrap-3d/transporter-inspired"
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=str(root / "transporter.blend"))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
assert len(meshes) == manifest["mesh_objects"]
assert any(collection.asset_data for collection in bpy.data.collections)
assert bpy.context.scene.camera.data.type == "ORTHO"
assert bpy.context.scene.render.film_transparent
assert bpy.context.scene.render.resolution_x == 768
assert all(obj.data.materials and len(obj.data.polygons) > 0 for obj in meshes)
assert not any(image.source == "FILE" for image in bpy.data.images)
for component in ["Broad tapered cargo hull", "Flattened separate nose cap", "Rear engine bridge",
                  "Continuous red side stripe", "Main drive dark throat", "Auxiliary drive dark throat"]:
    assert any(obj.name.startswith(component) for obj in meshes), component
main = [obj for obj in meshes if obj.name.startswith("Main drive dark throat")]
auxiliary = [obj for obj in meshes if obj.name.startswith("Auxiliary drive dark throat")]
assert len(main) == 1 and abs(main[0].location.y) < 0.001
assert len(auxiliary) == 2 and auxiliary[0].location.y * auxiliary[1].location.y < 0
assert all(obj.dimensions.y < main[0].dimensions.y / 2 for obj in auxiliary)
assert not any(obj.name.startswith("Dark cockpit window") or "cutter" in obj.name for obj in meshes)
hull = bpy.data.objects["Broad tapered cargo hull"]
hit, point, _, _ = hull.ray_cast(Vector((2, 0, 1.1)), Vector((-1, 0, 0)))
assert hit and point.x < 0.35, "The central front opening must penetrate the hull, not just paint its surface."
assert any(obj.name == "Forward overhang spine" for obj in meshes)
faceted = [bpy.data.objects["Flattened separate nose cap"], bpy.data.objects["Rear engine bridge"]]
faceted += [obj for obj in meshes if obj.name.startswith("Faceted rear drive shoulder")]
assert len(faceted) == 4
for obj in faceted:
    assert len(obj.data.polygons) <= 40 and not any(face.use_smooth for face in obj.data.polygons)
    bevels = [modifier for modifier in obj.modifiers if modifier.type == "BEVEL"]
    assert bevels and all(modifier.width <= 0.015 and modifier.segments == 1 for modifier in bevels)
assert not any(obj.name.startswith("Rounded rear drive shoulder") for obj in meshes)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root / "transporter.glb"))
assert any(obj.type == "MESH" for obj in bpy.context.scene.objects)
assert not any(image.source == "FILE" for image in bpy.data.images)
print("OPENFA_TRANSPORTER_REOPEN_OK", manifest["mesh_objects"], "mesh objects")
