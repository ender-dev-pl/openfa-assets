# Rigellian Transportation — first authored iteration (#1005)

`openfa:ship/rigellian/transportation`, global type 13, Rigellian local type 3. The authoritative inventory contained no source model. Existing reconstructions/refinements are preserved. This pass creates first versions only; further artistic refining remains deferred.

## Source evidence

`ship-reference-index.json` binds RI3C.256, a 32-entry paletted heading bank approximately 89-90 by 26-27 pixels. Actual headings 0/4/8/12/16/20/24/28 show two inline rounded masses with a narrow connection, a larger slate/blue forward mass, greener tapering rear mass, gold upper detail and brown terminal/rim features. No large catalogue video was located. Source front/rear orientation remains a calibration question rather than a recovered model axis. The runtime uses even heading samples only; rigid model rotation does not calibrate those headings.

ENGLISH.CDB Rigellian Architecture record 18 at 0x971 supports ergonomic/elegant construction as contextual ship guidance. Model metadata binds the cultural index hash. The article does not specify this vessel's hidden geometry, mechanisms, colours or materials. The functional index has no mapped narrative and the catalogue declares no equipment slots/mount coordinates; none are invented. AlignmentForward is an authored uncalibrated helper, not a weapon or sensor axis.

Original images are reference-only and absent from mesh/texture inputs. The reviewer validates palette metadata/canonical decoded hashes and records actual comparison-heading hashes.

## First assembly

`docs/assets/reconstruction/ships/rigellian/transportation/` contains editable Blend/GLB, six independent slate/green/copper colour and roughness maps, provenance, technical report and actual rendered gallery. Nineteen meshes and six materials comprise separate closed forward/aft hulls with a shared internal neck, copper terminal, closed curved oval gold forward patch, two curved copper aft strips, two service covers with dark slots, four fasteners and a small ventral connecting saddle.

Two measured dents, analytic stains, grain and seeded scratches supply new-object wear. Small components use rough alloy/joint/gold material values. The gold oval and copper strips have embedded closed back surfaces and follow the actual analytic module skin; they are not floating flat decals. Bevels precede local box UV assignment. Explicit authored corner normals retain native/imported shading consistency. PlacementRoot uses authored local -Y forward.

## Verification scope

The verifier reopens native Blender and independently imports GLB. Native physical meshes must be closed with positive volume. Diagnostic-only 1e-6-unit seam welding accounts for imported UV/flat-normal duplicates and must recover exact native geometric vertex counts. Files are not mutated. Other checks cover bounds/transforms, packed source image bytes/decoded colour/roughness pixels, all three image materials and local UV projections, explicit actual corner-normal vectors within 0.001, two dent depths, common interior forward/aft neck and terminal/saddle contacts, curved oval/strip roots and cover/fastener attachment samples. AlignmentForward is checked under four rigid root rotations without asserting source animation timing or heading calibration.

Actual native/imported Blender renders exercise the standalone target runtime. Whole-object framing, intentional hull-detail crops and matched-camera export comparisons remain distinct from artistic acceptance. Contact samples provide scoped correctness evidence, not exhaustive structural proof. Client integration is unchanged.

## Deferred

Exact module proportions, front/rear calibration, connection shape, source finish/marking subdivisions, hidden structures, required operational/damage variants and calibrated game scale/orientation remain for later review. Fine service detail is independently authored below the available pixel resolution. No final artistic acceptance gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version verification passed in Blender 4.5.15 for 19 meshes and six materials. Nine actual views passed framing/export comparison. Both matched-camera alpha channels and threshold-128 silhouettes are identical; foreground mean channel differences remain below 0.004/255. Cultural-source validation passed for six original architecture articles. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `441639b5`. Existing models were not regenerated or refined.
