# Remaining intro — basic pass

The scene plan covers original frames 413–1873. Scenes are authored sequentially, with a commit and push per major story milestone. `shot-plan.json` records which IDs are currently `basic_verified`; planned IDs are not yet buildable.

This pass establishes silhouettes, framing, major props and coarse keyframed motion. Facial likeness, phoneme lip sync, detailed materials, precise typography and effects are deferred. The officer's jaw motion is a placeholder, not recovered speech animation.

Build one implemented scene outside canonical sources:

```sh
blender --background --python build_scene.py -- --scene F --out /path/to/ignored/authoring-workspace/F
```

The native project retains editable text, separate named body parts and animation controls. The GLB is a static midpoint geometry snapshot; procedural material baking and real-time animation integration are deferred. `verify_scene.py` reopens the native source and independently imports the GLB, checks mesh coverage and world bounds. Representative rendered views are stored under `gallery/media/cinematics/intro/remaining-basic/`.

The source reference and original soundtrack remain local, following repository publication policy. A final assembly is added after all basic scenes have been verified; the completed first sequence remains preserved separately.
