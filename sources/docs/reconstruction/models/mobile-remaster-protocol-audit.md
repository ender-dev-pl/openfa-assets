# Existing mobile remaster protocol audit

Programme #248 covers mobile ships. All seven fixed-scale orbital stations/spacedocks are excluded, including AR5C and MN5C. This audit reads immutable Git snapshots rather than assuming that a model missing from the Mauna branch does not exist elsewhere. The companion JSON records the exact snapshots, source and binary identities, existing report bindings and remaining actions for all16 Terran/Rigellian/Achaean mobiles.

This is a content/evidence audit. It does not execute Blender, rerender unchanged models, certify client integration or grant new artistic acceptance. Existing runtime reports are useful only to the extent their recorded bytes still match the audited sources and outputs. Missing protocol metadata is not evidence that model geometry must be replaced.

## Rigellian: retain the existing four remasters

[PR233](https://github.com/ender-dev-pl/openfa-assets/pull/233), snapshot `93582d421d1ddef0b6a0172832df05cd4d30ad8f`, contains all four canonical mobile models. Each native/GLB byte hash matches both its metadata and existing runtime report. Recorded rendered outputs are content-checked separately. The models have16,400 /25,728 /32,842 /52,390 triangles for Lazzaro, Delphini, Messier-Lukannon and Transportation respectively; no new copies are introduced here.

The four user-provided artistic references were manually generated in ImageGen before modelling. Their actual attachment bytes match the filenames/hashes already recorded in `fleet-style.json`. They count as existing concept inputs; lack of an automated generation record does not justify generating them again. Exact manual prompts were not supplied and must not be invented. Original paletted sprite source identities also match the common reference index.

The existing delivery review explicitly records removal of the rejected dense hull grid and preservation of broad formed skins. Proposed class sizes and uncalibrated mounts remain client integration concerns. Review and integrate the existing PR before considering additional art changes; this audit does not recertify those changes merely from counts or hashes.

## Achaean: retain the existing three remasters and truthful feedback history

The current Hunter/Prospector branch, snapshot `3722ae78246ba213d2327aa39c2ad338a35d7b9b`, includes the transporter/fighter dependency chain: [PR235](https://github.com/ender-dev-pl/openfa-assets/pull/235), [PR237](https://github.com/ender-dev-pl/openfa-assets/pull/237), [PR239](https://github.com/ender-dev-pl/openfa-assets/pull/239). All three actual native/GLB hashes match metadata and runtime reports. Selected concept images and recorded prompt files are checked from the same snapshot. A current prompt file does not prove the exact prompts of every historical iteration.

- Dedicated Ore Transporter has53,248 triangles. Its concept, successive actual GLB feedback and four user-directed glazed crew domes are recorded. The user's decision to retain the final wing proportions stands; do not reopen that refinement solely to fill a new checklist.
- Dedicated Fighter has35,000 triangles and three ImageGen attempts already used. The selected concept's small inset has unresolved proportions and is explicitly excluded from geometric authority. Retain this limitation; neither a green runtime report nor this audit accepts that inset, and a fourth generation is outside the protocol.
- Hunter/Prospector has25,806 triangles. Two earlier ImageGen concepts were rejected by the user. The current concept is the user's three-view sketch, with two upright aft-opening crescents and one central hull. Preserve the correction and the rejected history; do not relabel the sketch as a newly generated image.

Native/import geometry checks and recorded visual feedback exist, including the corrections to crescent openings, lateral spacing and the absent extra spar. Cross-branch inventory/gallery integration and final current-view assessment remain distinct from this byte-level audit.

## Terran: source-specific follow-up remains open

Nine mobile entries are present in the common reference index. The three small craft (Assault Fighter, Combat Eagle and Scoutship) have single canonical construction-layer payloads. Their construction visual reports explicitly decline a legacy-fidelity claim. Construction correctness must not be presented as the missing legacy/concept feedback stage, and any further work must preserve their five construction stages and accepted exteriors.

Destructor, Terminator, Transporter, Fleet Battleship, Command Cruiser and Spy Satellite still require source-specific inspection of existing artistic/reference evidence before declaring the programme's concept/render feedback requirement met. Several have historical/refined/SciTek sources but no explicit selected canonical payload in the audited inventory. This is a selection/evidence concern, not authorization to package every variant or to assume all current artwork needs replacement. The shared Federal Transporter quality benchmark is a separate asset and is not a substitute for the ordinary Terran transporter entry.

## Remaining programme work

This audit does not complete the combined audit-and-repair milestone in #248. Keep that checkbox open until the remaining source-specific protocol work and canonical cross-branch integration are verified. At the audit snapshot, Mauna MN2C/MN3C/MN4C were also open; current coverage is tracked separately in `mauna-mobile-remaster.json`. Two MN2C requests and one MN3C request returned ImageGen output moderation errors without an inspectable image; no concept completion or corresponding new model is claimed for them. Exact failed-request history remains private and is summarized technically in the issue.

No model, reference raster, material or completed spacedock changed during this audit. No new checkout, build or archive was created. Only small evidence documents were added.

## Later verified follow-ups

The snapshots and findings above are historical. Current Terran canonical selection is recorded separately in `terran-canonical-selection.md`; its latest SciTek models are user-selected and must not be replaced automatically. The earlier moderation/missing-model notes for Mauna are superseded by completed five-model `mauna-mobile-remaster.json`, including MN2C/MN3C detailed milestones.

Destructor now has one actual retrospective ImageGen request and fresh saved-native/independent GLB render feedback in [destructor-protocol-review.md](destructor-protocol-review.md). Existing model bytes remain unchanged and visual differences remain explicit. This advances one Terran protocol entry; it does not complete the remaining eight Terran entries, cross-branch reconciliation, client integration or programme #248.

Terminator now also has one actual retrospective ImageGen request and fresh evaluated native/imported renders in [terminator-protocol-review.md](terminator-protocol-review.md). Its latest SciTek canonical binary is unchanged. Seven other Terran protocol entries remain open; this does not complete programme #248.

Fleet Battleship now has one actual retrospective ImageGen request and fresh evaluated native/imported renders in [fleet-battleship-protocol-review.md](fleet-battleship-protocol-review.md). The canonical SciTek source is preserved with explicit remaining appearance differences; six other Terran protocol entries remain open.

Command Cruiser now has two actual ImageGen iterations with original wireframe feedback and fresh evaluated native/imported renders in [command-cruiser-protocol-review.md](command-cruiser-protocol-review.md). Rejected iteration 1 and selected iteration 2 remain distinct. Five other Terran protocol entries remain open; no final fidelity/client acceptance is inferred.
