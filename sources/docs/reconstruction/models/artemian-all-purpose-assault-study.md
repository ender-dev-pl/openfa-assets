# Artemian All-Purpose Assault — first authored iteration (#1018)

`openfa:ship/artemian/all-purpose-assault`, global type 26 / Artemian local type 1, role class 1. The catalogue supplies the generic ship tag, armour 36 and AI construction cost 20. No registered study existed. This adds a missing first source while preserving previous reconstructions/refinements. Artistic refining remains deferred.

## Source evidence

AR1A.256 supplies 32 populated, correctly paletted headings. All were inspected, including enlarged 0/4/12/28 crops; eight headings appear in ignored comparison evidence. The approximately 15–18 by 8–11 pixel sprites support a broad pointed green silhouette with small grey central and lateral accents. AR1C is absent; no catalogue video is located. The broader green presentation and separated grey accents differ from Gerla-Kans' elongated grey roof. Precise volume, thickness, taper, accent sections, projection and front/rear calibration remain unresolved.

The first source interprets the grey accents as a low central cowl and two separate lateral cowls on a broad green delta hull. This does not prove their function or establish that the original used enclosed pods. The inferred central cowl also projects slightly through the underside; that hidden shape is not established by source pixels. The functional text index maps the name but no narrative. Three equipment slots lack recovered coordinates and default equipment. Neither cowls nor rear interfaces are labelled engines/weapons or assigned to those slots. AlignmentForward is an authored local -Y helper, not a recovered heading or equipment mount.

ENGLISH.CDB Artemian Architecture record 105 at 0x5734 supports contextual metal/alloy, shell and edge treatment. Its architectural statements do not prove spacecraft geometry or require every vehicle surface to be angular. The low rounded cowls and broad green hull are informed primarily by the specific sprite evidence. No decorative insignia or architectural interior features are invented. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Legacy pixels are reference-only and never enter geometry or texture generation.

## Independent assembly

`docs/assets/reconstruction/ships/artemian/all-purpose-assault/` contains editable Blend/GLB, four independent colour/roughness maps, metadata, native/imported renders, gallery and technical reports. The 54 closed meshes/four materials comprise the green hull, three grey cowls, six fitted service covers/twelve slots/twenty-four fasteners, a forward inset/three slats and two fitted rear bezels/interfaces.

The green delta uses a closed planform/profile grid; separate grey cowls use dense elliptical longitudinal sections with triangle-fan caps. The new recipe defines its own dimensions, sections, offsets and contacts; it does not regenerate Gerla-Kans. Primary grid/cowl triangulation precedes explicit corner-normal capture where required by the builder. Twenty-two overlays follow owner-shell widths/heights, including nested slots/slats. Fasteners align with normals sampled from actual supporting meshes. Rear bezels have ray-fitted embedded roots and targeted submicron bevel cleanup. All parts remain separately editable beneath PlacementRoot.

Four physical dents, independent analytic stains/grime, grain and issue-seeded scratches supply new-object wear. Two packed image materials cover ten meshes; oxidized service alloy and carbon-dark seams use rough authored solids. Applied modifiers precede local box UV assignment. Previous model sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens the native asset and independently imports GLB. Checks cover closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, materials and physical dents. Measured dents are approximately 0.00318 green, 0.00494 central cowl and 0.00397 for each lateral cowl. Maximum corner-normal error is approximately 0.000654.

Odd/even actual mesh containment verifies nine central cowl/hull contacts, six lateral cowl/hull samples, 64 rear-bezel roots, two rear interface joins, 198 fitted-overlay contacts and twenty-four fasteners. These scoped samples do not prove exhaustive structural or mechanical correctness. AlignmentForward is checked under four rigid root rotations without source heading, mount or animation calibration claims.

The actual gallery and eight-heading comparison were inspected. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1018-all-purpose-assault/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `4e7df3c7`.

## Deferred

Final body/cowl proportions, exact grey accent geometry/function, taper/thickness, underside and hidden construction, three calibrated mounts, runtime orientation/scale and required damage/operational variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
