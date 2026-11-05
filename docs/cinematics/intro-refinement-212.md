# Asteroid / base / footprint refining

Issue [#212](https://github.com/ender-dev-pl/openfa-assets/issues/212) refines scenes B/C/D of the opening cinematic. Completed scene A and later scenes are preserved. Earlier basic passes remain available.

The asteroid pass replaces random composition with measured active-picture anchors from original frame 176 (640×262 corrected presentation), fractures the shared rock meshes, and reduces excessively bright stars. The source reference remains local; authored geometry and procedural materials are published.

Runtime reports describe actual Blender native reopen and independent static GLB imports. These exports are midpoint geometric checks, not final game integration or material-baking acceptance.

The surface pass replaces the circular terrain bowl with layered mesas and eroded valley walls, adjusts the early camera horizon, places the reduced distant complex on an elevated apron, and adds cylindrical housings, fins, service panels, pipes and lamps. Boot panels/fasteners remain separate objects. The step enters from the right with staggered timing, revealing a tapered sole relief and raised outlined lettering. The end-card contour is reprojected from the footprint for registered cross-dissolves.

The preservation check compares geometry and object keyframes in 21 protected scenes (including completed scene A and all later basic shots), and numerically checks footprint/end-card contour registration at three frames during the dissolve. Rendered artistic comparisons remain separate from those structural checks.

Milestones pushed on `feat/intro-first-sequence-reconstruction`: `7c97924` (asteroids), `1bfcd7d` (base/terrain/step/footprint/end-card/full editable project). A silent 640×480/12 fps review covers original frames 144–412; the native project remains 24 fps. Source references and legacy/before/after comparison sheets remain local. [Source/rebuild guide](../../sources/docs/assets/cinematics/intro/refinements/asteroids-base-footprint-v1/README.md).

## Cinematic iteration 2

The separate `cinematic-v2` checkpoint adds high-resolution procedural basalt/metal materials, grazing cold sunlight, broad bounce, warm industrial light spill, footprint edge lighting and surface-seated geometric fragments. It preserves earlier checkpoints and provides a B/C/D excerpt with a 1920×1440 letterbox master at 24 fps. Three stills are rendered at 32 samples with denoising; native production settings use 128. No full-HD moving video or baked game material acceptance is claimed. See [source and rendering instructions](../../sources/docs/assets/cinematics/intro/refinements/cinematic-v2/README.md).
