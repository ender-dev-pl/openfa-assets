# RI05 Health Unit: canonical source remaster

Tracking: openfa-assets #253 and per-building #35. Preserve `openfa:building/legacy/044`, definition class 34, footprint 2x2 and construction updates 36. Original functional record 905 establishes advanced medical support. Rigellian culture record 18 describes ergonomic, elegant architecture and widespread research. Neither establishes a moving crown or the engineering of the low circular fitting.

## Evidence and concept feedback

The correctly paletted surface and catalogue phases 0/10/20/30/40 show a flared jade pedestal, narrow neck, rounded three-grille head, paired pale central grid, low circular detail and a gold fork on a narrow root. These phases reveal/highlight one view; they are not a recovered turntable or operating cycle. Original pixels remain private.

One built-in ImageGen request used the real surface and catalogue phase20. Its exact prompt is `ri05-concept-prompt-1.txt`; the published concept is in `gallery/media/concepts/rigellian/ri05-review-1.png`. The concept keeps the principal silhouette and palette, but simplifies the central grid to one column and turns the circular feature into a raised insert. Those differences are rejected: retain the existing paired grid and actual recessed well. Concept material wear/contrast is stronger than the established maps; its shading is guidance rather than proof of geometry.

## Single current model

Consumers select `sources/objects/rigellian/health-unit/model.blend` and `model.glb` for gameplay, build menu and SciTek. Prior studies remain historical, outside the single current inventory selection. The latest tapered-crown source is retained. Pedestal, neck, vented head and both broad crown arms retain exact evaluated geometry, with measured protected-surface error 0.0. Existing independently authored wear, two geometric dents and packed maps are preserved.

Only the ground rim and two neck collars receive measured tessellation reduction. Total evaluated triangles fall from 50,996 to 47,336; accepted bidirectional vertex-to-surface error stays below 0.000644 source units. This sampled measure is not an exhaustive Hausdorff bound. There are 41 editable physical mesh components, nine used materials and six embedded images; these costs do not certify draw-call batching or Android performance.

Root is identity `PlacementRoot`, local -Y forward, +Z dorsal and ground Z0. Bounds are [-0.85, -0.85, 0] to [0.85, 0.85, 3.6400001]. Footprint does not establish the conversion to game units. The model is static with no clips; construction/damage variants and client state behavior remain separate.

## Actual native and independent GLB verification

Blender 4.5.15 reopens the saved native model and independently imports GLB. All 41 components have closed positive welded surfaces. Source-specific checks retain the three real grille cuts, twenty seated louvre solids, two physical dents, overlapping neck/support, annular face penetration, open inspection centre and an embedded recessed floor. Current broad tapered-arm checks replace only obsolete thin-side-terminal assertions. The sampled contact graph has one component; this does not claim exhaustive structural intersections.

Complete body colour/roughness pixels, cylindrical side UVs and six planar cap mappings pass in both formats. Component names, triangle counts and used materials agree. Maximum bidirectional native/imported surface error is below 1.92e-7. Three actual view pairs were inspected: all threshold silhouettes match; front/rear alpha are exact and front-quarter has a small antialiased-edge difference recorded in visual-review.json. Whole-image mean channel differences stay below 0.030/255, with margins of at least 46 pixels.

The actual GLB retains the legacy-guided silhouette and specific grid/well details that the concept simplified. Exact grille engineering, hidden rear surfaces and crown function remain authored interpretation. Final user artistic acceptance, runtime scale/mount/state integration and performance require separate evidence; no client or renderer code changes here.

## Reproduction and disk

Run `remaster_rigellian_static.py` and then `verify_remastered_rigellian_static.py` in Blender background mode with Python exit code 1 and `-- --recipe sources/objects/rigellian/health-unit/recipe.json`. Register only after inspecting real renders and writing feedback using `tools/register_rigellian_building_remaster.py --model sources/objects/rigellian/health-unit`; rebuild galleries and run project/evidence/quality checks. Reports bind exact model, recipe, helpers, concept, prompt and render bytes. Reuse the existing checkout; no game build, archive or original-pixel publication is required. Remove only verified empty task-owned exporter temporary directories after processes finish.
