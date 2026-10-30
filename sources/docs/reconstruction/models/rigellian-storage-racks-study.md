# RI21 Storage Racks — first authored iteration (#993)

Catalogue ID `openfa:building/legacy/060`, global type 60, nominal 3x3 footprint. First iterations only; artistic refining remains deferred under `programme.json.current_pass`. Existing reconstructions/refined models are preserved.

## Function and visual evidence

Original ENGLISH.TXT record 921 at byte offset 0x118AF identifies ore storage. Correctly paletted surface body (35x49) and readable catalogue phase show clustered bronze housings in two visible tiers, five green oval details and grey front guides. Reveal phases do not establish rotations or loading animation.

The first version interprets the cluster as six housings. Exact profiles, hidden rear cradles/spines, face interfaces and support arrangement are independently authored interpretations. No unseen lower-central green face is asserted. Green faces are opaque materials without invented emission or glass behaviour. Original pixels are reference-only and absent from mesh/texture inputs.

## Initial assets

Editable Blend, standalone GLB, four independently generated bronze colour/roughness maps, metadata, technical/render reports and eleven actual 900x900 views are under `docs/assets/reconstruction/buildings/rigellian/storage-racks/`. Six geometric dents, joint dirt, handling marks, grain, scratches and local patina provide an initial worn finish. Small green faces and rack/rim fittings use independent material values. Original comparisons remain in ignored `artifacts/rigellian-building-reference-study/RI21/`.

Six separate housing meshes, five oval faces with body-fitted rims, two rear spines, two front guides and tiered cradle/tie members form one editable placement assembly. The first generated layout is retained without an artistic-refinement cycle.

## Technical verification

The verifier reopens native Blender and independently imports GLB. It checks positive closed topology, identity placement/3x3 bounds, individual transforms/bounds, six measured dents, housing/cradle attachment samples at both ends of each tier edge, rear spine/tie and housing/tie contact, front guide attachments, 32 flange-root samples per each of five rims and five face/rim attachment samples per oval.

Initial axial containment rays sometimes hit exactly along shared edges at cylindrical support extrema, returning only one surface. A saved-model diagnostic located those edge hits; the containment line is now oblique. It still requires the sample to lie strictly between both surfaces, without weakening the contact requirement or changing geometry.

It also verifies local cylindrical/planar UVs, twelve planar caps, four packed image source byte hashes, decoded colour/roughness pixel equality, material export quantization and reference/function index hashes. Samples are scoped technical evidence rather than exhaustive structural engineering proof. Whole-object framing and three matched-camera native/imported comparisons are render correctness checks; macro crops are intentional. Blender native/imported GLB is the standalone target runtime; client integration is unchanged.

## Later passes

Exact proportions/finish, hidden supports, operational/damage variants and game scale/orientation/placement remain for later passes. No final artistic acceptance gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for thirty-two mesh objects and five materials. Eleven render views passed framing; all three matched-camera native/imported pairs have identical threshold-128 silhouettes and alpha. Full inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `0a12fb11`.
