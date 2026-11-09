# RI08 Databanks: canonical source remaster

Tracking: openfa-assets #253 and per-building #39. Preserve `openfa:building/legacy/047`, definition class 255, footprint 2x2 and construction updates 44. Original functional record 908 establishes research-knowledge storage and remote communication; additional social functions are left unclear. Culture record 18 describes elegant ergonomic architecture and widespread research. Neither establishes machinery or emission for the upper equipment.

## Reference and concept feedback

Correctly paletted surface and catalogue phases 0/10/20/30/40 show the lower drum/channels, two-upper/one-lower arrangement of small gold fields, narrow neck, flared middle housing/large gold circular fitting, upper collar fields, pale patterned head, twin supports, side module and silver fork. Phases reveal/highlight a fixed view rather than showing an operating cycle. Current game directional-ID rules exclude this ID; construction is a separate shared presentation.

One actual built-in ImageGen request used the real surface and catalogue colour phase20. The exact prompt is `ri08-concept-prompt-1.txt`; the public concept is `gallery/media/concepts/rigellian/ri08-review-1.png`. It retains the major anatomy and colour layout, but thickens the fork arms, enlarges fittings and invents struts in the lower neck. Those changes are not adopted. Port count/depth, hidden equipment purpose and exact casting engineering remain authored interpretation. Original pixels stay private.

## One current source and runtime pair

Select `sources/objects/rigellian/databanks/model.blend` and `model.glb` across gameplay, build menu and SciTek. Previous studies remain historical, outside the single current inventory selection. The latest visible-equipment refinement is the source: retain its actual pale perforated head, rather than reverting to the older small dark fasteners.

Twenty-six protected components retain exact evaluated geometry, with measured protected-surface error 0.0. This includes four main solids, the perforated casing, eight inset backings, twin supports and complete silver crown. Existing body-fitted cast bezel, correct lower field arrangement, three physical dents and independently authored wear remain intact. Four rim/joint/gasket seams receive measured tessellation reduction: evaluated triangles fall from 82,360 to 77,840, with maximum accepted bidirectional vertex-to-surface deviation below 0.000666 source units. This sampled measure is not an exhaustive Hausdorff bound.

There are 50 editable physical components, nine used materials and five embedded maps. These costs do not certify draw-call batching or Android frame rate. Root is identity `PlacementRoot`, local -Y forward, +Z dorsal, ground Z0. Bounds are [-0.903623, -0.903595, 0] to [0.903623, 0.903595, 5.155000]. Footprint is not a calibrated scene-to-game scale. Static source, no clips; construction/damage variants and client state/mount calibration remain separate.

## Actual native and independent GLB validation

Blender 4.5.15 reopens the saved native model and independently imports GLB. All 50 components have positive closed, consistently oriented welded physical surfaces. Both source-specific contracts run: the original body assertions retain three slot/backing contacts, three dents, neck/housing overlaps, eight radial collar-crossing checks, six seated small fittings, five large-face contact samples, 32 cast-root samples, support/head/crown overlaps, module inset and silver terminal positions. The refined contract checks eight physical equipment recesses, open casing apertures, embedded backings and casing-root contacts. A connected sampled contact graph supplements these checks without claiming exhaustive solid-intersection proof.

Full colour/roughness pixels pass for the body/cap maps and pale upper coating. The three unchanged mapped body solids retain cylindrical sides and six planar end surfaces. The refined head, perforated casing and eight backings intentionally use local box-projected UVs from the later refinement, replacing the obsolete cylindrical-head contract. Every projected face is checked against one consistent original projection plane, including after triangulation and independent GLB import; the updated chart is not silently omitted from validation.

Component names, triangle counts and used materials agree. Maximum bidirectional native/import surface error is below 3.68e-7. Three actual view pairs were inspected: all alpha channels and threshold silhouettes match, whole-image mean channel differences stay below 0.0066/255, and margins are at least 57 pixels. The GLB retains the source-guided silhouette and readable perforations; material wear/contrast are subtler than the concept. Final user artistic acceptance, runtime scale/mount/state integration and game performance require separate evidence. No simulation or renderer code changes here.

## Reproduction and disk

Run `remaster_rigellian_static.py` followed by `verify_remastered_rigellian_static.py` in Blender background mode with Python exit code 1 and `-- --recipe sources/objects/rigellian/databanks/recipe.json`. Inspect actual renders and record feedback before registering with `tools/register_rigellian_building_remaster.py --model sources/objects/rigellian/databanks`; rebuild galleries and run local project/evidence/quality checks. Reports bind exact binaries, recipe, helpers, concept/prompt and render bytes. Reuse the existing checkout without a game build, archive or extra worktree. Remove only verified empty task-owned exporter directories after processes finish.
