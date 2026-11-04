# Mauna Combat Craft Type 1.5 — first authored iteration (#1024)

`openfa:ship/mauna/combat-craft-type-1-5`, global type 32 / Mauna local type 1, role class 1. The catalogue supplies the generic ship tag, armour 50 and AI construction cost 20. No registered source study existed. This adds a missing first source while preserving prior models/refinements. Artistic refining remains deferred.

## Source evidence

MN1A.256 supplies 32 populated, correctly paletted headings, approximately 6–18×7–13 pixels. All were inspected, including enlarged 0/4/12/28; eight appear in ignored comparison evidence. They support a low elongated grey rectangular body, a stepped upper contour and a pale blue-grey end area. This differs from Surveillance Craft Type 5's upright slab and warm lower details. No catalogue video or mapped functional narrative is located.

The first source interprets the shape as a chamfered low beam with two separated raised deck sections, end interfaces, seam strips and fitted side/deck service panels. Precise proportions, thickness, deck division, gap, surface details and bow/rear calibration remain unresolved. Pale end areas are non-emissive and not identified as windows, engines or weapons. Four equipment slots lack recovered mount coordinates/default equipment; no visible panel is assigned to them. AlignmentForward is an authored local -Y helper, not a source-calibrated heading or mount.

ENGLISH.CDB Mauna Architecture record 137 at 0x7bea supplies contextual utilitarian/no-decoration guidance. It does not establish concrete spacecraft material or exact vehicle geometry. The first source uses plain grey metal informed by the specific sprite evidence, without architectural ornament. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only and are absent from mesh/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/mauna/combat-craft-type-1-5/` contains editable Blend/GLB, two independent colour/roughness maps, metadata, nine native/imported rendered views, gallery and technical reports. The 49 closed meshes/four materials comprise the low body/two raised decks, two end interfaces, four seam strips, four side frames/four insets/eight dark strips/sixteen fasteners and a deck hatch/three strips/four fasteners.

The new recipe defines independent dimensions/sections, rather than regenerating the completed Type 5 asset. The body uses a dense chamfered rectangular loft with triangle-fan caps and two physical side dents. Separate deck grids include a third shallow dent and a real open gap between raised sections. Body/decks are triangulated before corner-normal capture. Twenty fitted overlays follow dented side/deck profiles, including nested inserts/strips. Side fasteners use normals sampled from actual body geometry; deck fasteners attach to the nearly planar hatch. All parts remain separately editable beneath PlacementRoot.

Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. One packed image material covers nine meshes; pale blue-grey end detail, oxidized alloy and carbon-dark surfaces use rough authored solids. Applied modifiers precede local box UVs and explicit corner normals. Previous model sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens native Blend and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, materials and dents. Measured dents are approximately 0.00400/0.00500 on the sides and 0.00400 on the raised deck. Maximum corner-normal error is approximately 0.000596.

Odd/even actual mesh containment verifies eighteen raised-deck/body contacts, six end-interface roots, four seam-strip roots, 180 fitted-overlay contacts and twenty side/deck fasteners. Three whole-assembly ray columns verify clearance above the main body between deck sections. These scoped samples do not establish exhaustive structural or mechanical correctness. AlignmentForward is checked under four rigid root rotations without source-heading, equipment-mount or animation timing claims.

The actual gallery and eight-heading comparison were inspected. Nine views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1024-combat-craft-type-1-5/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `9fcbd31e`.

## Deferred

Final body/deck proportions, stepped contour and gap, end interpretation, surface layout, hidden construction, four calibrated mounts, runtime scale/orientation and required damage/operational variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
