# RI21 Storage Racks canonical remaster verification

Tracking: openfa-assets #253/#54 and PR #254. ID `openfa:building/legacy/060`, class 30, footprint 3x3, construction updates 48. One current editable Blend/GLB in `sources/objects/rigellian/storage-racks/` serves gameplay, build menu and SciTek. Prior studies remain history. This pass preserves the good existing source geometry and maps rather than replacing it with extra concept details or reverting to the bootstrap study.

## Evidence and concept feedback

Actual ENGLISH.TXT record 921 identifies ore storage. CDB Architecture record 18 provides ergonomic/elegant mining-design context, not a recovered rack mechanism. Correctly paletted surface/shadow and catalogue phases 0/10/20/30/40 plus the colour/outlined close-up were inspected. Visible evidence is a two-tier bronze cluster, five green oval details and two grey front guides. Six total housings and hidden triangular cradles/rear spines are authored interpretations. No lower-central green face is asserted.

The current game selector and gameplay rules exclude ID060 from directional bodies. Catalogue reveal/highlighting does not establish loading animation; the common construction family is RIS3. Green colour alone does not establish glass, emission or a screen.

One real built-in ImageGen request used the actual paletted body and catalogue colour crop. Exact prompt is `ri21-concept-prompt-1.txt`; concept is `gallery/media/concepts/rigellian/ri21-review-1.png`. It preserves the two tiers, five visible ovals and front guides, but adds top handles, side collars, denser casing seams, massive supports and stronger wear. These unsupported details are rejected as automatic model changes. Existing source-derived proportions, tested cradle interfaces and subtler finish are retained.

## Actual source, native and independent GLB checks

All 32 evaluated source components are protected; source/native geometry error is zero. No reduction is claimed: 68,756 triangles, five materials and four embedded images. Per-component identities remain editable for technical diagrams; mesh/material counts do not imply draw-batch consolidation or Android frame-rate acceptance.

Actual saved-native and independently imported GLB checks cover closed positive-volume topology after coincident UV seam vertices are welded for analysis, identity placement and source-specific rack anatomy. They retain six measured dents; housing/cradle attachment samples at both ends of tier edges; rear spine/tie and tie/housing containment; front guide/foot-tie connections; 160 oval-bezel flange-root samples and 25 oval-face/rim samples. One sampled contact graph connects all 32 components without isolated parts. These checks are scoped contact diagnostics, not exhaustive solid-intersection or engineering proof.

Full decoded bronze colour/roughness pixels are retained, as are six cylindrical housing mappings and twelve planar end caps. Every used texture-material UV corner is matched bidirectionally by material, world position and UV, including seams: source/native 193,536 directed matches, native/imported 244,152. The count increases after export triangulation; equal counts are not an acceptance requirement. Source/native UV error is zero, export UV error below 0.000000030. Geometry export error is below 0.000000134. Opaque rough green faces have zero transmission and emission, alpha one, and remain exactly five visible authored face meshes.

Three paired actual whole-object renders were inspected against source views, legacy and the concept. Export pixel equivalence is separate from a numerical legacy-fidelity percentage. No loading, opening or rotation clip was invented. Same canonical geometry supplies main and technical views, avoiding an independently remodelled diagram assembly.

## Integration limits

PlacementRoot is identity; Blender -Y forward and +Z dorsal. Ground is at Z0, nominal footprint 3x3, top near Z1.81. Exact bind bounds, binary/helper hashes, maps and render comparisons are in model/runtime/visual metadata and the delivery manifest. Both interactive and Markdown galleries show the current model, concept and actual independent GLB preview.

Client scale/orientation/placement, shared construction integration, operational/damage variants if later supported, Android cost and final user artistic acceptance remain separate. The 68,756-triangle/32-mesh budget is recorded explicitly rather than inferred to meet a frame-rate target. Existing wear and simple casing surfaces are preserved; no dense panel divisions, invented glass or lighting.

Reproduce with the shared static author using `sources/objects/rigellian/storage-racks/recipe.json`, the case-specific `verify_remastered_rigellian_storage.py`, and `tools/review_rigellian_storage_pixels.py` with private reference/contact-sheet paths. The verifier reuses the already verified generic UV-corner matcher without modifying its bound source. Original pixels remain private. Existing checkout reused; no new worktree/build/archive. Former mobile-ship programme #248 remains unfinished.
