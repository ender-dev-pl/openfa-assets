# RI23 Ultrathermal Lance — first authored iteration (#995)

Catalogue ID `openfa:building/legacy/062`, global type 62, nominal 3x3 footprint. This pass generates first versions only. Existing reconstructed/refined assets are preserved and further artistic refining remains deferred.

## Evidence and interpretation

Original ENGLISH.TXT at 0x11995 describes the most effective anti-ship weapon. The correctly paletted fixed-base sprite (descriptor 1) shows a flared green pedestal over a bronze skirt, a front circular fitting and a small green spur. Directional descriptors 2..17 show the upper green assembly and paired bronze lances; layer-combination previews retain the fixed base. Catalogue reveal phases are not spatial rotations or firing timing.

The first independent mesh interprets these as a fixed skirt/pedestal/bearing, a rounded yaw head and two parallel tapered bronze lances. Exact profiles, hidden root construction, cross-sections and pivot height are inferred. There is no asserted pitch mechanism or invented firing effect. Original images are reference-only and are not mesh/texture inputs.

## Deliverables and technical scope

Editable Blender and GLB files, eight independent colour/roughness maps, provenance and render reports are in `docs/assets/reconstruction/buildings/rigellian/ultrathermal-lance/`. Five physical dents, joint contamination, handling marks, grain and seeded scuffs provide wear. Small fittings and spur have independent solid alloy materials.

Thirteen closed mesh objects and seven materials form one ground-centred PlacementRoot assembly. The head and both lances share YawPivot; each lance has its own local +Z tip socket. The verifier reopens native Blender and imports GLB separately, checking four quaternion yaw poses, stationary base bounds, both tip positions/directions, transforms, packed image bytes and decoded pixels, cylindrical/planar UVs, ten planar caps and material export quantization.

Contact samples require shared interior points at skirt/base, base/bearing, bearing/head, both lance roots and the spur root. The front fitting has 32 root samples and a face/rim overlap check; strips are checked against their owning pedestal or skirt. Five local dent depths are measured. These samples establish scoped correctness rather than exhaustive engineering proof.

Actual native/imported Blender renders exercise the standalone runtime. Whole-object views, intentional macro crops and three matched-camera export comparisons are checked. Client renderer/integration is unchanged; calibrated game direction mapping is not inferred from rigid yaw tests.

## Deferred acceptance

Artistic refining, final silhouette/finish acceptance, operational/damage variants, runtime scale/orientation/placement and any further evidenced mechanism remain for later passes. Scaffolding is separately deferred under #983. No final artistic acceptance gate is promoted.

First-version verification passed in Blender 4.5.15 for thirteen meshes/seven materials and eleven render views. Three matched-camera native/imported comparisons have identical alpha and threshold-128 silhouettes. The rear/side/top gallery makes the paired lances visible; the front-quarter camera overlaps their projections. The source skirt front has additional stepped/ladder-like detailing absent from this initial smooth skirt; preserve this as an explicit later detail gap, without claiming artistic completion. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `fb628611`.
