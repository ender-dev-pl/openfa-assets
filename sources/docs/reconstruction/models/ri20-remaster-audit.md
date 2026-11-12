# RI20 Extractor canonical remaster verification

Tracking: openfa-assets #253/#53 and PR #254. ID `openfa:building/legacy/059`, class 8, footprint 2x2, construction updates 42. Current editable Blend and GLB are in `sources/objects/rigellian/extractor/`. The latest structural refinement is preserved rather than reverting to the older smooth capsule/flat-inlay study. Previous studies remain history; one current selection serves gameplay, build menu and SciTek.

## Original evidence and concept

Original ENGLISH.TXT record 920 identifies the Extractor as one mining device handling all ores. Actual CDB Architecture record 18 describes elegant ergonomic Rigellian architecture, including mining facilities. This context does not establish hidden mechanisms or material identity. Correctly paletted surface/shadow and catalogue phases 0/10/20/30/40 plus the coloured/outlined close-up were inspected. They show the broad lower shoulder, round upper housing, attached side pod, lower rib tiers, green lower feature, two long narrow front slots and round fittings. Catalogue reveal/highlight is presentation, not operating motion.

Current game `LegacyBuildingSpriteFrameSelector` and current gameplay rules exclude ID059 from the directional-body allowlist. Body/shadow descriptors do not establish an activity cycle. Shared construction family is RIS2. No external drill, plumbing network, firing effect or moving assembly is inferred from ambiguous colour patches.

One actual built-in ImageGen request used the paletted surface and a crop of the real catalogue colour view. The exact prompt is `ri20-concept-prompt-1.txt`; selected concept is `gallery/media/concepts/rigellian/ri20-review-1.png`. It agrees broadly with the stepped silhouette, side pod, slots and lower tiers. Its rounded slot ends, enlarged upper fitting, rearranged green blocks and stronger natural patina are interpreted details; those changes are not transferred automatically. The existing authored bronze/green finish is retained as a more graphic, subtler interpretation of the source marks.

## Saved-native and independent GLB checks

All 39 evaluated source components are protected; no tessellation reduction or geometric redesign is claimed. The current asset has 13,774 triangles, five materials and four embedded images. Retained structural checks cover shoulder proportion, three readable lower ribs, two actual recessed slot cavities/backings, the silhouette-changing side pod, green blocks, front fittings and exposed drum contacts. Two measured casing dents remain. All physical parts are closed and positive-volume after coincident UV seam vertices are welded for topology analysis.

A sampled vertex/face-centre contact graph connects all 39 components with no isolated part. This diagnostic and local structural rays are not exhaustive solid-intersection proof. No operating animation is invented.

All used colour/roughness maps are decoded and compared from the historical source, saved native file and independent GLB. Shader-bound UV coordinates are matched bidirectionally by material and world position, including split seams: 40,620 directed corner matches for each comparison. Source/native UV error is zero; native/imported UV error is below 0.000000030. Export geometry error is below 0.000000120 and all protected source surfaces are unchanged within 0.000001. Three paired whole-object renders were inspected; their near-identical pixels verify export equivalence rather than a percentage of legacy likeness.

The original 17-part first-version verifier describes older geometry and cannot certify the latest 39-part refinement unchanged. The remaster instead retains the later source-specific shoulder/rib/cavity checks, adds full source/map/UV preservation, dent samples and the contact graph. It does not bypass the old semantics by substituting a simpler model. Current source-bound JSON files identify all helpers and actual renders.

## Integration and limits

PlacementRoot remains identity; Blender -Y forward and +Z dorsal. Nominal footprint is 2x2. The lowest physical surface remains at source Z0.02, so client ground alignment must use the reported bounds rather than assuming a surface at root Z0. No automatic root shift is hidden in this remaster. Bind bounds and exact hashes are in model/runtime metadata and the delivery manifest.

Use the one canonical current model across gameplay, building catalogue, information and SciTek; technical views derive from the same geometry. Both Markdown and interactive galleries include the concept and actual independent GLB preview. Client scale/orientation/ground calibration, construction/damage/state integration, Android cost and final user artistic acceptance remain separate. No frame-rate, draw-batch consolidation or continuous mechanism proof is claimed.

Reproduce with `remaster_rigellian_static.py -- --recipe sources/objects/rigellian/extractor/recipe.json`, `verify_remastered_rigellian_extractor.py` using that recipe, and `tools/review_rigellian_extractor_pixels.py` with private reference/contact-sheet paths. Original pixels remain private. Existing checkout reused, no extra build/worktree/archive. Former mobile-ship programme #248 remains unfinished.
