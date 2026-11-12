# Braccatian WidowMaker — first authored iteration (#1008)

`openfa:ship/braccatian/widowmaker`, global type 16, Braccatian local type 1, role class 6. The gameplay catalogue tags it `combat-direct-approach`. No study was registered in the authoritative inventory. This creates a missing first source and preserves existing reconstructions/refinements. Artistic refining remains deferred.

## Source evidence

BR1C.256 supplies 32 correctly paletted headings, approximately 35–81 pixels wide and 35–39 pixels high. All headings were inspected. They show a gold body widening toward the broad end, a rose circular nose, grey side armour and thin longitudinal projections, four round dark openings at the broad end, and rose marks near the neck. BR1A is absent; no larger catalogue video is located. Exact cross-sections, hidden surfaces, radial panel/strake arrangement and front/rear calibration remain interpretation. The model uses an authored local -Y nose orientation.

The functional text index maps the name but no narrative. The gameplay catalogue supplies four equipment slots without mount coordinates. Metadata binds that catalogue hash and records four declared slots / zero calibrated 3D mounts. The four visible round openings are not assigned to those slots, and their mechanical function is not established. AlignmentForward is an authored uncalibrated helper, not a weapon/sensor mount. Duct-style geometry describes the authored housing, not a recovered engine/weapon mechanism.

The original ENGLISH.CDB Braccatian Architecture article, record 47 at 0x2142, supports lavish decoration for buildings. Its use for a vessel's independent rose neck accents and framed service treatment is contextual extrapolation, not proof of ship geometry, material or heraldry. No clan insignia is invented. Metadata binds the cultural/reference indexes and helper sources. Original paletted pixels are reference-only, never mesh or texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/braccatian/widowmaker/` contains editable Blend/GLB, six independent rose/gold/grey colour and roughness maps, provenance, technical reports and actual rendered views. Forty-eight closed meshes and five materials comprise two overlapping pressure forms, four body-fitted tapered grey cheeks, four thin diagonal strakes, four hollow aft housings with recessed dark floors, a body-fitted central nose casting/face, four gold nose studs, eight independently drawn rose neck accents, two fitted service covers with six slots and eight fasteners.

The primary profiles have explicit triangle-fan end caps. Twenty closed conformal overlays follow the actual analytic body surface, including shallow dents; exact profile/width breaks are included without duplicate row heights. Cheeks embed into the pressure hull; covers embed into cheeks, and slots/fasteners into covers. The annular housings have continuous inner walls and open axes, with separate recessed floors. Their geometry, count and placement do not establish calibrated equipment mounts or operating states.

Two shallow physical dents, analytic stains, grain and seeded scratches supply new-object wear. Three packed image materials cover 36 meshes; oxidized titanium and carbon-dark recesses use rough authored solid materials. Bevels precede local box UV assignment. The new nose casting resolves any sub-micron bevel slivers before UVs/normals. Explicit corner normals preserve shading across export. All components remain separately editable under PlacementRoot.

## Verification scope

The verifier reopens native Blender and independently imports GLB. Checks cover closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, transforms/bounds, actual corner normals within 0.001, source/helper/binary hashes, packed source image bytes and decoded texture/material parity, box UVs, both measured dents, shared nose/body interior points, 180 fitted overlay contacts, 12 strake roots and 16 housing roots. Additional checks cover floor/body/housing overlaps, four genuinely open housing axes and recessed floors, 32 nose-casting root samples, nose-face overlap, four nose studs and eight cover fasteners. These samples are scoped contact evidence, not exhaustive structural proof.

The alignment helper is checked through four rigid root rotations. No animation timing or heading/mount calibration is inferred. Actual native/imported Blender renders exercise the standalone modelling runtime. Framing, matched-camera alpha/silhouette/pixel checks and qualitative comparison against eight paletted headings remain separate from artistic acceptance. The complete 32-heading inspection and original crops remain ignored reference evidence. Game-client integration is unchanged.

## Deferred

Final proportions, exact armour/strake arrangement and finish, front/rear calibration, hidden joints and machinery, the round openings' function, four equipment mounts, calibrated runtime scale/orientation and required operational/damage states remain unresolved. Artistic refining and construction scaffolding (#983) remain deferred. This first source does not promote final acceptance or variant/attachment gates.

The actual gallery and original-heading comparison were inspected. The authored cheek faceting and simplified neck accents remain later finish/artistic questions. First-version verification passed in Blender 4.5.15 for 48 meshes/five materials, including 36 mapped meshes. Measured dent depths were approximately 0.00497 and 0.00404 model units. Maximum actual corner-normal vector error was 0.000668 (bound 0.001). Nine actual views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical, with maximum foreground mean channel difference below 0.003/255. Cultural-source validation passed for six architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `2758d736`. Existing models were not regenerated or refined.
