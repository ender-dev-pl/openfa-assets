# Messier-Lukannon — first authored iteration (#1004)

`openfa:ship/rigellian/messier-lukannon`, global type 12, Rigellian local type 2. The authoritative inventory registered no source model. Existing reconstructions/refinements are preserved. Current work generates first versions only, with artistic refining deferred.

## Sources and style context

`ship-reference-index.json` binds RI2C.256, a 32-entry correctly paletted heading bank around 60 by 23-27 pixels. Actual headings 0/4/8/12/16/20/24/28 show a flattened slate/green hull, copper/brown terminal and side details, small gold upper features and brown lateral/ventral projections. No large catalogue animation was located. The reviewer validates original palette metadata/canonical frame hashes and records actual comparison-heading hashes. Original pixels remain reference-only.

The user's cultural-source guidance is now indexed in `cultural-architecture-index.json`. ENGLISH.CDB Rigellian Architecture record 18 at 0x971 describes ergonomic, elegant construction, including mining facilities. The metadata binds this index hash. Coherent curved hull transitions and integrated interfaces are contextual authoring decisions for this ship, not recovered geometry or direct spacecraft specifications. The article does not mandate a particular metal, colour or universal curved shape. Other cultures' articles are separately indexed with the same observed-versus-interpreted distinction; existing models are not retrofitted.

The functional text index has no mapped narrative for this definition. No equipment slots or designer mount coordinates are declared, so none are invented. Brown side bosses and ventral wings are opaque interpreted structures, not confirmed weapon or propulsion components. AlignmentForward is an authored uncalibrated helper, not a recovered weapon/sensor axis.

## First assembly

`docs/assets/reconstruction/ships/rigellian/messier-lukannon/` contains editable Blend/GLB, four independent slate/copper colour/roughness maps, provenance, technical report and actual render gallery. Twenty-six meshes and five materials interpret the source as a flattened rounded hull, copper terminal, two swept lower wings, four body-fitted side bosses/faces, slate service covers/slots, gold dorsal fittings and small wing pads.

Two measured geometric dents, analytic stains, grain and seeded scratches supply new-object wear. Small parts have rough alloy/joint/gold material values. Applied bevels precede box UV mapping, with explicit authored corner normals for native/imported shading consistency. PlacementRoot uses authored local -Y forward.

Initial side-boss flange checks found one planar front partially buried in the convex hull. Its mounting clearance was increased while retaining the sampled embedded root. This is a first-version technical contact correction, not a refining cycle. All four bosses retain 32 independent root samples each.

## Verification scope

Native Blender is reopened and GLB imported separately. Native meshes must be closed with positive volume. Diagnostic-only seam welding at 1e-6 units accounts for glTF UV/normal splits and must recover exact native geometric vertex counts; files are not mutated. Other checks cover bounds/transforms, packed source image bytes/decoded pixels, UV projections, actual corner normals within 0.001 vector difference, two measured dents, terminal/wing/pad/cover/dorsal-fitting contacts, 128 boss-root samples and four face/rim overlaps. The alignment helper is tested at four rigid root rotations without asserting calibrated sprite headings or animation timing.

Actual native/imported Blender renders exercise the standalone runtime. Whole-object framing, intentional hull-detail crops and matched-camera export comparisons are distinct from final artistic acceptance. Client integration is unchanged. Contact samples are scoped evidence, not exhaustive structural proof.

## Later gaps

Exact flattened hull proportions, terminal orientation, boss arrangement, ventral projection profile, source finish/colour matching, hidden surfaces, required state variants and calibrated game scale/orientation remain for later review. Fine service detail is independently authored below the available pixel resolution. No final artistic gate is promoted. Further refining and construction scaffolding remain deferred, the latter separately under #983.

Final first-version verification passed in Blender 4.5.15 for 26 meshes and five materials. Nine actual views passed framing/export comparison. Both matched-camera alpha channels and threshold-128 silhouettes are identical; foreground mean channel differences remain below 0.005/255. Cultural-source validation passed for six architecture sections with original record/offset/hash anchors. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `895c7e7a`. No previous model was regenerated or refined.
