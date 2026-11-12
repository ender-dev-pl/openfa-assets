# RI17 Arms Unit — first authored iteration (#989)

Catalogue ID `openfa:building/legacy/056`, global type 56, nominal 3x3 footprint. This is the first authored version, with artistic refining deferred by the user. Existing reconstructed/refined assets are preserved.

## Functional and visual evidence

Original ENGLISH.TXT record 917 at byte offset 0x11688 identifies the Arms Unit as a weapons factory. Correctly paletted surface body (36x40) and readable catalogue phase show a low grey annular housing with an open central recess, green interior element, red inner-wall detail, underside ribs and a tall green mast with a bronze spear-like head. Reveal/highlight phases are not rotations or evidence of operating machinery.

Exact profiles, cavity depth, low floor, unseen rear/bottom geometry, rib count, panel support and roof fitting construction are independently authored interpretations. An open recess is modelled without inferring an underground hangar, launch silo or grille. No moving mechanism is established. Legacy pixels remain reference-only and are absent from mesh/texture inputs.

## Initial deliverables

Editable Blend, standalone GLB, twelve independent source maps, metadata, technical/render reports and eleven actual 900x900 views are under `docs/assets/reconstruction/buildings/rigellian/arms-unit/`. Four geometric dents and analytic bronze/green/grey colour/roughness maps provide restrained joint dirt, handling marks, grain and scratches. Original comparison pixels stay under ignored `artifacts/rigellian-building-reference-study/RI17/`, outside distributable assets.

## Technical checks

The verifier reopens native Blender and independently imports GLB. It checks positive closed topology, identity root and 3x3 placement bounds, individual transforms/bounds, four dents, open recess and low floor, interior-unit/floor and mast/head overlap, mast/casing placement, twelve underside-rib attachments, red panel/frame/wall contacts and 32 roof-fitting flange-root samples plus embedded face.

It verifies cylindrical/planar UVs, eight planar caps, twelve packed image source byte hashes, decoded colour/roughness pixel equality, material export quantization and reference/function index hashes. Contacts are scoped samples, not exhaustive engineering proof. Whole-object framing and three matched-camera native/imported render comparisons are technical checks. Macro crops are intentional. Blender native/imported GLB is the target runtime for this standalone milestone; client integration is unchanged.

## Deferred acceptance

The first render and source comparison are retained without an artistic-refinement cycle, following `programme.json.current_pass`. Proportions, finish, hidden engineering, operational/damage variants and game scale/orientation/placement remain for later passes. No final artistic review gate is promoted. Construction scaffolding remains deferred under #983.

Final first-version checks passed in Blender 4.5.15 for twenty-one mesh objects and nine materials. Eleven views passed render checks and all three matched-camera pairs have identical threshold-128 silhouettes and alpha. The interior macro intentionally fills the frame; transparent-background checks remain strict for whole-object views. Full inventory verification passed for 303 definitions / 1444 reference occurrences, and required changed-code quality verification passed against milestone base `29419b70`.
