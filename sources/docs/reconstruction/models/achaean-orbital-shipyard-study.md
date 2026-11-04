# Achaean Orbital Shipyard — first authored iteration (#1032)

`openfa:ship/achaean/orbital-shipyard`, global 40/local 3: role class 7, zero-speed orbital shipyard, armour 100, AI cost 80. Three equipment slots lack calibrated coordinates/default equipment. No mapped functional narrative or catalogue video is located. This adds a missing first source; previous reconstructions/refinements remain unchanged.

## Source and interpretation

AC3C.256 supplies two correctly paletted fixed-state sprites, 202×50 and 219×62 pixels, not independent cameras. Both were inspected. State 0 supports a long warm/rose axial structure, six repeated tall segments, small blue fields and orange central detail. State 1 is a larger open-frame presentation whose meaning/timing remain unresolved. This first source interprets state 0 only, without state-completeness, deployment, damage or construction-scaffolding claims.

The model interprets the spine as a tapered radial body aligned to local X, with six separate vertical profiled segments, collars, blue-field mounts, fitted orange centre, service covers and axial terminals. Exact profiles, dimensions, collar/field counts, hidden surfaces and source orientation remain authored interpretations. Colours are rough non-emissive surfaces; parts are not assigned proven engine, weapon or sensor functions. Three gameplay slots are not mapped to decorative components. AlignmentAxis is an uncalibrated local +X helper.

ENGLISH.CDB Achaean Architecture record 166 at 0x9d65 supplies curved architectural context; it does not establish station domes, furnishings or mechanisms. Specific paletted sprites guide broad form and colour. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, four independent 1024-square colour/roughness maps, metadata, nine rendered views, gallery and technical reports. There are 94 closed meshes/six materials; two image materials cover 37 meshes. Components comprise spine, six profiled segments/twenty-four collars, seven field mounts/seven blue fields, orange central field/two dividers, two axial stems/two terminals and six fitted service covers/twelve slots/twenty-four fasteners.

Dense independent profiles retain seven physical dents. Twenty-one fitted overlays follow their owner profiles; fasteners align to actual ray-sampled normals. An explicit proper rotation maps the spine's local Z to world X while preserving its local Y, keeping the dent/orange field on the intended front face. Segment profiles retain their vertical axes. Applied modifiers and primary triangulation precede box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Existing assets and shared helpers are preserved.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded pixels, UVs/materials and seven dents. Actual odd/even containment checks spine/segment/collar/field/axial joins, 189 fitted-surface samples and twenty-four fasteners. Five void witnesses preserve upper segment separation. AlignmentAxis is checked under yaw, pitch and roll, without source heading/equipment/timing calibration claims. Scoped samples do not establish exhaustive mechanical correctness.

The actual gallery and comparison with both source states were inspected. Nine views passed framing checks. Both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Maximum corner-normal error is 0.000643. Core dent measures approximately 0.006; six segment dents measure 0.00285�0.00380. Ninety-six assembly contacts, 189 fitted-surface samples, twenty-four fasteners and five separation witnesses passed. This source remains visibly simplified: richer axial segmentation, asymmetry, central structures and side detail await the explicitly deferred refining pass. Original comparison pixels remain ignored in `artifacts/issue-1032-orbital-shipyard/`; tracked views contain authored models only. Required changed-code quality base: `a6840e57`. Game-client integration is unchanged.

## Deferred

Final profiles/proportions, richer layered side structures, field/collar layout/functions, hidden construction, second fixed-state presentation, three equipment mounts, runtime scale/orientation and operational/damage variants remain unresolved. Technical validity does not accept final art or state completeness. Refining and construction scaffolding remain deferred.
