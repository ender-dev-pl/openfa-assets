# RI19 canonical Thermal Lance review and delivery

Tracking: openfa-assets #253/#52 and PR #254. Semantic ID `openfa:building/legacy/058`, class 17, footprint 3x3, constructionUpdates 28. One current editable Blend/GLB is selected in `sources/objects/rigellian/thermal-lance/`; previous studies remain history. This pass preserves the good existing independently authored geometry rather than replacing it with an enlarged ImageGen interpretation. No polygon reduction or invented new operating mechanism is claimed.

## Legacy and concept feedback

Original ENGLISH.TXT record 919 identifies this as the least effective anti-ship weapon. Original CDB architecture record 18 describes ergonomic/elegant Rigellian architecture and widespread research; it does not establish the mechanism, alloy identity or firing effects. Correctly paletted base and all sixteen base-plus-head compositions 2..17 were viewed. Catalogue phases 0/10/20/30/40 and the coloured/outlined close-up show reveal/highlighting rather than timed operation. They support the same bell-shaped pedestal, dark lower slots, bronze front strip/base fitting and short rounded head with a single tapered lance.

Current game `LegacyBuildingSpriteFrameSelector.SelectBodyFrame` and current gameplay rules retain static descriptor 1 and use `2+(((heading+8)>>4)&15)` for the upper bank. This proves the directional bank/selection formula, not the model's sign or phase relative to a world heading. The model rig and exact elevation/pivot sections are authored; client yaw calibration remains open. Shared RIS3 construction is separate.

One actual built-in ImageGen concept was generated using four actual paletted assembled headings. The exact prompt is `ri19-concept-prompt-1.txt`; public concept is `gallery/media/concepts/rigellian/ri19-review-1.png`. The concept follows the bell pedestal, lower slots, bronze details and single tapered upper projection. It enlarges/fuses the rounded head/lance root, strengthens the foot lip and strip, and exaggerates wear. These are not recovered details, so source-derived proportions, seated fittings, three existing geometric dents and authored wear maps are retained. No second concept request was necessary.

## Actual native and independent GLB runtime

The author opens the hash-bound existing source, applies its evaluated modifiers without changing its surface, preserves all twelve named mesh components and the PlacementRoot/YawPivot/LanceTipSocket hierarchy, then exports extras. Four upper meshes and the tip socket inherit YawPivot; pedestal, bearing and lower fittings remain under PlacementRoot. No separate whole-heading models or timed/firing/pitch clips are created.

The source-specific anatomy checks retain three dents, bearing/head/lance seating, fitted lower strips, 64 fitting-flange samples and packed decoded green colour/roughness pixels with local cylindrical UVs and six planar caps. Native/imported topology is closed and positive-volume after welding coincident UV seam vertices at tolerance 0.000001. Requiring raw index-connected glTF vertices would incorrectly reject exported UV seams; this adjustment does not fill geometric holes.

All sixteen authored yaw samples at 22.5-degree intervals verify that the fixed base remains stationary and that the actual lance end, socket position and socket forward axis follow the expected rigid rotation. Corresponding native/imported moving matrices differ by less than 0.000000239. Protected source geometry is unchanged within 0.000001, and bidirectional export surface error is below 0.000000133. This is 30,200 triangles, twelve mesh nodes, five materials and four embedded images; no Android frame-rate or batch-consolidation result is inferred.

Nineteen paired actual renders cover three whole-object angles and all sixteen authored yaw poses. One pose initially had only 3 pixels of framing margin; the case-specific verifier expands whole-object camera scale by 8 percent and rerenders both formats. All delivered comparisons preserve margins and nearly identical appearance; render equivalence is separate from legacy likeness. Same canonical geometry supplies technical views and information displays, rather than independent diagram geometry. Interactive and Markdown galleries include the concept, actual GLB and 90/180/270-degree sample links explicitly marked authored head yaw with a fixed base.

## Integration limits and reproduction

Use `model.json`, `runtime-review.json`, `visual-review.json` and the delivery manifest for exact binary/helper/image hashes, bind bounds and articulation contract. PlacementRoot is identity; Blender -Y forward/+Z dorsal, YawPivot local +Z and tip-socket local +Z forward. No model yaw sign/phase, game scale, continuous collision sweep, firing/pitch effects, construction/damage integration, Android cost or final user artistic acceptance is claimed. These limits must remain explicit in integration.

Reproduce with `remaster_rigellian_thermal_lance.py`, `verify_remastered_rigellian_thermal_lance.py -- --recipe sources/objects/rigellian/thermal-lance/recipe.json`, and `tools/review_rigellian_thermal_lance_pixels.py` with private legacy/contact-sheet paths. Original pixels remain private. Existing checkout reused, no extra game build/worktree/archive. Former mobile-ship programme #248 remains unfinished.
