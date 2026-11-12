# Artemian Ultimate Mk II — first authored iteration (#1020)

`openfa:ship/artemian/ultimate-mk-ii`, global type 28 / Artemian local type 3, role class 6. Catalogue data establishes combat-direct-approach, armour 80 and AI construction cost 50. No registered source study existed. This adds a missing first source while preserving all previous models/refinements. Artistic refining remains deferred.

## Source evidence

AR3C.256 supplies 32 populated, correctly paletted headings, approximately 38–80×21–23 pixels. All were inspected, including enlarged 0/4/12/28 crops; eight appear in ignored comparison evidence. They support an elongated rounded grey upper cover above a green lower body and small grey perimeter protrusions. Pale source areas are visible highlights/marks, not established lamps, windows or emission. No catalogue video or mapped functional narrative is located.

The first source interprets the form as an elliptical pressure assembly with a broad upper cover, smaller green lower body, an annular seam rim and twelve separate perimeter fittings. Exact proportions, sections, fitting count/spacing, hidden backs and front/rear calibration remain unresolved. Twelve fittings are an inferred physical layout, not recovered equipment mounts. Six catalogue slots have no mount coordinates or default equipment, and visible protrusions are not assigned to them or labelled engines/weapons. AlignmentForward is an authored local -Y helper, not a source-calibrated heading or mount.

ENGLISH.CDB Artemian Architecture record 105 at 0x5734 supplies contextual metal/alloy and shell guidance. It does not override this object's rounded sprite evidence or prove vehicle mechanisms/interior features. No insignia or architectural furnishings are invented. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only and are not geometry/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/artemian/ultimate-mk-ii/` contains editable Blend/GLB, four independently authored colour/roughness maps, metadata, nine native/imported views, gallery and technical reports. The 55 closed meshes/four materials comprise the upper/lower bodies, closed annular lid rim, twelve ray-fitted bezels/twelve separate perimeter fittings, four service covers/eight slots and sixteen fasteners.

The independently authored radial profiles are stretched along Y by 2.05. Separate upper/lower volumes overlap at the seam; the rim is an annular mesh with an explicit central void. Perimeter origins/normals are sampled from the actual lower body and retained as authored fitting frames, not hardpoint transforms. Bezels have embedded roots sampled from the real support mesh, with targeted submicron cleanup after bevel application. Fittings retain independently editable pressure profiles. Twelve overlays follow their curved owner profile, including nested slots. Fasteners follow normals sampled from actual hull geometry. All parts remain editable beneath PlacementRoot.

Two physical radial dents, independent analytic stains/grime, grain and issue-seeded scratches supply new-object wear. Authored local radial depths are 0.006/0.005; world-space radial samples after the Y stretch measure approximately 0.01214/0.01000 model units. Two packed image materials cover thirty meshes; oxidized service alloy and carbon-dark seams use rough authored solids. Applied modifiers precede local box UVs and explicit corner normals. Existing model sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens native Blend and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, material parity and radial dents. Maximum actual corner-normal error is approximately 0.000687. Expected XY bounds include the lid rim's 0.012-unit extension, rather than incorrectly using only the main cover profile.

Odd/even actual mesh containment verifies five upper/lower body overlaps, sixteen rim roots with a clear annular-axis witness, 384 bezel-root contacts, twelve fitting/bezel joins, 108 fitted-overlay contacts and sixteen fasteners. Fitting support distances are checked against the authored frame records. These scoped contact samples do not prove exhaustive structural or mechanical correctness. AlignmentForward is tested under four rigid root rotations without equipment-mount or source-heading calibration claims. No animation timing is inferred.

The actual gallery and eight-heading comparison were inspected. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1020-ultimate-mk-ii/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `3f028a58`.

## Deferred

Final upper/lower proportions, exact cover sections, material/highlight interpretation, perimeter fitting count/layout/function, hidden construction, six calibrated mounts, runtime orientation/scale and required damage/operational variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
