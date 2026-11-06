# Older alien building quantitative export comparisons (#1105)

This extends the earlier 114-model source-specific runtime check with actual per-object geometry/material comparisons. Existing last-present silhouette sources are selected from the current inventory: Braccatian 23, Mikotaj 21, Artemian 23, Mauna 21 and Achaean 26. Later replacements/refinements are preserved and excluded. No source asset was rebuilt or altered.

`audit_older_alien_building_exports.py` ran in Blender 4.5.15, reopening each native source at frame 1 and independently importing its existing GLB at corresponding start frame 0. All 114 models / 2431 mesh object identities match, as do named material identities and parameter values (maximum material error zero). Maximum bidirectional nearest evaluated world-position error is 2.45757e-7 model units; maximum per-object bounds error is 1.34111e-7. Imported seam duplication is not treated as a geometry change. Source Blend/GLB/metadata hashes remained unchanged. Process completed with all 114 success markers and exit zero.

One first-selected model per culture received actual native/import front/rear quarter renders (twenty new images). `review_older_alien_building_exports.py` verifies image hashes/framing, measures pixel differences and produces the combined comparison sheet, which was inspected. All ten matched pairs have identical alpha and threshold-128 silhouettes. Maximum foreground mean RGB differences across each example's two views are:

| Example | Maximum mean RGB channel difference |
| --- | ---: |
| Braccatian BR01 | 0.0015/255 |
| Mikotaj MK01 | 0.0015/255 |
| Artemian AR01 | 2.2451/255 |
| Mauna MN01 | 0.0101/255 |
| Achaean AC01 | 0.1920/255 |

The larger AR01 shading discrepancy remains unresolved. Prior light-ship normal experiments do not prove its cause. Five example renders do not establish pixel parity for the other 109 models or final legacy fidelity.

Reports and actual images are under `docs/assets/reconstruction/evidence/older-alien-building-comparisons/`. `summarize_older_alien_exports.py --check` binds the current inventory selection, all source/report hashes and selected pixel reports. This checker does not execute Blender itself. Evidence is exact-byte scoped to this checkout, not portable normalized-text ledger acceptance.

No final quality, exhaustive topology/UV/corner-normal, state/animation/variant, calibrated attachment or game-client integration gate is accepted here. No ledger gates changed. Refining and scaffolding remain deferred. Required changed-code quality base: `40407159`.
