"""Verify saved building source geometry and independently import all five exports."""
import json
from pathlib import Path

import bpy
from mathutils import Vector


root = Path(__file__).resolve().parents[2] / "docs/assets/bootstrap-3d/buildings-inspired"
manifest = json.loads((root / "manifest.json").read_text())
contracts = {
    "cpu": ({"CPU peripheral pod": 5, "CPU gold command dome": 1}, (2.4, 2.4, 1.6)),
    "solar": ({"Solar collector petal": 4, "Solar tapered mast": 1}, (1.8, 1.8, 3.4)),
    "air": ({"Air processor large bronze cap": 1, "Air processor small bronze cap": 1,
             "Air processor blue curved pipe": 2}, (1.3, 1.4, 2.8)),
    "hydroponics": ({"Hydroponics glazed hemisphere": 1, "Hydroponics glazed hemisphere triangular frame": 1,
                     "Hydroponics annex tank": 2}, (1.8, 2.2, 1.9)),
    "hydration": ({"Hydration external support column": 8, "Hydration bell shaped head": 1}, (1.2, 1.2, 2.9)),
}
assert {item["name"] for item in manifest["buildings"]} == set(contracts)
for item in manifest["buildings"]:
    name = item["name"]
    bpy.ops.wm.open_mainfile(filepath=str(root / name / "model.blend"))
    scene = bpy.context.scene
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    assert len(meshes) == item["mesh_objects"]
    assert scene.render.film_transparent and scene.camera.data.type == "ORTHO"
    assert scene.render.resolution_x == 768 and scene.render.resolution_y == 768
    assert any(collection.asset_data for collection in bpy.data.collections)
    assert not any(image.source == "FILE" for image in bpy.data.images)
    features, limits = contracts[name]
    for prefix, expected in features.items():
        # Blender duplicate suffixes are numeric; longer distinct component names do not count.
        parts = [obj for obj in meshes if obj.name == prefix or obj.name.startswith(prefix + ".")]
        assert len(parts) == expected, (name, prefix, len(parts), expected)
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in meshes:
        evaluated = obj.evaluated_get(graph)
        for corner in evaluated.bound_box:
            point = evaluated.matrix_world @ Vector(corner)
            assert abs(point.x) < limits[0] and abs(point.y) < limits[1] and -0.1 < point.z < limits[2], (name, obj.name, point)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(root / name / "model.glb"))
    assert any(obj.type == "MESH" for obj in bpy.context.scene.objects)
    assert not any(image.source == "FILE" for image in bpy.data.images)
    print("OPENFA_BUILDING_REOPEN_OK", name, item["mesh_objects"])
