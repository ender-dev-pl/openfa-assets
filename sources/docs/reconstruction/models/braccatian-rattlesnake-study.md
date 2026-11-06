# Braccatian Rattlesnake — first authored iteration (#1007)

`openfa:ship/braccatian/rattlesnake`, global type 15, Braccatian local type 0, role class 2; the gameplay catalogue tags it as a scout. No source study was registered in the authoritative inventory. This creates a missing first version and preserves every existing reconstruction/refinement. Artistic refining remains deferred.

## Evidence and limits

BR0C.256 is absent; the runtime fallback selects BR0A.256. Its 32 correctly paletted headings are tiny: approximately 5–19 pixels wide and 7–16 pixels high. All 32 headings were inspected. They show an elongated warm copper/pink body with a lighter gold end and a thicker raised opposing end. Large wings or separate large engine pods are not established. No larger catalogue video is located. Exact profile sections, hidden depth and front/rear calibration are unresolved; the model's local -Y gold prow is an authored orientation, not a recovered heading calibration.

The functional text index maps the name but no narrative. The gameplay catalogue supplies the scout tag and two equipment slots without mount coordinates. Model metadata binds the catalogue hash and records two declared slots / zero calibrated 3D mounts. AlignmentForward is explicitly an authored uncalibrated helper, not a weapon mount or proof of machinery.

The original ENGLISH.CDB Architecture article for Braccatians, record 47 at 0x2142, describes large lavishly decorated buildings and communal/clan facilities. Its use for a small vessel's restrained gold inlay and carefully framed service surfaces is contextual extrapolation. It establishes neither ship geometry nor specific heraldry, materials or colour; no clan symbols are invented. The cultural index and reference hashes are bound in metadata. Legacy image pixels remain reference-only and are absent from all mesh/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/braccatian/rattlesnake/` contains the editable Blend/GLB, independent colour/roughness maps, provenance, actual native/imported render gallery and technical reports. The first source has two separately closed overlapping main forms: a warm copper body with rounded rectangular sections, a thicker aft end, and a raised pale gold prow with elliptical sections. Both are densely sampled editable profiles with explicit triangle-fan end caps.

Twenty-one closed body-fitted overlays supply two narrow longitudinal gold inlays, five transverse inlays, central/aft service covers and slots, a copper prow stripe and a ventral service keel/slots. Ten small service fasteners remain independent geometry. Inlays avoid coplanar overlap with the service covers and each other. Fitted overlay rows include exact profile breaks and merge numerically coincident row heights before faces are generated. This preserves thickness and export topology at sharp section transitions.

Two shallow physical dents, analytic stains, grain and seeded scratches supply new-object wear. Two image materials use four packed independent colour/roughness maps on 13 meshes; oxidized service alloy and carbon-dark joints use authored rough solid materials. Bevels are applied before local box UV assignment. Explicit authored corner normals preserve native/imported shading. The 33 meshes and four materials remain separate and editable under PlacementRoot.

## Verification scope

The verifier reopens the native Blend and independently imports GLB. Checks cover closed positive physical meshes, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, mesh transforms/bounds, actual corner normals within 0.001, source/binary/helper hashes, packed image bytes and decoded colour/roughness/material parity, local box UVs, both measured dents, three shared interior prow/body points, 189 fitted overlay root/contact samples and ten fastener roots. Raised slot faces are checked against their actual fitted covers, while covers/inlays are checked against the pressure hull. Diagnostic welding does not modify the exported asset.

The helper's position/axis is checked through four rigid root rotations. No animation timing, equipment calibration or complete variant coverage is inferred. Actual native/imported Blender renders exercise the standalone modelling runtime; matched-camera alpha/silhouette/pixel checks and framing are separate from artistic acceptance. Eight paletted heading crops and all 32 inspected reference headings remain in ignored reference evidence; comparison is qualitative, not a calibrated camera match. Game-client integration is unchanged.

## Deferred

Exact proportions, end orientation, cross-sections, material subdivisions and markings; hidden machinery, two equipment mounts, calibrated runtime scale/orientation and required operational/damage variants remain unresolved. These are first-source geometry and provenance, not final artistic acceptance. Further artistic refining and construction scaffolding (#983) remain deferred.

The actual gallery and comparison sheet were inspected. The prow/body underside intersection outline is not a recovered seam and remains a later joint/proportion review question. No artistic gate is promoted from this inspection.

First-version verification passed in Blender 4.5.15 for 33 meshes/four materials, including 13 meshes using authored image maps. Measured dent depths were approximately 0.00395 and 0.00303 model units. Maximum actual corner-normal vector error was 0.000728 (bound 0.001). Nine actual views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical, with maximum foreground mean channel difference below 0.006/255. Cultural-source validation passed for six original architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. The required changed-code quality gate passed against milestone base `bf8e89d2`. Existing models were not regenerated.
