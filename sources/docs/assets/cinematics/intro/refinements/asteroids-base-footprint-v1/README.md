# Asteroids, distant base and footprint — refining pass 1

Editable refinement of cinematic shots B/C/D; original first-scene A and remaining shots are preserved. Previous authored stages remain unchanged.

`refine_sequence.py` takes `--input`, `--out` and `--stage asteroids|surface`. Run it with Blender 4.5 LTS in an isolated authoring workspace, first on the basic full intro with `asteroids`, then on that result with `surface`. It never needs original video pixels as textures. Reference observations are documented in issue #212.

The B GLB is a static midpoint geometric snapshot. `verify_scene.py` reopens the native and independently imports the GLB to compare mesh coverage and world bounds; material baking, animation export and game integration remain outside this pass.
