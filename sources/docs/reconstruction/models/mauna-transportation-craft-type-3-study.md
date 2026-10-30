# Mauna Transportation Craft Type 3 — first authored iteration (#1027)

`openfa:ship/mauna/transportation-craft-type-3`, global 35/local 4: role class 5, armour 35, AI cost 45, four equipment slots without calibrated coordinates/default equipment. Catalogue tags establish ore/missile transporter roles and outer-orbit behaviour. No mapped ship functional narrative or catalogue video is located. This is a missing first source; prior reconstructions/refinements remain unchanged.

## Reference and interpretation

MN4C.256 has sixteen populated even headings and empty odd frames, matching the runtime even-heading restriction. All populated headings were inspected, including enlarged 0/4/12/20. They support three tall notched sections over a broad lower housing, pale blue bands, grey lower blocks and warm metallic lower/end details. Apparent height differences in oblique views do not establish unequal physical tower heights.

The first source interprets the sections as three equal-height extrusions with three deep open side recesses each. Exact notch depth/width, hidden surfaces, proportions and heading calibration remain uncertain. In particular, full-width cutouts are an interpretation of the small side silhouettes, not recovered mechanical geometry. Service panels, strips and fasteners are independent subpixel detail. The visible parts are not assigned cargo, engine, shield or weapon functions. Four gameplay slots are not mapped to decorative components; AlignmentForward is an authored local -Y helper.

Mauna Architecture ENGLISH.CDB record 137 at 0x7bea supplies utilitarian angular context. It does not prove concrete spacecraft material or specific vehicle geometry. Reference, functional, cultural and gameplay indexes are hash-bound. Original images are reference-only and do not enter geometry or texture inputs.

## Assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine actual rendered views, gallery and technical reports. There are 83 closed meshes and five materials; three image materials cover 33 meshes. Separate components include the lower housing, three notched towers, six fitted frames/six insets/twelve strips/twenty-four fasteners, twelve blue tower bands/three rear plates, lower trim/seams/service blocks, warm feet/end details and two grey lower blocks.

Concave YZ profiles are tessellated and subdivided into dense cap triangles, joined by actual side walls. Each tower has a physical side dent; fitted panels follow the analytic dent profile. Actual ray-sampled tower normals place fasteners. Face normals are recalculated before those placement samples, avoiding reversed roots; modifiers and primary triangulation precede UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and seeded scratches supply new-object wear. Existing sources and shared helpers are preserved.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render verify the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded pixels, box UVs/material values and three dents. Actual odd/even containment checks tower roots, attached details, 216 fitted-surface samples and twenty-four fasteners. Twenty-seven empty-notch witnesses and occupied adjacent-tooth samples distinguish real recesses from flat dark rectangles; six additional witnesses preserve tower separation. The alignment helper is tested under four root rotations, without source-heading or equipment calibration claims.

The actual gallery and eight-heading reference comparison were inspected. Nine views passed framing checks. Both matched native/imported alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.003/255. Maximum corner-normal error is 0.000671. Measured dents are approximately 0.00555/0.00647/0.00740. Sixty-six assembly contacts, 216 fitted-surface samples, twenty-four fasteners, twenty-seven notch voids and six tower-separation witnesses passed. Exact notch shape and band layout remain for later artistic review. Original comparison images remain ignored in `artifacts/issue-1027-transportation-craft-type-3/`; tracked views contain authored models only. Required changed-code quality base: `ffc69ae6`. Game-client integration is unchanged.

## Deferred

Final proportions, notch sections, band layout, hidden construction, runtime scale/orientation, four mount coordinates and required operational/damage variants remain unresolved. Final artistic acceptance/refining and construction scaffolding remain deferred.
