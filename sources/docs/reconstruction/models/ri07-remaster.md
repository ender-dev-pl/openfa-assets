# RI07 Science Labs: canonical source remaster

Tracking: openfa-assets #253 and per-building #38. Preserve `openfa:building/legacy/046`, definition class 255, footprint 3x3 and construction updates 58. Original functional record 907 establishes mainly civilian fundamental research. Culture record 18 describes elegant, ergonomic architecture and widespread research. Neither establishes a crown mechanism or emission effect.

## Reference and concept feedback

Correctly paletted surface and catalogue phases 0/10/20/30/40 show a flared jade pedestal, one broad saucer, small circular features, a dark left roof detail, gold rim fittings, exposed brass/pale neck, segmented green mast and a thin silver fork. The silver fork and single saucer distinguish RI07 from RI06. Catalogue phases reveal/highlight one view; they are not camera angles or an operating cycle. Current game sprite-selector rules and directional IDs were inspected; this ID is not directional. Construction uses the separate shared construction presentation.

One actual built-in ImageGen request used the real surface and colour phase20. Its exact prompt is `ri07-concept-prompt-1.txt`; the public concept is `gallery/media/concepts/rigellian/ri07-review-1.png`. It retains the main anatomy and silver fork, but broadens the foot, thickens retainers and adds an unsupported rectangular roof cover and more prominent gold fittings. Those differences do not replace the legacy-guided geometry. Small fitting counts, circular-cover engineering, roof-well interiors and hidden surfaces remain authored interpretation. Original pixels stay private.

## One current source and runtime pair

Use `sources/objects/rigellian/science-labs/model.blend` and `model.glb` for gameplay, construction/build menu and SciTek. Former studies remain historical, outside the single current inventory selection. The completed revision-three study is the starting source, including its corrected roof shading and material field; it is not rebuilt from the older bootstrap silhouette.

The three mapped solids and all twelve silver crown components retain exact evaluated geometry, with protected-surface error 0.0. The thin silver prongs are deliberately preserved rather than replaced by broad gold arms from another building. Existing independently authored wear, three physical dents, roof cut and seated covers/supports remain intact. Reduction affects only six rim, collar and joint seams. Evaluated triangles fall from 72,072 to 65,184, with maximum accepted bidirectional vertex-to-surface deviation below 0.000604 source units. This sampled measure is not an exhaustive Hausdorff bound.

There are 38 editable physical components, eight used materials and four embedded maps. These explicit costs do not certify batching or Android frame rate. Root is identity `PlacementRoot`, local -Y forward, +Z dorsal, ground Z0. Bounds are [-1.104000, -1.113000, 0] to [1.103595, 1.104378, 5.850000]. Nominal footprint is not a calibrated scene-to-game scale. The source is static, with no clips; construction/damage variants and client state/mount calibration remain separate.

## Actual saved-native and GLB verification

Blender 4.5.15 reopens the saved native model and independently imports GLB. All 38 components have positive closed welded surfaces. The original source-specific anatomy assertions remain intact: actual roof cut, sleeve/bore/floor contacts, two supported fins, three measured dents, pedestal/saucer overlap, neck/mast overlap, four retainers, seated circular covers and rim fittings, crown supports and three silver terminals. The connected sampled contact graph is supplemental diagnostic evidence, not exhaustive solid-intersection proof.

Complete mapped colour/roughness pixels, cylindrical side UVs and six planar cap surfaces pass in both formats. Component names, triangle counts and used materials match; maximum bidirectional native/import surface error is below 6.06e-7. Three actual view pairs were inspected: all alpha channels and threshold silhouettes are identical, whole-image mean channel differences remain below 0.020/255, and framing margins are at least 56 pixels.

The GLB keeps the source-guided silhouette and slim silver fork. Its surface wear/contrast are subtler than the concept. Exact small fitting counts, roof-feature engineering and hidden surfaces remain interpreted, rather than proven by technical validity. Final user artistic acceptance, client scale/mount/state integration and performance require separate evidence. No simulation or renderer code changes here.

## Reproduction and disk

Run `remaster_rigellian_static.py` and then `verify_remastered_rigellian_static.py` in Blender background mode with Python exit code 1 and `-- --recipe sources/objects/rigellian/science-labs/recipe.json`. Inspect actual renders and record feedback before registering with `tools/register_rigellian_building_remaster.py --model sources/objects/rigellian/science-labs`; rebuild galleries and run local project/evidence/quality checks. Reports bind exact binaries, recipe, helpers, concept/prompt and render bytes. Reuse the existing checkout; no game build, archive or extra worktree is needed. Remove only verified empty task-owned exporter directories after processes finish.
