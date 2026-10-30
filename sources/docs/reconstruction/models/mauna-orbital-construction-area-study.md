# Mauna Orbital Construction Area — first authored iteration (#1028)

`openfa:ship/mauna/orbital-construction-area`, global 36/local 5: role class 7, zero-speed orbital shipyard, armour 130, AI cost 80 and five equipment slots without calibrated coordinates/default equipment. No mapped functional narrative or catalogue video is located. This adds a missing first source; previous models/refinements remain unchanged.

## Source and interpretation

MN5C.256 supplies two correctly paletted fixed-state sprites, 153×104 and 179×109, not separate cameras. Both were inspected. State 0 supports a broad grey/copper station, raised spires, a tapered lower assembly and a lateral bank of green rectangular details. State 1 is a larger open-frame presentation with unresolved meaning/timing. This first source interprets state 0 only and does not claim state completeness, deployment, damage timing or scaffolding. Construction scaffolding remains explicitly deferred.

The model interprets the broad casing and upper shell as stretched radial sections, with a separate tapered lower shell, central and secondary towers/spires, orange collars, axial stems and lateral panel bank. Exact sections, dimensions, counts, hidden surfaces and alignment remain authored interpretations. Coloured fields use rough non-emissive materials; no source-backed engine, weapon or shield function is assigned. Five gameplay slots are not mapped to decorative components. AlignmentAxis is an uncalibrated local +Z helper.

ENGLISH.CDB Mauna Architecture record 137 at 0x7bea supplies contextual utility/no-decoration guidance. It does not establish concrete spacecraft material or require angular substitution for the specific curved sprite form. Cultural, functional, reference and gameplay indexes and authoring helpers are hash-bound. Original pixels are reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, four independent 1024-square colour/roughness maps, metadata, nine actual rendered views, gallery and technical reports. The 89 meshes/six materials include three main shells, central/secondary towers and stems/collars, lower stem/vents, lateral spine, four panel frames/four green inserts/twelve bars, terminal/link/bands, opposite root/tip, three fitted central green plates/six dividers and four service covers/eight slots/sixteen fasteners. Two image materials cover sixteen meshes.

Dense radial profiles retain three physical dents after elliptical stretching. Twenty-four fitted overlays follow actual owner profiles, including lower vents and nested service/green-plate dividers. Fasteners align to ray-sampled shell normals. Applied modifiers and triangulated primary shells precede box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and seeded scratches supply new-object wear. Shared helpers and all prior assets are preserved.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Scoped checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, provenance/binary hashes, packed bytes/decoded pixels, UVs/material values and three dents. Odd/even actual containment checks shell/tower/axial/panel-bank joins, 216 fitted-surface samples and sixteen fasteners. Four gap witnesses preserve bank-panel separation. AlignmentAxis is checked under yaw, pitch and roll, without runtime calibration or mechanism/timing claims. Samples do not establish exhaustive mechanical correctness.

The actual gallery and comparison with both original states were inspected. Nine views passed framing checks. Both matched native/imported views have identical alpha channels and threshold-128 silhouettes; maximum foreground mean RGB difference is below 0.003/255. Maximum corner-normal error is 0.000587. Measured dents are approximately 0.00553/0.00489/0.00400 after stretching. Fifty-four assembly contacts, 216 fitted-surface samples, sixteen fasteners and four bank-gap witnesses passed. The current source is visibly simplified relative to the source station; secondary shell segmentation, small side structures and richer layered details remain for the explicitly deferred refining pass. Original pixels remain ignored in `artifacts/issue-1028-orbital-construction-area/`; tracked galleries contain only authored models. Required changed-code quality base: `c4f66f02`. Game-client integration is unchanged.

## Deferred

Final proportions, section/detail layout, hidden construction, second fixed-state presentation, five mounts, runtime scale/orientation and operational/damage variants remain unresolved. Technical validity does not establish final artistic acceptance. Refining and construction scaffolding remain deferred.
