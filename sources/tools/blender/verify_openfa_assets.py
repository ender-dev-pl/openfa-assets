"""Verify the saved portable configuration, editable files and self-contained glTF exports."""
import json
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[2] / "docs/assets/bootstrap-3d"
manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
library = bpy.context.preferences.filepaths.asset_libraries.get("OpenFA original models")
assert library is not None and Path(library.path).resolve() == (root / "models").resolve()
assert bpy.context.scene.render.engine == "CYCLES"
assert bpy.context.scene.render.film_transparent
assert bpy.context.scene.camera.data.type == "ORTHO"
assert bpy.context.scene.render.resolution_x == manifest["render"]["resolution"]
configuration = bpy.utils.user_resource("CONFIG")
assert (Path(configuration) / "startup.blend").is_file()
assert (Path(configuration) / "userpref.blend").is_file()
for asset in manifest["assets"]:
    bpy.ops.wm.open_mainfile(filepath=str(root / asset["blend"]))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    assert len(meshes) == asset["mesh_objects"]
    assert any(collection.asset_data for collection in bpy.data.collections)
    assert bpy.context.scene.camera.data.type == "ORTHO"
    assert bpy.context.scene.render.film_transparent
    assert all(obj.data.materials for obj in meshes)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(root / asset["gltf"]))
    assert any(obj.type == "MESH" for obj in bpy.context.scene.objects)
    assert not any(image.filepath and image.source == "FILE" for image in bpy.data.images)
    print("OPENFA_ASSET_REOPEN_OK", asset["name"])
print("OPENFA_PORTABLE_CONFIG_OK", configuration)
