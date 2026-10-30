# Mauna Surveillance Craft Type 5 — first authored iteration (#1023)

`openfa:ship/mauna/surveillance-craft-type-5`, global type 31 / Mauna local type 0, role class 2. Catalogue data establishes a scout with armour 5 and AI construction cost 15. No registered source study existed. This adds a missing first source while preserving all previous reconstructions/refinements. Artistic refining remains deferred.

## Source evidence

MN0A.256 supplies 32 populated, correctly paletted headings, approximately 11–22×18–25 pixels. All were inspected, including enlarged 0/4/12/28; eight appear in ignored comparison evidence. They support a grey angular slab-like body, an interrupted upper edge, blue-grey surface areas and warm lower tabs/marks. No catalogue video or mapped functional narrative is located. Exact thickness, proportions, corner sections, crown/tab count, surface treatment and front/rear calibration remain unresolved.

The first source interprets the form as a chamfered metal slab with four separated crown tabs, two warm lower blocks, seam strips and paired service-panel assemblies on each broad face. This is independent construction below source resolution, not proof of original part counts or hidden geometry. Surface fields are not labelled windows; lower blocks are non-emissive and are not claimed as engines/weapons. Two equipment slots lack recovered coordinates/default equipment; no visible panel is assigned to them. AlignmentForward is an authored local -Y helper, not a source-calibrated heading or mount.

ENGLISH.CDB Mauna Architecture record 137 at 0x7bea describes utilitarian angular buildings without decoration or comfort-driven features. It guides plain construction contextually, not concrete spacecraft material or exact ship geometry. The grey opaque metal interpretation follows the specific visual evidence without architectural ornament. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only, absent from mesh/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/mauna/surveillance-craft-type-5/` contains editable Blend/GLB, four independent colour/roughness maps, metadata, nine native/imported rendered views, gallery and technical reports. The 47 closed meshes/five materials comprise the slab body, four crown tabs, two warm lower blocks, four seam strips, four service frames/four blue-grey insets/twelve dark strips and sixteen fasteners.

The slab uses a dense chamfered rectangular loft with explicit triangle-fan caps. Edge insets scale the cross-section without reversing vertex order at its axes. Two broad-face Gaussian dents deform real geometry. The body is triangulated before corner-normal capture. Twenty nested overlays follow the actual analytic dented face profiles; fasteners align to normals sampled from the actual mesh. Crown gaps remain physically open, while tabs, lower blocks and seam strips overlap the supporting body. All parts remain separately editable beneath PlacementRoot.

Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Two packed image materials cover fifteen meshes; blue-grey insets, oxidized alloy and carbon-dark strips use rough authored solids. Modifiers precede local box UVs and explicit corner normals. Previous model sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens native Blend and independently imports GLB. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, materials and dents. Measured dents are approximately 0.00500/0.00600 model units. Maximum actual corner-normal error is approximately 0.000326.

Odd/even actual mesh containment verifies twelve crown roots, six lower-block contacts, four seam-strip contacts, 180 fitted-panel/inset/strip contacts and sixteen fasteners. Three ray columns through the whole assembly check clear crown gaps above the main body. These scoped samples do not prove exhaustive structural/mechanical correctness. AlignmentForward is tested under four rigid root rotations without source heading, equipment-mount or animation calibration claims.

The actual gallery and eight-heading comparison were inspected. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Warm lower blocks are visible in the lower-angle/underside views and can be occluded by the slab in upper quarter views; their source-relative projection/placement needs later calibration. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1023-surveillance-craft-type-5/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `8511d4c7`.

## Deferred

Final slab proportions/thickness, crown form/count, surface-panel arrangement, lower-tab projection/meaning, hidden construction, two calibrated mounts, runtime orientation/scale and required operational/damage variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
