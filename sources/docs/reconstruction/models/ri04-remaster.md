# RI04 Community: canonical source remaster

Tracking: openfa-assets #253 and per-building #34. Identity `openfa:building/legacy/043`, definition class 0, footprint 2x2 and construction updates 48 remain unchanged. Original functional record 904 describes living quarters. Culture record 18 describes ergonomic, elegant Rigellian architecture. Neither establishes an operational role or animation for the gold crown.

## Reference and concept decision

Correctly paletted body and catalogue phases 0/10/20/30/40 were inspected. They show two rounded jade sections, a narrow waist, six staggered upper gold fittings, two lower fittings, pale lower equipment with a red core, a stepped gold base and three open prongs. Reveal/highlight phases remain presentation, not a turntable or working mechanism. One actual built-in ImageGen request used the body and catalogue colour phase 20; its exact prompt is `ri04-concept-prompt-1.txt`. The concept keeps the major anatomy, but its heavier crown shoulders, broad stepped foot and wider pale equipment are interpreted proportions. The established refined geometry is retained instead of copying those differences blindly. Original pixels stay private.

## Current model and preservation

Current consumers must select only `sources/objects/rigellian/community/model.blend` and `model.glb`. All former studies remain historical, outside the single current inventory selection. Reuse the same object for gameplay, build menu and SciTek; there is no separate prettier menu model.

The latest tapered-crown refinement is the starting source. Its two pods, structural waist and both broad tapered crown cheeks retain exact evaluated geometry (measured protected-surface error 0.0). Complete body colour/roughness pixel preservation and six planar end-cap/cylindrical side UV contracts are checked in both formats. Red equipment, real recess, ribs, eight gold fittings, fasteners and existing wear are retained. Reduction affects only the ground rim, waist seam, crown foundation and rubbed mounting lip. The evaluated total falls from 47,324 to 42,536 triangles; maximum accepted bidirectional vertex-to-surface deviation is below 0.000682 source units. This is sampled surface evidence, not exhaustive Hausdorff proof.

There are 56 editable physical mesh components, nine used materials and six embedded images. These counts are explicit costs, not a batching or Android FPS certification. Root is identity `PlacementRoot`, Blender local -Y forward and +Z dorsal, ground Z0. Measured bounds are [-0.620000, -0.644000, 0] to [0.620000, 0.620000, 3.607500]. Footprint is not a calibrated conversion from scene units to game units. The source is static with no clips or inferred moving assemblies.

## Actual saved-native and GLB feedback

Blender 4.5.15 reopens the saved native source and independently imports GLB. All 56 components have positive closed welded physical surfaces. Source-specific checks retain the actual service cut, two geometric dents, seated waist/crown support, eight bezel/gold-face contacts and red-core/backing overlap. Current broad tapered crown checks replace the obsolete thin-conductor terminal checks, rather than silently skipping crown validation. A sampled contact graph has one component; it is not exhaustive structural intersection proof.

Native/import component names, used materials and triangle counts match, with bidirectional surface error below 3.38e-7. Original protected body/crown surfaces and native/import texture pixels/UVs pass. Three actual native/imported camera pairs were inspected; all threshold silhouettes are identical. Front and rear alpha are exact; front-quarter has a small antialiased edge difference recorded in visual-review.json. Whole-image mean channel differences stay below 0.022/255 and framing margins are at least 54 pixels. Current GLB keeps the source's anatomy, colour placement and open crown; fine material contrast is simpler than the artistic concept.

Source-bound reports bind current tools, recipe, exact model bytes, concept/prompt and render pixels. Prior RI03 evidence remains valid and unchanged. Final user artistic acceptance, client scale/state/mount integration, construction/damage variants and performance are separate. No gameplay or renderer code is changed here.

## Reproduction and disk

Run `remaster_rigellian_static.py -- --recipe sources/objects/rigellian/community/recipe.json`, then `verify_remastered_rigellian_static.py` with the same recipe in Blender background mode and Python exit code 1. The case recipe protects completed surfaces and selects its explicit anatomy checks; additional recipes do not require rewriting RI03 authoring history. Register only after real reports exist with `tools/register_rigellian_building_remaster.py --model sources/objects/rigellian/community`, then rebuild the gallery and run project/evidence/quality checks. The registrar binds evidence; it never fabricates a Blender run. Temporary exporter directories are task-owned and cleaned after use. No new checkout, build, archive or original-pixel publication is needed.
