# Achaean Dedicated Ore Transporter — first authored iteration (#1031)

`openfa:ship/achaean/dedicated-ore-transporter`, global 39/local 2: role class 5, armour 40, AI cost 45. Catalogue transporter tags include ore/missiles and outer-orbit behaviour. Four equipment slots lack calibrated coordinates/default equipment. No mapped narrative or catalogue video is located. This adds a missing first source; previous models/refinements remain unchanged.

## Evidence and interpretation

AC2C.256 supplies sixteen populated even headings and empty odd frames, consistent with runtime heading selection. All populated headings and enlarged 0/4/12/28 were inspected. They support widely spaced thin upright grey/red crescents, a fuller warm/red axial body, red transverse structures, pale terminal and yellow rear marks. In this source the crescent openings face opposite the long central projection, unlike Dedicated Fighter. The end-on source is much wider relative to its height.

The first source defines its own fuller body profile, wider transverse links, reversed crescent direction, lower crescent height, red body fields, yellow bands, pale fore terminal and grey link sleeves. Exact profiles, proportions, details, hidden surfaces and heading calibration remain interpretations. The grey sleeves and fitted fields are not recovered machinery. Coloured fields are non-emissive; no decorative component is assigned proven cargo, weapon, engine or sensor function. Four gameplay slots are not mapped to visible parts. AlignmentForward is an uncalibrated local -Y helper.

ENGLISH.CDB Achaean Architecture record 166 at 0x9d65 supplies curved-form context, not proof of vehicle domes, towers, ornament or mechanisms. Actual paletted sprites guide geometry and colours. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only and absent from mesh/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine rendered views, gallery and technical reports. There are 37 closed meshes/six materials; three image materials cover fifteen meshes. The assembly comprises body, two crescent shells/two links, axial stem/terminal, two red crescent fields/two fitted plate covers/four strips/eight fasteners, body cover/two strips/four fasteners, two red body fields/two yellow bands, pale fore terminal and two grey sleeves.

The established loft/closed-grid authoring methods are reused with new dimensions, section profiles and crescent orientation; the completed fighter source is not regenerated or altered. Dense body and crescent shells retain three physical dents. Fitted overlays follow owner profiles; fasteners use actual ray-sampled normals. Modifiers and primary triangulation precede local box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and issue-seeded scratches provide new-object wear. Earlier assets and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded texture pixels, box UVs/materials and three dents. Actual odd/even containment checks body/link/crescent/axial/terminal/sleeve joins, 135 fitted-surface samples and twelve fasteners. Four empty-mouth and six occupied-rim witnesses preserve actual open crescents. AlignmentForward is tested under four rigid root rotations, without source-heading/equipment/timing calibration claims. Samples do not establish exhaustive mechanical correctness.

The actual gallery and eight-heading source comparison were inspected. Nine views passed framing. Both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.006/255. Maximum corner-normal error is 0.000711. Three dents measure approximately 0.005/0.005/0.006. Twenty-three assembly contacts, 135 fitted-surface samples, twelve fasteners, four mouth gaps and six occupied-rim samples passed. Body fullness and layered detail remain provisional for the deferred refining pass. Original comparison pixels remain ignored in `artifacts/issue-1031-dedicated-ore-transporter/`; tracked views contain authored models only. Required changed-code quality base: `56473ce1`. Game-client integration is unchanged.

## Deferred

Final body fullness/section and crescent outlines, detail layout/functions, hidden construction, terminal interpretation, four equipment mounts, runtime scale/orientation and operational/damage variants remain unresolved. Technical validity does not accept final art. Refining and construction scaffolding remain deferred.
