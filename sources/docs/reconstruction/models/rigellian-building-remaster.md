# Rigellian building remaster: preservation baseline

Tracking: openfa-assets #253; prior reference programme #31 and refining programme #185. This file preserves the initial inspection milestone. Current completed asset delivery is recorded in [the completion audit](rigellian-building-remaster-completion.md); game integration remains separate.

## Existing models to preserve

| Definition | Candidate | Native meshes | Triangles | GLB materials | Embedded images |
| --- | --- | ---: | ---: | ---: | ---: |
| RI01 / 040, Central Unit | rigellian-refined/ri01 | 75 | 40,636 | 7 | 2 |
| RI02 / 041, Filtration Plant | buildings/rigellian/filtration-plant | 83 | 65,890 | 8 | 2 |
| RI03 / 042, Nourishment Bank | rigellian-refined/ri03 | 43 | 79,668 | 7 | 4 |

All paths above are relative to `sources/docs/assets/reconstruction/`. See [the complete inspection](rigellian-building-remaster-baseline.json) for exact source/export hashes, per-mesh world bounds, roots, images and action inspection.

A fresh Blender 4.5.15 session opened each saved native candidate, then cleared the scene and independently imported its GLB. Matching mesh names and frame-1 world bounds agree within 4.77e-7 scene units. Source and export hashes remained unchanged. No GLB clips are present in these five inspected candidate/predecessor pairs. This does not establish material appearance, UV parity, exhaustive states, geometry fidelity, calibrated dimensions, frame rate or visual acceptance.

At the baseline inspection, RI01 and RI03 inventory evidence bound earlier sources instead of their later refinements. The inspection includes those predecessors to expose the difference. It does not silently replace the inventory selection or rebind an acceptance claim. RI02 already points to its current filtration study.

## Reference interpretation

Correctly paletted surface previews and catalogue phase sheets for RI01 and RI02 were inspected privately. The catalogue sequence includes reveal and red highlighting of a fixed view; these are not additional camera headings. RI01's broad saucer, waisted base, grille and three-prong crown should be preserved. RI02's rounded body, capped upper tower, gold front ports and lower slots should be preserved. Existing gallery views are historical renders, not fresh pixel comparisons from this inspection. RI01 predates the wear requirement; this audit does not authorize an automatic wear retrofit.

Original English functional records 901-903 describe essential colony supplies, clean-water filtration including excess oxygen, and species-appropriate nutritional substances respectively. Culture evidence describes ergonomic, elegant architecture even for industrial use. These guide interpretation without establishing hidden mechanical designs. Private original pixels and original text are not redistributed here.

The current game's `LegacyBuildingSpriteFrameSelector.cs` hash is `9f2f4401d8576909af9382176b7cdec0ca024b129e355953cd4fdfd4bb4745a8`, matching the historical audit. Its current `legacy-gameplay.json` hash is `dc79ec4e0b5bd7fb1231e0e622c40bcbfc167b0a6c1579e568350e738fd3481f`, different from the historical audit. Current directional definitions include 058, 061 and 062. Do not treat all eighteen descriptors as headings or claim the old gameplay snapshot verifies today's state selection. Activity rules still name specific Terran definitions; per-object integration requires investigation.

Original functional source SHA-256: `559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449`. Culture source SHA-256: `767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4`. These original files were checked locally, not copied into this repository.

## Delivery gates at the baseline inspection

Preserve the good RI01/RI02 geometry; assess concept history and missing current protocol evidence before authoring. Continue RI03 onward from existing studies. Each ready building needs actual native/import renders against legacy and its concept, material/batch evaluation without silhouette degradation, explicit canonical selection, spatial and state contracts, gallery updates, source-bound checks, a signed milestone and a game-thread handoff. Triangle or material counts alone are not an Android performance certification. Keep historical studies out of package selection rather than duplicating gameplay/menu payloads.

The inspector is read-only and deliberately makes no new acceptance entries. Re-run from the asset root with Blender background mode, Python exit code 1, script `sources/tools/blender/inspect_rigellian_building_baseline.py` and arguments `-- --output sources/docs/reconstruction/models/rigellian-building-remaster-baseline.json`. It requires the current inventory's latest present studies and their ledger predecessors.
