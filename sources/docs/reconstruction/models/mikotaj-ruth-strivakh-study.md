# Mikotaj Ruth-Strivakh — first authored iteration (#1015)

`openfa:ship/mikotaj/ruth-strivakh`, global type 23 / Mikotaj local type 3, role class 5. Catalogue tags establish an ore/missile transporter; armour is 40 and AI construction cost is 45. No registered study existed. This adds a missing first source without modifying previous models/refinements. Artistic refining remains deferred.

## Source evidence

MK3C.256 contains 16 populated even headings and 16 empty odd headings, consistent with its even-heading runtime selection. All populated frames were inspected with the embedded original palette. Canonical headings are 89–90×24–25 pixels; heading 4 reaches 124×19, while headings 12/28 are 46–47×29. No catalogue video is located. The sprites support a blue-grey central body with lower projecting grey surfaces, a long copper-coloured lateral assembly, oval terminal bodies and green raised details. Exact sections, openings, proportions, material divisions and depth remain interpretation.

The first source interprets the copper assembly as paired open beams with crossmembers, eight green fixtures and two terminal pods. The source's projected green highlights do not prove eight physical fixtures or their function. Likewise, the rectangular beam sections/openings, lower keel and central shell profile are independently authored construction, not recovered geometry. The central body's height/volume and lower projections need a later proportion review; technical export checks do not establish fidelity.

The functional text index maps the name but no narrative. Two equipment slots lack recovered coordinates and default equipment. No visible fixture is assigned to a slot or claimed as a weapon, engine or cargo interface. AlignmentForward is an authored local -Y helper, not a calibrated source heading or mount.

Mikotaj Architecture in ENGLISH.CDB, record 76 at 0x39fa, distinguishes heavy metallic mining-colony construction from light resonant crystal architecture on home worlds. It provides contextual guidance for robust interfaces, not proof that this spacecraft uses either construction system. The green fixtures remain opaque and non-emissive. Cultural, functional, visual-reference and gameplay indexes plus authoring helpers are hash-bound. Legacy pixels are reference-only and are not geometry/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/mikotaj/ruth-strivakh/` contains editable Blend/GLB, six independently authored colour/roughness maps, metadata, native/imported renders, gallery and technical reports. The 68 closed meshes/six materials comprise a central pressure shell, lower keel, two terminal pods, four copper rails/eight crossmembers, eight fixture bases/eight green fixtures, four rail insets, two fitted body bezels/faces, and four service covers/eight slots/sixteen fasteners.

Dense elliptical longitudinal shells have explicit triangle-fan caps and three shallow physical dents. Twelve overlays fit their owner shell; body bezels use ray-sampled embedded roots, with targeted submicron cleanup after bevel application. Rail, pod, base and crossmember volumes overlap at authored joints while six sampled frame openings remain clear. These construction choices are independently editable beneath PlacementRoot.

Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Three packed image materials cover 36 meshes. Gold interfaces, oxidized service alloy and carbon-dark seams use authored rough solid materials. Modifiers precede local box UVs and explicit corner-normal capture. Existing models and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens the native asset and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, material parity and actual corner normals within 0.001. Three measured dents are approximately 0.00593, 0.00396 and 0.00396 model units. Maximum corner-normal vector error is approximately 0.000701.

Odd/even mesh containment verifies nine keel/body contacts, eight rail/body/pod attachment samples, sixteen rail/crossmember joints, eight fixture roots with supporting base contacts, four rail insets, 64 body-bezel roots, two bezel/face joins, 108 fitted-overlay contacts and sixteen fasteners. Six vertical rays through the full assembly verify clear frame openings. These scoped samples do not prove exhaustive structural or mechanical correctness. The alignment helper is verified under four rigid root rotations without mount or animation calibration claims.

The actual gallery and eight-heading source comparison were inspected. Nine rendered views passed framing and matched-camera export checks. Both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean colour difference is below 0.009/255. Native and imported rendering exercise the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored evidence in `artifacts/issue-1015-ruth-strivakh/`; tracked gallery images contain only authored models.

Inventory and source checks cover 303 definitions / 1444 visual reference occurrences and six cultural architecture articles. Required changed-code quality verification uses milestone base `a7e6a865`.

## Deferred

Central body/lower projection proportions, beam sections/openings, fixture layout/function, hidden construction, two calibrated mounts, runtime orientation/scale and required operational/damage variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
