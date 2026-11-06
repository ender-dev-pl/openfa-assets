# Terran Explosive and Area Explosive missile studies

Tracking: #959, relates to #951 and #946. Reference preparation: #958.

## Evidence and observed structure

`missile-reference-index.json` binds each definition to source archive hashes, exact decoded frames and proven palettes. PM00 and PM01 management previews resolve a gray cylindrical segmented pressure body, red jacket, long rounded red tail members and a recessed nose instrument. Explosive has a rounded shoulder nose and long silver instrument insert; Area Explosive has a stepped nose and a shorter circular instrument. Runtime frames 0, 3, 6 and 9 confirm the long narrow red/gray/red arrangement at game scale. They do not establish a complete 3D rotation or hidden mechanisms.

The original images remain in ignored reference artifacts. No pixel, texture or mesh from them is incorporated into either model. Reference sheets: `artifacts/missile-reference-study/explosive-comparison.png` and `area-explosive-comparison.png`; regenerate using `review_terran_missiles.py` after reference preparation.

## Modelling and actual render refinement

Revision 1 established distinct lofted noses, instrument channels cut into actual jacket geometry, segmented pressure casing and a hollow bell. Comparison with the management preview and four runtime frames found tail members too narrow, an instrument disk too small, and a front-facing center tail member inconsistent with the two main visible lobes.

Revision 2 widens and rounds the tail members, rotates the fourfold arrangement by 45 degrees, widens the actual instrument channel and disk, and replaces the solid aft casing cap with a thick hollow skirt. The stricter whole-model axial test also exposed a solid retaining collar obstructing the nozzle; it was replaced with a true thick annular shell and checked again. It retains a broad uninterrupted gray middle section and restrained surface joints instead of masking the shape with invented greebles. Actual front and oblique renders were reviewed again; the paired front lobes, nose distinctions and red/gray proportions are clearer. Six transparent views per model include direct front, oblique front/rear, side, nose and nozzle views. Authored-only galleries are alongside each model.

## Authored interpretation and unresolved fidelity

The fourfold hidden tail arrangement is an interpretation; the single management perspective does not prove the rear member count. Exact dimensions, nozzle throat, shell thickness, material response, fasteners and small service labels are independently authored. The more rounded original Area nose steps remain a possible refinement; the study currently emphasizes machined retaining rims. The enlarged instrument disk and channels preserve the visible feature but are not pixel-calibrated reconstructions.

Native nose axis is +Z, front is -Y and units are uncalibrated. No socket transform, deployment mechanism, animation or gameplay heading calibration is asserted. The 14 runtime frames are presentation states, not evidence of an independently animated nozzle or rotating nose. Integration and final artistic acceptance remain open; neither study is accepted as a completed catalogue asset.

## Reproduction and verification

Run Blender with `build_terran_missiles.py`, then `verify_terran_missiles.py`; run `review_terran_missiles.py` with Pillow. Reopen native sources and import standalone GLB to verify actual topology, materials, bounds, distinct nose structures, four declared tail members, the cut instrument recess, the open nozzle axis, wall thickness and the first axial occlusion at the recessed throat. Both models have 57 mesh objects and five materials; the checks use actual intersections rather than object names alone for nozzle depth and rim seating. Sources contain editable named meshes, intentional materials and asset collections. No invented animation or external file image dependency is present.

Regenerate and verify the reconstruction inventory after changing registered sources. Per-model JSON records source/build hashes and technical/render checks; these checks do not imply artistic acceptance. This milestone changes model sources and documentation only, so Blender is the exercised target runtime; the game renderer and catalogue bindings are unchanged.
