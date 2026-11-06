# Asset integration review — 2026-11-06

Reviewed inputs: trading goods `c08f963c`, Sci-Tek plus Federal Transporter and PS7C `cc38a8df`, target main `bfaf0d44`.
Relates to #208, #214, #215, #216 and the existing menu-label dependency #206.

The integration preserves both input histories. It combines 304 physical definitions and 101 trading definitions, with 180 supplemental UI/scaffold records: 585 interactive catalogue entries. The 471 physical studies and 202 trading studies remain available. Generated gallery conflicts were resolved by rebuilding from the merged inventories. Layout entries were joined by destination, rejecting differing definitions of the same destination. The project validator now checks trading rows against their source-bound provider separately, preserving physical model, animation and category/culture checks.

## Fresh verification

- All 36 Sci-Tek native solids reopened in Blender 4.5.15 and independently imported from GLB; three pose samples each and portable colour checks passed. See scitek-native-import.json.
- All 36 research deliveries, six collages, one logo and 72 full movies passed file/provenance/format/complete-decode checks. All 36 actual legacy tiles and 72 original video source hashes matched. See scitek-delivery.json and scitek-legacy.json.
- Trading catalogue, 101 refined source/image hashes, all 101 first-pass PNGs and lore evidence passed their dedicated validators. Fourteen representative current native/GLB pairs were independently reopened/imported again, including all seven lore corrections, repaired shapes and missile reuse. Reports are in trading-runtime/.
- PS7C finished and construction native/GLB checks were rerun in a separate isolated worktree: 950/969 closed parts, zero geometric drift, maximum matrix error 5.96e-8. Render silhouette IoU is 1.0 for both variants; mean foreground RGB differences are 1.912/255 and 0.088/255. The 144-frame construction movie fully decodes and contains 141 distinct poses.
- Fresh PS7C imported render and representative refined trading renders were visually inspected. The actual in-app browser showed 101 trading cards and correctly filtered TI064 with both iterations rendered. The optional Python Playwright runner was unavailable locally; it is not reported as passed.
- Shared project/layout validation passes (13,953 layout files; 1,520 Python sources). Node gallery checks pass all 72 race/type combinations and 79 animated studies, including search/reset/deep links and hidden-video pause.
- The game checkout quality gate `tools/Verify-ChangedCodeQuality.ps1 -BaseSha HEAD` passes: 1,161 production C# files, no changed C# files. This asset-only review does not modify or launch the game client.

## Acceptance limits

This is source-asset merge readiness, not new package/client integration acceptance. Existing Sci-Tek delivery approximations remain explicit in sources/docs/reconstruction/scitek/DELIVERY.md. The pending Screen Generator surrounding glow/bloom refinement is a separate renderer follow-up, not claimed delivered here. Trading has 28 partial and two ambiguous artistic/lore assessments; these are preserved iteration targets, not hidden failures. Its 202 legacy-size compact/detail UI outputs remain deferred, and GLBs retain scalar fallbacks rather than full native procedural material bakes.

The Federal Transporter and legacy menu labels are included from the Sci-Tek branch ancestry. No cinematic/alien-character branch is merged or changed. No worktree, recordings or other artifacts are deleted.

## Publication repair

The initial combined scan found 1,536 publication failures: 1,451 PNG metadata payloads, 84 native files with absolute path strings and one logo generator with an absolute system font path. tools/prepare_scitek_publication.py removes image metadata with exact decoded-RGBA equality, and uses the existing tested fixed-width Blend path sanitizer, which verifies every byte outside the path strings remains identical. The logo generator resolves the same font through WINDIR. GLBs, geometry, animation, shader data and packed resources are not rebuilt.

publication-normalization.json retains original and normalized binary hashes and the transitive metadata hash-rebinding ledger. Historical subject reports were not rerun and their rebinding is explicitly justified by this equivalence certificate, not portrayed as fresh execution. The separate 36-subject Blender/GLB audit and complete film/delivery audit were rerun after normalization. normalized-native-runtime.json additionally records fresh reopening and dependency checks for all 84 normalized Blend files; no missing image/font/library dependencies remain. Public Pages generation and its nine publication regression tests pass. The final full publication guard passes: 20,553 inspected files, zero failures.
