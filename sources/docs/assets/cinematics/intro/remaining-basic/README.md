# Remaining intro — basic pass

The scene plan covers original frames 413–1873. Scenes are authored sequentially, with a commit and push per major story milestone. `shot-plan.json` records which IDs are currently `basic_verified`; planned IDs are not yet buildable.

This pass establishes silhouettes, framing, major props and coarse keyframed motion. Facial likeness, phoneme lip sync, detailed materials, precise typography and effects are deferred. The officer's jaw motion is a placeholder, not recovered speech animation.

Build one implemented scene outside canonical sources:

```sh
blender --background --python build_scene.py -- --scene F --out /path/to/ignored/authoring-workspace/F
```

The native project retains editable text, separate named body parts and animation controls. The GLB is a static midpoint geometry snapshot; procedural material baking and real-time animation integration are deferred. `verify_scene.py` reopens the native source and independently imports the GLB, checks mesh coverage and world bounds. Representative rendered views are stored under `gallery/media/cinematics/intro/remaining-basic/`.

The source reference and original soundtrack remain local, following repository publication policy. A final assembly is added after all basic scenes have been verified; the completed first sequence remains preserved separately.

## Complete assembly

All 20 planned shots are implemented and runtime-verified. `full-intro-basic.blend` combines them with the preserved first sequence: 24 scene strips, three original cross-dissolves, 3748 frames at 24 fps (156.1667 seconds), 640×480 output with the established letterbox. Each new shot also remains independently editable under `scenes/`.

`assemble_intro.py --out /path/to/work/full-intro-basic.blend` rebuilds the assembly in Blender from committed sources. It encodes the historical first-sequence worker's nebula visibility rule as native animation keys; earlier source files and model geometry remain unchanged. `verify_assembly.py --report /path/to/report.json` checks the reopened full project.

For a lightweight review, open the assembled native and run `render_animatic_worker.py --out /path/to/frames`. Optional `--worker N --workers COUNT` divides the 937 samples across processes. Then run `encode_animatic.py --frames /path/to/frames --native full-intro-basic.blend --output /path/to/animatic.mp4 --report /path/to/report.json` with Python and ffmpeg available. This validates every worker frame hash, encodes a silent 320×240/6 fps proxy, and checks the actual video stream. The canonical editable animation remains 24 fps. Review renders belong outside `sources/`.

The public sources are self-contained and require neither the original installation nor its soundtrack. The ending holds the emblem through original frame 1873. Transmission bridges use procedural static; visible underlays and exact distortion remain for refining. Lab equipment, human/alien likeness, speech, typography, explosions and the final emblem are deliberate geometric approximations. The static GLBs are interchange checks, not an animated real-time game deliverable.
