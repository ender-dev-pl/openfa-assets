# Achaean Dedicated Fighter — first authored iteration (#1030)

`openfa:ship/achaean/dedicated-fighter`, global 38/local 1: role class 4, direct-approach combat, armour 50, AI cost 35. Four equipment slots lack calibrated coordinates/default equipment. No mapped functional narrative or catalogue video is located. This adds a missing first source; previous reconstructions/refinements are preserved.

## Source and interpretation

AC1C.256 supplies 32 populated correctly paletted headings, approximately 29–59 pixels wide. All headings and enlarged 0/4/12/28 were inspected. End-on frames support two thin upright side elements; side frames show open swept grey crescents with red areas around a warm axial body, transverse links and yellow axial detail. These are distinct from Hunter/Prospector's red horizontal lobes.

The first source interprets these as separate vertical C-shaped plates, red outer-face fields, warm tapered central body, two transverse links and axial stem/terminal. Precise crescent sections, terminal shape, proportions, hidden surfaces and source heading remain uncertain. Coloured marks are non-emissive; no decorative part is assigned proven weapon, engine, shield or sensor function. Four gameplay slots are not mapped to visible details. AlignmentForward is an uncalibrated local -Y helper.

ENGLISH.CDB Achaean Architecture record 166 at 0x9d65 supplies curved-form context. It does not establish spacecraft domes, ornament or mechanisms. Specific paletted sprites direct geometry and colour. Cultural, functional, reference and gameplay indexes and authoring helpers are hash-bound. Original pixels remain reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine rendered views, gallery and technical reports. The 30 meshes/six materials comprise axial body, two crescent shells/two links, axial stem/terminal, two red fields/two fitted plate covers/four strips/eight fasteners, and one fitted body cover/two strips/four fasteners. Three image materials cover eleven meshes.

The central body uses a dense swept elliptical loft. Crescent plates use two closed grid faces and actual curved perimeter walls, with open mouths and finite thickness. Each shell has a physical dent. Red fields, service covers and strips follow the respective dented surfaces; fasteners align to normals sampled from actual geometry. Modifiers and primary triangulation precede authored box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and seeded scratches supply new-object wear. Existing assets and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render verify the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, provenance/binary hashes, packed bytes/decoded pixels, UVs/materials and three dents. Odd/even containment checks axial/transverse joins, 99 fitted-surface contacts and twelve fasteners. Four crescent-mouth void witnesses and six occupied-rim samples distinguish real open crescents from solid plates. AlignmentForward is tested under four rigid root rotations, without source heading/equipment/timing calibration claims. Samples do not prove exhaustive mechanical correctness.

The actual gallery and eight-heading source comparison were inspected. Nine views passed framing checks. Both matched native/imported alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.005/255. Maximum corner-normal error is 0.000672. Measured dents are approximately 0.005/0.005/0.006. Eighteen assembly contacts, 99 fitted-surface samples, twelve fasteners, four empty mouths and six occupied-rim witnesses passed. Body length/section and crescent outline remain provisional for the deferred refining pass. Original comparison pixels remain ignored in `artifacts/issue-1030-dedicated-fighter/`; tracked galleries contain authored models only. Required changed-code quality base: `6a397eec`. Game-client integration is unchanged.

## Deferred

Final proportions, crescent/body sections, detail layout, hidden construction, axial-terminal interpretation, four equipment mounts, runtime scale/orientation and operational/damage variants remain unresolved. Technical validity does not establish final artistic acceptance. Refining and construction scaffolding remain deferred.
