# Achaean Hunter/Prospector — first authored iteration (#1029)

`openfa:ship/achaean/hunter-prospector`, global 37/local 0: role class 2, scout, armour 25, AI cost 15. Two equipment slots lack calibrated coordinates/default equipment. No mapped functional narrative or catalogue video is located. This adds a missing first source while preserving completed reconstructions/refinements.

## Evidence and interpretation

AC0A.256 supplies 32 populated correctly paletted headings, approximately 9–21 pixels wide. All were inspected, including enlarged 0/4/12/28. They support a green central shape and elongated projection, swept red lateral shapes and a narrower warm central element. Resolution makes exact sections, thickness, part division and heading calibration highly uncertain.

The first source interprets this as a curved green body/nose, two separate swept red lobes and a warm central spar with red tip, preserving open gaps between the three trailing parts. The central spar's rectangular section, lobe profiles, proportions, hidden underside and service layout are authored interpretations. No part is assigned proven engine, weapon, sensor or mining-equipment function. Coloured surfaces are non-emissive. The two gameplay slots are not mapped to decorative components; AlignmentForward is an authored local -Y helper.

ENGLISH.CDB Achaean Architecture record 166 at 0x9d65 describes curved architectural forms, domes and decorated inhabited spaces. This supplies curved-form context only; it does not establish domes, towers, furnishings or ornament on this small scout. Specific paletted sprites guide silhouette and colour. Cultural, functional, reference and gameplay indexes and authoring helpers are hash-bound. Original pixels remain reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine rendered views, gallery and technical reports. There are 26 closed meshes/five materials; three image materials cover eight meshes. Components comprise three dense swept lofts, central spar/red tip, three fitted service covers/six strips and twelve fasteners.

Loft sections supply independent positions, widths and heights; each curved shell has a physical upper-surface dent. Fitted patches follow the analytic crown and fasteners align to actual ray-sampled shell normals. Face normals are established before placement; applied modifiers and primary triangulation precede box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and seeded scratches supply new-object wear. Shared helpers and all earlier models remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed geometry, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded pixels, UVs/materials and three dents. Odd/even containment samples verify body/lobe and spar/tip joins, 81 fitted-surface contacts and twelve fasteners. Four void witnesses preserve fork gaps. AlignmentForward is checked under four rigid root rotations, without source-heading, equipment or timing calibration claims. These scoped checks do not prove exhaustive mechanical correctness.

The actual gallery and eight-heading source comparison were inspected. Nine views passed framing checks. Both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.008/255. Maximum corner-normal error is 0.000704. Three dents measure approximately 0.005/0.004/0.005. Twelve assembly contacts, 81 fitted-surface samples, twelve fasteners and four gap witnesses passed. Coarse shell section changes and detail layout remain for the deferred refining pass. Original comparison images remain ignored in `artifacts/issue-1029-hunter-prospector/`; tracked views contain authored models only. Required changed-code quality base: `2f917ccd`. Game-client integration is unchanged.

## Deferred

Final fork/body proportions, section smoothness and detail layout, central-spar interpretation, hidden surfaces, two equipment mounts, runtime scale/orientation and operational/damage variants remain unresolved. Technical validity does not accept final art. Refining and construction scaffolding remain deferred.
