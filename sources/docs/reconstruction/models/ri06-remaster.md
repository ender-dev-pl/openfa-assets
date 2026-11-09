# RI06 Strategic Bunker: canonical source remaster

Tracking: openfa-assets #253 and per-building #36. Preserve `openfa:building/legacy/045`, definition class 24, footprint 3x3 and construction updates 34. Original functional record 906 establishes a command centre with research/information coordination. Culture record 18 describes ergonomic, elegant buildings and widespread research. Neither establishes an operational role for the crown.

## Evidence and concept feedback

Correctly paletted surface and catalogue phases 0/10/20/30/40 show three broad rounded levels, small rim fittings, dark roof features, a brass/pale exposed upper neck, tapered jade mast and compact gold fork. These phases reveal/highlight a fixed view, not a turntable or operating cycle. The current game sprite selector and its directional-ID list were inspected: this ID is not directional. Construction uses the separate shared construction presentation; no technical animation is inferred from the catalogue.

One actual built-in ImageGen request used the real surface and catalogue colour phase20. Its exact prompt is `ri06-concept-prompt-1.txt`; the public concept is `gallery/media/concepts/rigellian/ri06-review-1.png`. It preserves the broad anatomy and restrained jade/brass palette, but thickens the disc rims, enlarges the crown and gives the dark roof features unsupported crescent geometry. Those differences are rejected. The established thinner levels and compact crown remain; round roof wells, sleeves, floors and fins are explicitly an authored interpretation of ambiguous source details. Exact hidden engineering is not recovered. Original pixels remain private.

## One current model and budget

Select `sources/objects/rigellian/strategic-bunker/model.blend` and `model.glb` for gameplay, build menu and SciTek. Former studies remain historical, outside the single current inventory selection. The latest tapered-crown refinement is the starting source. All three saucers, central structural column, upper mast and both crown arms retain exact evaluated geometry, with protected-surface error 0.0. Existing physical dents, independently authored wear and texture maps are retained.

Reduction is limited to seven rim, collar and groove seams. Evaluated triangles fall from 87,200 to 79,236, with maximum accepted bidirectional vertex-to-surface deviation below 0.000647 source units. This sampled measure is not an exhaustive Hausdorff bound. There are 47 editable physical components, eight used materials and six embedded images. This relatively substantial geometry budget preserves mapped surfaces and actual cuts; it does not certify batching or Android frame rate. Client profiling may justify a separately verified LOD without changing the canonical anatomy.

Root is identity `PlacementRoot`, local -Y forward, +Z dorsal and ground Z0. Bounds are [-1.104000, -1.106750, 0] to [1.104000, 1.104000, 4.965000]. Footprint is not a calibrated conversion to game units. The source is static, with no clips or invented crown mechanisms. Construction/damage variants and client state/mount calibration remain separate.

## Actual native and independent GLB feedback

Blender 4.5.15 reopens the saved native model and independently imports GLB. All 47 components have closed positive welded physical surfaces. Case-specific checks retain three actual roof cuts, sleeve/bore contacts, embedded floors, six supported fins, three measured dents, six seated rim fittings, column/level overlaps, exposed neck/roof/mast contacts, four mast retainers and crown supports/central terminal. Current tapered-arm checks replace only obsolete thin-side-terminal assertions. The sampled contact graph is connected; this is supplemental evidence, not exhaustive solid-intersection proof.

Complete mapped colour/roughness pixels, cylindrical side UVs and ten planar cap surfaces pass in both formats. Names, triangle counts and used materials agree; maximum bidirectional native/import surface error is below 5.71e-7. Three actual native/imported view pairs were inspected: all alpha channels and threshold silhouettes are identical, whole-image mean channel differences stay below 0.052/255 and framing margins are at least 58 pixels.

The GLB retains the legacy-guided three-level silhouette and slim mast/crown. Its material contrast and wear are subtler than the concept. Precise dark roof-feature interpretation and hidden underside structure remain authored inference. Final user artistic acceptance, runtime scale/mount/state integration and game performance require separate evidence. No game renderer or simulation code changes here.

## Reproduction and disk

Run `remaster_rigellian_static.py` and then `verify_remastered_rigellian_static.py` in Blender background mode with Python exit code 1 and `-- --recipe sources/objects/rigellian/strategic-bunker/recipe.json`. Inspect the actual output and write visual feedback before registering with `tools/register_rigellian_building_remaster.py --model sources/objects/rigellian/strategic-bunker`; rebuild the galleries and run project/evidence/quality checks. Reports bind exact binaries, recipe, helpers, concept/prompt and renders. Reuse the existing checkout, avoid game builds/archives and remove only verified empty task-owned exporter directories after processes finish.
