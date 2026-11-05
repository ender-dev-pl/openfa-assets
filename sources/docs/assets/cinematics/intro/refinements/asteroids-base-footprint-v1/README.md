# Asteroids, distant base and footprint — refining pass 1

Editable refinement of cinematic shots B/C/D; original first-scene A and remaining shots are preserved. Previous authored stages remain unchanged.

`refine_sequence.py` takes `--input`, `--out` and `--stage asteroids|surface`. Run it with Blender 4.5 LTS in an isolated authoring workspace, first on the basic full intro with `asteroids`, then on that result with `surface`. It never needs original video pixels as textures. Reference observations are documented in issue #212.

The B GLB is a static midpoint geometric snapshot. `verify_scene.py` reopens the native and independently imports the GLB to compare mesh coverage and world bounds; material baking, animation export and game integration remain outside this pass.

The current full project is `full-intro-refined.blend` (24 fps); standalone `B.blend` and `C.blend` retain individually editable shots. `export_shot.py` extracts a named shot, exports a static midpoint GLB and renders specified original-frame samples. For example, load the full project and run it with `--scene C --out /path/to/work --samples 224,272,300,320,340,368`.

`verify_preservation.py --before BASIC_FULL_PROJECT --after REFINED_FULL_PROJECT --report REPORT` verifies protected geometry/object keyframes, packed authored file images, absence of original audio and contour registration during the footprint-to-logo dissolve. It does not establish final artistic acceptance or shader equivalence.

`render_review.py --out /path/to/review --worker 0 --workers 1` renders original frames 144–412 at 12 fps for review, retaining 24 fps in the native project. Four disjoint workers are supported. Outputs are separated by native SHA256 to avoid mixing successive revisions; the review begins at 12 seconds into the film. Original reference screenshots and comparisons stay outside the public source tree.

After all workers complete, run `python encode_review.py --native full-intro-refined.blend --frames /path/to/review --out /path/to/review.mp4 --report /path/to/report.json`. The encoder validates current native and worker SHA256s, every PNG hash, actual stream dimensions/frame count/duration, absence of audio and the decoded final black frame.

[Silent motion review, original frames 144–412](../../../../../../../gallery/media/cinematics/intro/refinements/asteroids-base-footprint-v1/refined-sequence-review.mp4) · [Authored refined-shot sheet](../../../../../../../gallery/media/cinematics/intro/refinements/asteroids-base-footprint-v1/refined-shots.jpg).

This is a first refining pass, not a claim of exact recovery of the original models or final artistic acceptance. Geological relief, industrial function/detail and step trajectories remain inferred from the low-resolution reference. Earlier checkpoints and the complete basic pass are retained.
