# Mikotaj Ylikt-shan — first authored iteration (#1013)

`openfa:ship/mikotaj/ylikt-shan`, global type 21, Mikotaj local type 1, role class 1. The gameplay catalogue supplies only the generic ship tag. The authoritative inventory had no registered source study. This creates a missing first source and preserves previous reconstructions/refinements; artistic refining remains deferred.

## Source evidence

MK1C.256 is absent; the runtime fallback selects MK1A.256. All 32 populated, correctly paletted headings were inspected. Sprites are approximately 8–21 pixels wide and 8–13 pixels high. They support two parallel elongated blue/grey members, a transverse connecting body, open end gaps and small gold accents. Exact sections, proportions, gold placement and front/rear calibration remain interpretation. No catalogue video is located.

The functional text index maps the name but no narrative. Two equipment slots have no recovered mount coordinates; metadata binds the gameplay catalogue hash and records two declared slots / zero calibrated 3D mounts. Neither rail nor fitting is assigned to a slot or given a proven weapon/engine function. AlignmentForward is an authored uncalibrated local -Y helper.

ENGLISH.CDB Mikotaj Architecture record 76 at 0x39fa distinguishes heavy metallic mining-colony construction from light crystal architecture on home worlds. Its contextual use for robust metal interfaces does not establish this ship's material or geometry. Visible blue/grey/gold colours guide the opaque first source; no transparent homeworld-crystal specification is inferred. Cultural/reference indexes and authoring helpers are hash-bound. Original pixels remain reference-only and are absent from mesh/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/mikotaj/ylikt-shan/` contains editable Blend/GLB, four independent blue/gold colour and roughness maps, provenance, actual render gallery and technical reports. The 28 closed meshes/four materials comprise two faceted longitudinal rails, a transverse hull, four small end fittings, two fitted octagonal gold bands, a gold bridge plate, two rail service covers/six slots/eight fasteners and two fore-rail insets.

The new geometry preserves the open fore/aft gaps rather than reusing Hiero's radial body. Primary sections retain planar octagonal faces with dense subdivisions for physical wear and explicit triangle-fan caps. Gold bands are open annular meshes following rail width/height/centre profiles. Eleven fitted overlays include exact longitudinal profile and octagonal roof breaks without duplicate rows/columns. Fasteners align to normals sampled from the actual rail mesh. Exact end-fitting and service construction remain independently authored detail below source resolution.

Three physical dents on the rails/bridge, analytic stains, grain and seeded scratches supply new-object wear. Two packed image materials cover eight meshes; oxidized alloy and carbon-dark seams use authored rough solid materials. Bevels precede local box UV assignment. Explicit corner normals preserve shading across export. All components remain separately editable under PlacementRoot, without regenerating any previous source.

## Verification scope

The verifier reopens native Blender and independently imports GLB. Checks cover closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, actual corner normals within 0.001, transforms/bounds, source/helper/binary hashes, packed image bytes and decoded material/map parity, box UVs and three measured dents.

Odd/even actual mesh containment checks six bridge/rail interior points, eight band roots with clear annular-axis witnesses, four end fittings, 99 fitted-overlay contacts and eight fasteners. Two additional rays through the full assembly must pass freely through the fore/aft centre gaps. These are scoped contact/clearance samples, not exhaustive structural proof. AlignmentForward is checked under four rigid root rotations without source heading, socket or animation calibration claims.

Actual native/imported Blender renders exercise the standalone modelling runtime. Whole-object framing, intentional detail crops and matched-camera alpha/silhouette/pixel checks remain separate from artistic acceptance. Eight paletted headings are compared qualitatively; all-heading inspection and original crops remain ignored reference evidence. Game-client integration is unchanged.

## Deferred

Exact rail/bridge/gap proportions, gold placement, end-fitting shapes/functions, hidden structures, two calibrated equipment mounts, runtime scale/orientation and required operational/damage variants remain unresolved. Technical correctness does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.

The actual gallery and original-heading comparison were inspected. First-version verification passed in Blender 4.5.15 for 28 meshes/four materials, including eight mapped meshes. Two rail dents measured approximately 0.00297 model units each; the bridge dent measured about 0.00357. Maximum actual corner-normal vector error was approximately 0.000648 (bound 0.001). Nine rendered views passed framing/export checks: both matched-camera alpha channels and threshold-128 silhouettes are identical, with maximum foreground mean colour difference below 0.005/255. Cultural-source validation passed for six architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `6b52279d`. Existing models were not regenerated or refined.
