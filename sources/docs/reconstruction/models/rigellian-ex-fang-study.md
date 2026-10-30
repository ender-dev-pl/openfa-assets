# RI22 Ex-Fang — first authored iteration (#994)

Catalogue ID `openfa:building/legacy/061`, global type 61, nominal 4x4 footprint. This is a first iteration only; artistic refining remains deferred under `programme.json.current_pass`. Existing reconstructions and refined versions are preserved.

## Function and evidence

ENGLISH.TXT record 922 at byte offset 0x118D8 describes an energy weapon draining attacking fleets, with its exact operating method uncertain. Correctly paletted RI22 surface descriptor 1 is empty; descriptors 2 through 17 contain sixteen complete directional building sprites, rather than separate base and turret overlays. The catalogue animation provides additional views, without establishing mechanical timing.

The visible green pedestal, inclined support, large round collector, copper central feed and four bronze fittings guide the independent model. Concavity, hidden supports, the fixed/moving division and pivot height are authored interpretations. No pitch animation, discharge effect or unsupported operating mechanism is supplied. Original pixels are reference-only and absent from generated mesh/texture inputs.

## Initial assets and verification

`docs/assets/reconstruction/buildings/rigellian/ex-fang/` contains editable Blender and GLB files, eight independent colour/roughness maps, metadata and technical/render evidence. The assembly has sixteen meshes, nine materials, a closed concave collector, three profile dents and one collector dent. Joint dirt, patina, scratches and handling marks implement the worn finish for new objects.

PlacementRoot preserves a ground-centred 4x4 assembly. YawPivot carries eleven meshes; CollectorAxisSocket uses local +Z. Native Blender and imported GLB are checked at four quaternion yaw angles for rigid geometry, stationary base and socket position/direction. This does not establish calibrated game direction mapping.

Checks cover positive closed meshes, materials and packed texture bytes/pixels, local cylindrical/planar UVs, source/helper hashes, collector thickness/concavity and sampled contacts for supports, feed, bearing, yoke caps, four fittings and base insets. The feed root is embedded in the shell; the attachment check requires a common interior sample. Contact samples are technical evidence rather than exhaustive structural proof. The first geometric layout is otherwise retained without artistic refining.

Actual native/imported Blender renders exercise the standalone target runtime. Whole-object framing, three matched-camera export comparisons and intentionally cropped detail views are checked separately. Client integration is unchanged.

## Deferred

Final proportions and finish, artistic acceptance, runtime scale/orientation and direction calibration, operational/damage variants and any evidenced pitch/effects belong to later passes. Construction scaffolding remains separately deferred under #983. No final artistic acceptance gate is promoted.

First-version checks passed for sixteen meshes and nine materials in Blender 4.5.15. Eleven render views passed framing and export comparison. Whole-object and collector-detail binary silhouettes match exactly. The base macro has one threshold-128 edge crossing; all four changed alpha pixels differ by at most 4/255. The render check permits only up to four such fractional edge crossings, with both alpha values in 124..131; opaque/interior silhouette mismatches remain rejected. Full inventory verification passed for 303 definitions and 1444 reference occurrences. Required changed-code quality verification passed against milestone base `237132c1`.
