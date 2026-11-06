# RI18 Missile Launcher — first authored iteration (#990)

Catalogue ID `openfa:building/legacy/057`, global type 57, nominal 3x3 footprint. Current pass is first iterations only; artistic refining and exact operating-state reconstruction are deferred. Existing reconstructions/refined assets are preserved.

## Function and source states

Original ENGLISH.TXT record 918 at byte offset 0x11774 identifies missile silos. Correctly paletted surface body (34x41), catalogue frames and all base-plus-overlay combinations 2..17 were inspected before modelling. Visible features include a bronze lower drum, stepped tapering green casing, open neck, angled bronze attachment and presentations progressing from a closed cap toward an open aperture. Catalogue reveal phases are not rotations. Exact leaf construction, motion and the semantics of the final body/ground overlay remain unresolved.

The first version uses one independently editable nominal closed cap. This is not a claim that the original has a one-piece lid. Hidden profiles, bore depth, low floor, rib/band construction and attachment interfaces are authored interpretations. The angled bronze part is not assigned an unsupported weapon or antenna behaviour. No original pixels enter mesh or texture authoring.

## Deliverables

Editable Blend, standalone GLB, eight independent source maps, metadata, technical/render reports and eleven actual 900x900 views are under `docs/assets/reconstruction/buildings/rigellian/missile-launcher/`. Three measured geometric dents and analytic bronze/green colour/roughness maps add restrained joint contamination, handling marks, grain and scratches. Original comparisons remain in ignored `artifacts/rigellian-building-reference-study/RI18/`, outside distributable assets.

## Technical verification

The verifier reopens native Blender and independently imports GLB. It checks positive closed topology, identity placement root/3x3 bounds, individual transforms/bounds, three geometric dents, clear bore through both annular casings at five aperture points, a low floor at Z=0.05 and nominal closed-cap coverage of the same points. Bore geometry is ray-inspected independently of the separate cap; it is not filled with a grille or shallow plug.

Checks also cover floor/base and casing/cap overlap, twelve drum-rib attachments, two front bands and casing/sleeve/angled-attachment contacts. UVs, six planar caps, eight packed source-image byte hashes, decoded colour/roughness pixels, material export quantization and reference/function index hashes are verified. Contacts are scoped samples, not exhaustive mechanical proof.

Whole-object framing and three matched-camera native/imported pairs are technical checks; intentional macro crops may fill the frame. Blender native/imported GLB is the target runtime for this standalone milestone. Client integration is unchanged.

## Later passes

The first generated geometry is retained without an artistic-refinement cycle. Exact cap leaf geometry, all operating overlays/animation, proportions/finish, construction/damage variants and game orientation/scale/placement remain unresolved. No final artistic acceptance gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for twenty mesh objects and eight materials. Eleven views passed render checks; all three matched-camera pairs have identical threshold-128 silhouettes and alpha. Full inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `73087301`.
