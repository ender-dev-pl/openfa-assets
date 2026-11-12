# Mauna Max Combat Craft Type 6 — first authored iteration (#1025)

`openfa:ship/mauna/max-combat-craft-type-6`, global 33 / local 2: role class 4, armour 70, AI cost 35, six equipment slots without calibrated coordinates or default equipment. This adds a missing first source; previous sources and refinements remain unchanged.

## Evidence and interpretation

MN2C.256 supplies 32 populated headings with embedded palette. All headings and enlarged selected frames were inspected; eight headings appear in the ignored comparison. They support a layered elongated grey rectangular hull, sloped raised upper structure, two red protrusions, long warm brown side areas, pale blue end detail and warm lower details. No catalogue video or mapped functional narrative was located.

Exact proportions, sections, underside construction, detail counts and heading calibration remain interpretations. Red parts are not assigned weapon or engine functions; pale blue areas are non-emissive. Six gameplay equipment slots are not mapped onto decorative parts. AlignmentForward is an authored local -Y helper only.

ENGLISH.CDB Mauna Architecture record 137 at 0x7bea describes utilitarian angular construction without aesthetic/comfort priorities. This is contextual guidance, not evidence for concrete spacecraft or exact ship geometry. Source and cultural indexes are hash-bound. Original pixels are reference-only; all geometry and textures are independently authored.

## Assembly and verification

The asset directory contains editable Blend and GLB, six independent colour/roughness maps, metadata, nine rendered views, gallery and technical reports. There are 58 closed meshes and six materials; three image materials cover sixteen meshes. Layered hull, sloped roof, red stacks, brown bands, end panels, lower blocks and fitted service details remain independently editable. New-object wear includes procedural grime, stains, scratches and three physical dents, approximately 0.005/0.006 on the hull sides and 0.005 on the roof.

Blender 4.5.15 reopened the native file and independently imported GLB. Checks passed for positive closed geometry, exact geometric vertex counts after diagnostic-only seam welding, source hashes, hierarchy/transforms/bounds, UVs, material values, packed bytes and decoded texture pixels. Maximum corner-normal error is approximately 0.000575, below 0.001. Odd/even containment samples verify the layered assembly, red mounts, side/end details, lower blocks, 180 fitted-overlay contacts and twenty fasteners. Three ray columns verify clearance between the red parts. These samples do not establish exhaustive mechanical correctness.

The actual gallery and original-heading comparison were inspected. Nine views passed framing checks; matched native/imported views have identical alpha and threshold-128 silhouettes, with foreground mean RGB differences below 1.5/255. Actual rendering verifies the standalone modelling runtime; game-client integration is unchanged. Original comparison pixels remain ignored in `artifacts/issue-1025-max-combat-craft-type-6/`. Required changed-code quality base: `471eaddb`.

## Deferred

Final proportions, colour interpretation, hidden construction, six calibrated mounts, runtime orientation/scale and operational/damage variants remain unresolved. Technical export validity does not constitute final artistic acceptance. Refining and construction scaffolding remain deferred.
