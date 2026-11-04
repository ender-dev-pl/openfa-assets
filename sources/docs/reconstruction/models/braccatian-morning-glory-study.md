# Braccatian Morning Glory — first authored iteration (#1010)

`openfa:ship/braccatian/morning-glory`, global type 18, Braccatian local type 3, role class 1. The gameplay catalogue supplies only the generic ship tag. No study was registered in the authoritative inventory. This creates a missing first source and preserves all previous reconstructions/refinements. Artistic refining remains deferred.

## Source evidence

BR3C.256 is absent; the runtime fallback selects BR3A.256. All 32 populated, correctly paletted headings were inspected. The sprites are only approximately 8–18 pixels wide and 9–12 pixels high. They support a narrow gold spindle with a grey end, a broader rose terminal and a bright gold/cream central patch. No larger catalogue video is located. These sprites do not resolve exact sections, mechanisms, service detail or front/rear calibration.

The functional text index maps the name but no narrative. Four gameplay equipment slots have no recovered mount coordinates; metadata binds the catalogue hash and records four declared slots / zero calibrated 3D mounts. No visible tip, collar or bright patch is assigned to those slots or given a weapon/engine/sensor function. The model's rose-ended local -Y alignment is explicitly authored and uncalibrated.

The original ENGLISH.CDB Braccatian Architecture article, record 47 at 0x2142, describes lavish decorated building surfaces. Its use for small gold appliques, rim studs and framed service surfaces is contextual extrapolation, not evidence of spacecraft geometry or clan insignia. No heraldry is invented. Cultural/reference indexes, generators and helper hashes are bound in metadata. Original pixels remain reference-only, never model/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/braccatian/morning-glory/` contains editable Blend/GLB, four independent gold/rose colour and roughness maps, provenance, actual render gallery and technical reports. This silhouette differs sufficiently from the prior Braccatian sources to warrant new geometry rather than fitting an existing hull to it. Authoring/render/verification infrastructure is reused; previous source assets are unchanged.

Forty closed meshes/four materials comprise a gold tapered spindle, broad rose terminal, gold terminal-face volume and short rose axial tip, three fitted annular bands/collars, grey shaft terminal, four gold crown appliques, four rose shaft inlays, two service covers with six slots, eight cover fasteners and eight terminal rim studs. All four primary profiles have explicit triangle-fan caps. Sixteen closed conformal overlays follow actual host profiles and include exact section breaks without duplicate row heights. Bright-face and axial-tip construction are independent interpretation of the unresolved central source patch, not recovered mechanisms.

Two shallow physical dents, analytic stains, grain and seeded scratches supply new-object wear. Two packed image materials cover 24 meshes; oxidized titanium and carbon-dark joints use authored rough solid materials. Bevels precede local box UV assignment. Explicit corner normals preserve shading across export. All components remain separately editable under PlacementRoot.

## Verification scope

The verifier reopens native Blender and independently imports GLB. Checks cover closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, actual corner normals within 0.001, transforms/bounds, source/helper/binary hashes, packed image bytes and decoded material/map parity, local box UVs and both measured dents. Contact checks include nine shared interior primary-joint points, 144 fitted surface samples, twelve annular collar roots, grey terminal attachment, eight cover fasteners and eight terminal rim studs. Samples are scoped geometric evidence, not exhaustive structural proof.

AlignmentForward is checked through four rigid root rotations; no animation timing, heading calibration or complete variant coverage is inferred. Actual native/imported Blender renders exercise the standalone modelling runtime. Whole-object framing and intentionally cropped detail views are checked separately. Matched-camera alpha/silhouette/pixel comparisons remain distinct from artistic acceptance. Eight paletted headings are compared qualitatively; the complete bank inspection and original crops remain ignored reference evidence. Game-client integration is unchanged.

## Deferred

Exact proportions and end orientation, gold/rose material divisions, bright-face shape, tip/grey-end construction and function, hidden details, four calibrated equipment mounts, runtime scale/orientation and required operational/damage states remain unresolved. Technical correctness does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.

The actual gallery and original-heading comparison were inspected. In particular, the spindle/terminal length ratio is an authored estimate and remains a later proportion-review item; the tiny source is not a calibrated camera match. First-version verification passed in Blender 4.5.15 for 40 meshes/four materials, including 24 mapped meshes. Measured dents were approximately 0.00302 and 0.00397 model units. Maximum actual corner-normal vector error was 0.000706 (bound 0.001). Nine actual views passed framing/export checks: threshold-128 silhouettes are identical; front-quarter/detail alpha differences affect two/four edge pixels respectively, maximum 4/255, within existing tolerances. Maximum foreground mean colour difference is below 0.003/255. Cultural-source validation passed for six architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `d9c98e4f`. Existing models were not regenerated or refined.
