# Mauna Elite Command Craft — first authored iteration (#1026)

`openfa:ship/mauna/elite-command-craft`, global 34 / local 3: role class 6, armour 80, AI construction cost 50. Six equipment slots have no calibrated coordinates or default equipment. This adds a missing first source; completed models and refinements are preserved.

## Evidence and interpretation

MN3C.256 supplies 32 populated correctly paletted headings. All were inspected, with enlarged 0/4/12/28 and an eight-heading comparison. They support two thick angular grey sections, a narrower connection, pale blue band-like details and long axial projections with red tips. The narrow end-on views distinguish this tall paired body from the low Type 6 hull. No catalogue video or mapped functional narrative is located.

Exact dimensions, sections, hidden surfaces, placement of the blue bands and source heading remain unresolved. The first source interprets the sections as chamfered block pods, joined by a narrow solid connector; separate axial roots, beams and tips are editable. Service frames, strips, fasteners and small markers are authored detail below source resolution. They are not identified as weapons, engines, glazing or emitters. The six gameplay slots are not mapped to decorative parts. AlignmentForward is an uncalibrated local -Y helper.

ENGLISH.CDB Mauna Architecture record 137 at 0x7bea supports contextual utilitarian, angular construction without aesthetic/comfort priorities. It does not establish concrete spacecraft material or precise vehicle form. The specific sprite evidence directs the ship geometry. Cultural, functional, reference and gameplay sources are hash-bound. Original pixels remain reference-only, absent from geometry and texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, nine rendered views, gallery, metadata and technical reports. The 59 meshes/five materials comprise two dense chamfered pods, central connector, two axial roots/two projections/two red tips, four blue side bands/four service frames/four insets/twelve strips/sixteen fasteners, four small red markers, two upper blue bands and four upper rails. Three image materials cover twenty meshes.

New-object wear combines independent analytic grime/stains, grain and seeded scratches with two physical side dents. Twenty-four fitted side surfaces follow the dented profiles, including nested panels and strips; fastener placement uses normals sampled from actual pod geometry. Applied modifiers and triangulated primary pods precede box UVs and explicit corner-normal capture. Shared helpers and earlier model assets remain unchanged.

## Verification scope

Native reopen and independent GLB import/render exercise Blender 4.5.15. Scoped checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed image bytes and decoded pixels, UVs/materials and both physical dents. Odd/even mesh containment checks assembly roots, fitted surfaces and fasteners; six void witnesses preserve the narrow connection's open side areas. Alignment helper positions/axes are checked under four root rotations. These samples do not prove exhaustive mechanical correctness or source-calibrated mounts.

The actual gallery and eight-heading source comparison were inspected. Nine views passed framing checks. Both matched native/imported views have identical alpha channels and threshold-128 silhouettes, with maximum foreground mean RGB difference below 0.002/255. Measured dents are approximately 0.006/0.007; maximum corner-normal error is 0.000685. Seventy assembly samples, 216 fitted-panel samples and sixteen fasteners passed actual containment checks. The standalone modelling runtime is the verification target; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1026-elite-command-craft/`; tracked gallery images contain authored models only. Required changed-code quality base: `45917c30`.

## Deferred

Final proportions, band layout, axial-part interpretation, hidden construction, runtime orientation/scale, six equipment mounts and operational/damage variants remain unresolved. Technical validity does not accept final art. Refining and construction scaffolding remain deferred.
