# RI20 Extractor — first authored iteration (#992)

Catalogue ID `openfa:building/legacy/059`, global type 59, nominal 2x2 footprint. First iterations only: artistic refining remains deferred under `programme.json.current_pass`. Existing reconstructed/refined models are preserved.

## Functional and visual evidence

Original ENGLISH.TXT record 920 at byte offset 0x117E4 identifies a single mining device handling all ores. Correctly paletted surface body (28x38) and readable catalogue phase show a rounded bronze main housing, side module/round details, dark narrow front features, lower stepped base and green lower element. Reveal phases are not rotations or operating animation.

Exact profiles, unseen rear/bottom construction, fitting interfaces and lower-element function are independently authored interpretations. Dark features are represented as fitted inlays, not asserted to be exhaust ports. The source's green colour features do not by themselves prove plumbing; independently generated patina is a surface treatment. No unsupported external drill or operating motion is invented. Original image pixels are absent from mesh and texture authoring.

## Initial assets

Editable Blend, standalone GLB, eight independently generated source maps, metadata, technical/render reports and eleven actual 900x900 views are under `docs/assets/reconstruction/buildings/rigellian/extractor/`. Four measured geometric dents, restrained joint dirt, handling marks, grain, scratches and local green patina provide an initial worn finish. Original comparisons stay in ignored `artifacts/rigellian-building-reference-study/RI20/`.

A small reusable closed-profile-strip helper creates the fitted dark inlays. Existing RI19 geometry/scripts and their evidence hashes are unchanged. This model binds the new helper hash in its metadata.

## Technical verification

The verifier reopens native Blender and independently imports GLB. It checks positive closed topology, identity placement/2x2 bounds, individual transforms/bounds, four actual dents, main/base/side/green-fitting overlap, dark-inlay contact samples, five root samples on each of seven round details, and 32 upper-fitting flange-root samples plus embedded face.

It verifies local cylindrical/planar UVs, eight planar caps, eight packed source-image byte hashes, decoded colour/roughness pixel equality, material export quantization and reference/function index hashes. Contact samples are scoped checks, not exhaustive mechanical proof. Whole-object framing and three matched-camera comparisons are technical render checks; macro crops are intentional. Blender native/imported GLB is the standalone target runtime; client integration is unchanged.

## Later passes

The first generated geometry is retained without an artistic-refinement cycle. Precise proportions/finish, hidden engineering, operational/damage variants and game scale/orientation/placement remain for later passes. No final artistic gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for seventeen mesh objects and seven materials. Eleven render views passed framing; all three matched-camera native/imported pairs have identical threshold-128 silhouettes and alpha. Full inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `21a6853a`.

A source-format follow-up removes an extra blank line at the end of the new strip helper and refreshes its provenance hash and model reports. Python AST comparison confirms unchanged helper semantics; decoded GLB triangle coordinates match the first committed geometry at 1e-6 precision despite binary/export ordering differences. Native/imported checks and render checks were rerun after the source-format correction.
