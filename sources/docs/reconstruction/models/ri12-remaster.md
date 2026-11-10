# RI12 Deep Space Probes: canonical sensor tower

Tracking: openfa-assets #253 and per-building #45. Catalogue identity `openfa:building/legacy/051`, definition class 16, footprint 2x2, construction updates 36. Original functional record 912 describes research and observation sensors. Culture record 18 supports elegant ergonomic research architecture, without establishing hidden machinery.

## Reference and concept feedback

Actual correctly paletted surface body and catalogue phases 0/10/20/30/40 were inspected. They show a shallow circular jade pad, small brass fitting, stepped pedestal, long narrow mast, exposed copper neck, graphite/red side module, enlarged sensor head and relatively straight segmented tip. Reveal/highlight phases are not additional spatial views or a mechanical sequence. The pedestal's dark patch is ambiguous and remains a shadow hypothesis rather than an invented trench. Shared RIS2 construction is separate.

Two actual built-in ImageGen requests were used within the limit of three. Attempt 1 returned no image after output moderation; attempt 2 produced the published review concept. Exact prompts are `ri12-concept-prompt-1.txt` and `ri12-concept-prompt-2.txt`. The successful concept preserves the basic anatomy and jade/copper/red palette, but thickens the base and changes the small round brass fitting into an oblong plate. Those geometry changes are rejected. Original pixels remain private and are not used as textures.

## Preserve the good refinement

The latest existing revision 2 is retained rather than rebuilt from the bootstrap study: shallow stepped pad, corrected straight segmented tip, separate mapped copper spindle, cylindrical side UVs and twelve planar end surfaces. Six profile/spindle parts are protected with exact evaluated surface preservation. Five shallow geometric dents, authored painted wear, machining variation and collar oxidation remain. Fine detail is deliberately restrained instead of adding a dense panel grid. Hidden/rear anatomy and exact dimensions remain engineering interpretation.

Only the cast fitting bezel is reduced, from 2,714 to 1,574 triangles, with maximum sampled bidirectional vertex-to-surface deviation below 0.000041 source units. Total cost decreases from 45,650 to 44,510 triangles: 19 editable physical components, seven used materials and six embedded maps. This is a measured asset budget, not Android performance or batching acceptance.

## Actual runtime and single selection

Use `sources/objects/rigellian/deep-space-probes/model.blend` and `model.glb` across gameplay, build menu and SciTek. Previous studies remain historical and must not be packaged as additional current payloads. Root `PlacementRoot` is identity, local -Y forward and +Z dorsal; nominal ground is Z0. Bounds are [-0.9, -0.9, 0] to [0.9, 0.9, 4.04]. Nominal footprint is not a calibrated game placement. Static export has no animation clips.

Blender 4.5.15 reopened the saved native file and independently imported GLB. All 19 welded physical meshes are closed with positive volume. Entire prior anatomy/map contract remains: five measurable dents, copper overlap with mast/head, recessed red module contact, 32 curved-pad bezel root rays, fitting face contact, full decoded colour/roughness pixels and twelve planar end UVs. A connected sampled contact graph supplements local checks without claiming exhaustive intersections. Native/imported surface deviation is below 0.000000015 source units. Three matching view pairs were rendered and inspected; actual alpha and threshold silhouettes agree exactly. Numeric differences and framing margins are recorded in `visual-review.json`.

The imported model keeps the legacy anatomy and round fitting rather than adopting the concept's thicker base. Final user artistic approval, hidden details, damage presentation, game scale/state integration and frame rate remain separate. This milestone does not claim completion of mobile-ship programme #248.

## Reproduction and disk

Run `remaster_rigellian_static.py` and `verify_remastered_rigellian_static.py` through Blender with `--python-exit-code 1 -- --recipe sources/objects/rigellian/deep-space-probes/recipe.json`. Inspect renders before registration and gallery generation. Source-bound reports retain exact binary, recipe, helper and render hashes. Reuse the existing checkout; no build, archive or additional worktree is needed. Only verified task-owned temporary output may be removed.
