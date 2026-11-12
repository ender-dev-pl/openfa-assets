# RI19 Thermal Lance — first authored iteration (#991)

Catalogue ID `openfa:building/legacy/058`, global type 58, nominal 3x3 footprint. This is a first version; artistic refining remains deferred under `programme.json.current_pass`. Existing reconstructions/refined models are preserved.

## Function and directional evidence

Original ENGLISH.TXT record 919 at byte offset 0x117A1 identifies an anti-ship weapon. Correctly paletted fixed base, all sixteen base-plus-directional-overlay combinations 2..17 and catalogue frames were inspected. The base remains fixed while the rounded upper head and tapered lance change direction. Visible bronze details include a base strip/side fitting and a small upper fitting. Reveal phases are not operating-animation timing.

Exact profiles, rear construction, fitted strip details, pivot height, fixed lance elevation and the tip socket are independently authored interpretations. Yaw separation is supported by the directional bank; pitch articulation, firing effects and exact runtime direction-angle mapping are not established. No original image pixels enter mesh or texture authoring.

## First-version rig and assets

The model has `PlacementRoot`, a local +Z `YawPivot` and `LanceTipSocket`. Only the upper head, lance and upper fitting assembly parent to the yaw pivot. The fixed pedestal and lower fittings remain under the placement root. The socket sits at the actual lance end and uses local +Z as an authored forward axis. No animation timing or firing clip is invented.

Editable Blend, standalone GLB, four independent green colour/roughness maps, metadata, reports and eleven actual 900x900 renders are under `docs/assets/reconstruction/buildings/rigellian/thermal-lance/`. Three shallow geometric dents, restrained joint contamination, handling marks, grain and scratches provide an initial worn finish. Small bronze/metal fittings use independent material values. Original comparisons remain in ignored `artifacts/rigellian-building-reference-study/RI19/`.

## Technical verification

The verifier reopens native Blender and independently imports GLB. It checks positive closed topology, identity root/3x3 bounds, individual transforms/bounds, three local-space dents, bearing/head/lance contact, fitted pedestal strips and 32 sampled flange roots per fitting plus embedded faces. It verifies local cylindrical/planar UVs, six planar caps, packed image bytes, decoded colour/roughness pixels, material quantization and reference/function index hashes.

In both native and imported models it rotates yaw through 0/90/180/270 degrees, checks that all fixed geometry bounds stay unchanged, and verifies the actual lance endpoint, socket position and forward axis against the corresponding rigid rotation. The source bank's exact runtime angle assignment is not inferred from this technical test.

The first imported check found that the shared exporter omitted custom socket properties. This model now exports glTF extras through a local wrapper, preserving pivot/socket metadata without changing shared exporters or older assets. The imported pivot uses quaternion rotation mode; the yaw check therefore drives explicit quaternions in both formats rather than assigning inactive Euler values. Geometry/appearance was not artistically refined during these corrections.

Whole-object framing and three matched-camera native/imported comparisons are technical render checks. Intentional macros may crop the whole assembly. Blender native/imported GLB is the standalone milestone's target runtime; client integration is unchanged.

## Later passes

The first generated geometry is retained without an artistic-refinement cycle. Precise proportions/finish, source/runtime yaw calibration, any pitch/effects supported by further evidence, construction/damage variants and game placement remain open. No final artistic gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for twelve mesh objects and five materials. All four yaw tests passed independently in native Blend and imported GLB. Eleven render views passed framing and all three matched-camera pairs have identical threshold-128 silhouettes and alpha. Full inventory verification passed for 303 definitions / 1444 reference occurrences; required changed-code quality verification passed against milestone base `31596b62`.
