# RI09 Construction Unit: canonical source remaster

Tracking: openfa-assets #253 and per-building #40. Preserve `openfa:building/legacy/048`, definition class 25, footprint 4x4 and construction updates 30. Original functional record 909 establishes ship construction. Culture record 18 describes ergonomic, elegant Rigellian architecture. These records do not specify a construction-machine cycle.

## Reference and concept feedback

Correctly paletted surface and catalogue phases 0/10/20/30/40 show two open annular platforms, a raised circular hood with depressed top feature, central red inset, small brass fittings, paired rear uprights, green internal equipment and a small front inspection detail. Catalogue phases reveal/highlight one spatial presentation rather than proving mechanical movement. Current game selector/directional-ID rules exclude this ID; shared building-construction presentation is separate from machine operation.

One actual built-in ImageGen request used the real surface and catalogue colour phase20. Its exact prompt is `ri09-concept-prompt-1.txt`; the public concept is `gallery/media/concepts/rigellian/ri09-review-1.png`. It keeps the main anatomy, but invents extra internal posts and hood supports, replaces recessed channels with raised ribs and broadens the hood depression. Those differences are not adopted. Exact post counts, rear mounting runners, recess depth, front-rib interpretation and hidden connections remain authored interpretation. Original pixels stay private.

## One current source and runtime pair

Use `sources/objects/rigellian/construction-unit/model.blend` and `model.glb` across gameplay, build menu and SciTek. Earlier studies remain historical, outside the single current inventory selection. The latest reference-refined revision-three source is retained, including the circular hood depression and paired rear uprights corrected during earlier comparison.

All six mapped castings retain exact evaluated geometry, with protected-surface error 0.0: two annuli, front joining bridge, support spine, central column and hood. Existing actual channels, measured casting dents and independently authored wear remain. Only four green equipment-post meshes receive tessellation reduction. Total evaluated triangles fall from 60,124 to 49,372; maximum sampled bidirectional old/new vertex-to-surface error remains below 9.14e-7 source units. This sampled measure is not an exhaustive Hausdorff bound.

There are 46 editable physical components, eight used materials and four embedded maps. These explicit costs do not certify batching or Android frame rate. Root is identity `PlacementRoot`, local -Y forward, +Z dorsal, ground Z0. Bounds are [-1.800000, -0.950000, 0] to [1.800000, 1.020000, 1.470000]. Nominal footprint is not a calibrated scene-to-game scale. The source is static with no clips; a shipbuilding sequence, construction/damage variants and client state/mount calibration remain separate.

## Actual saved-native and independent GLB validation

Blender 4.5.15 reopens the saved native model and independently imports GLB. All 46 components have positive closed welded physical surfaces. The existing anatomy assertions remain intact: rays through both annular centres miss every mesh, ten channels have actual depth and embedded backings, casting dents remain measurable, the hood recess meets its floor, and the column overlaps the spine and hood. New checks use rays through actual solids to confirm overlapping post/runner and post/pale-cap intervals for all four green posts after reduction. A connected sampled contact graph supplements these checks without claiming exhaustive solid intersections.

Full casting colour/roughness pixels and every mapped corner on the six castings satisfy their existing planar/cylindrical UV contracts. Component names, triangle counts and used materials agree. Maximum bidirectional native/import surface error is below 1.36e-7. Three actual native/imported view pairs were inspected: all alpha channels and threshold silhouettes match, whole-image mean channel differences stay below 0.031/255, and framing margins are at least 59 pixels.

The GLB retains the reference-guided broad silhouette and open structure. Fine cast wear is subtler than the concept. Hidden connections, post/rib interpretation and exact manufacturing details remain inferred. Final user artistic acceptance, game scale/mount/state integration and performance require separate evidence. No simulation or renderer code changes here.

## Reproduction and disk

Run `remaster_rigellian_static.py` and then `verify_remastered_rigellian_static.py` in Blender background mode with Python exit code 1 and `-- --recipe sources/objects/rigellian/construction-unit/recipe.json`. Inspect actual renders and record feedback before registering with `tools/register_rigellian_building_remaster.py --model sources/objects/rigellian/construction-unit`; rebuild galleries and run local project/evidence/quality checks. Reports bind exact binaries, recipe, helpers, concept/prompt and render bytes. Reuse the existing checkout without a game build, archive or extra worktree. Remove only verified empty task-owned exporter directories after processes finish.
