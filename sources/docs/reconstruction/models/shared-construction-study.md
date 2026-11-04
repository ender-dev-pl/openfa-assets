# Shared construction-state reference inventory (#983)

## Scope and source contract

All 177 building definitions now map to an explicit shared culture/footprint construction family in the 303-definition reconstruction inventory. This adds 177 archive reference occurrences, bringing the verified inventory to 1444 occurrences. Shared families are additional required model work, not 28 new building definitions or completed replacement models.

The current loader in `GameplayAssets.LoadLegacyConstructionSprites` derives footprint class as clamp(max(width,height),1,4), maps culture to PB/RI/BR/MK/AR/MN/AC, and loads `<prefix>S<class>.256` from `_B`. These findings establish current OpenFA mapping. Original assembly selection and progress timing have not been traced afresh in the decompile and must not be inferred solely from this loader.

`LegacyConstructionSpriteFrameSelector` excludes descriptor zero and maps clamped progress across descriptors 1..last using rounded interpolation. This is current runtime behavior, not proof that every source descriptor zero is a shadow.

## Decoded coverage

| Culture | Families | Descriptor counts for sizes 1/2/3/4 | Buildings using sizes 1/2/3/4 |
| --- | --- | --- | --- |
| Terran | PBS1..4 | 17 / 9 / 5 / 3 | 2 / 28 / 8 / 2 |
| Rigellian | RIS1..4 | 3 / 3 / 3 / 3 | 0 / 12 / 9 / 2 |
| Braccatian | BRS1..4 | 3 / 3 / 3 / 3 | 0 / 13 / 10 / 0 |
| Mikotaj | MKS1..4 | 3 / 3 / 3 / 3 | 0 / 13 / 8 / 0 |
| Artemian | ARS1..4 | 3 / 3 / 3 / 3 | 0 / 12 / 10 / 1 |
| Mauna | MNS1..4 | 3 / 3 / 3 / 3 | 0 / 11 / 8 / 2 |
| Achaean | ACS1..4 | 3 / 3 / 3 / 3 | 0 / 17 / 9 / 0 |

All 28 installed sheets contain 106 descriptors. Nineteen families are used by the current definitions; nine installed families have no current building dependency and remain explicitly listed. The index preserves original payload hashes, correctly decoded palette hashes, descriptor sizes, offsets, indexed-pixel hashes, reference PNG hashes and family contact-sheet hashes. Original pixels stay under ignored `artifacts/shared-construction-reference-study/`; no model uses them as geometry or textures.

The overview contact sheet was visually inspected across all cultures. Detailed sheets were inspected for RIS2 and ARS2. This is not a per-state visual acceptance of all families.

## RI11 dependency and observed structures

RI11 Probe Launch is a 2x2 Rigellian building and maps to RIS2, shared with eleven other definitions. RIS2 has a purple perimeter-like descriptor zero plus two body images showing green structural posts with copper/brass framing around an open construction site. The second body is taller/more developed than the first. These are not launch-door phases and not two cameras of the completed Probe Launch. Reconstructing the shared site once should serve all twelve current dependencies, subject to footprint/origin calibration.

## ARS2 discrepancy

ARS2 descriptor zero visibly contains a green domed, perforated construction body, unlike the purple perimeter-mask appearance seen in the other reviewed sheets. All three ARS2 descriptors show body-like structures. Current selection excludes zero; that does not prove the original did. Preserve every descriptor and investigate original frame selection, palette/composition and construction progression before changing runtime or dropping this state. This discrepancy is an evidence question, not a confirmed client bug.

## Boundaries and next work

No independent 3D construction model is accepted by this milestone. Editable shared models, required pose exports, relative origin/footprint calibration, original progress semantics and per-state native/imported render comparisons remain outstanding. RI11 itself has only descriptors 0 and 1 in its completed surface sheet; its 41 catalogue phases are reveal/highlight presentation, not evidence of additional launch doors. Damage variants remain a separate source question: absence from that two-descriptor sheet does not establish absence of shared damage effects elsewhere.

The inventory generator links each building's family and actual source entry. Its verifier recomputes all original decodes, compares reference pixels and hashes, checks all 177 mappings and verifies the added archive references. Existing model acceptance gates are unchanged. This is an analytical/reference milestone; no application or model runtime changed.

Reproduce with `../legacy/system/python/python.exe tools/blender/prepare_shared_construction_references.py`, then `--check`, followed by `inventory_reconstruction.py` and `verify_reconstruction_inventory.py` from the same tools directory. The reference-only overview is `artifacts/shared-construction-reference-study/overview.png`.

## Scaffold stacking correction and analysis

The `{race}S{size}` families are construction scaffolding, not representations of the partially built final structure. User clarification prompted review of the actual decompile: 0x449F0 carries erection stages into additional vertically offset scaffold descriptors. See [scaffold-stacking-analysis.md](scaffold-stacking-analysis.md) and its source-bound JSON for the recovered carry/offset arithmetic, current runtime gap and modular 3D recommendation. The current progress-to-single-frame selector must not be treated as the full legacy mechanism. Each family's index now explicitly records `object_kind: construction-scaffolding`.

## RIS2 modular prototype

An unaccepted editable RIS2 study now exercises stages `[1]`, `[2]`, `[2,1]` and `[2,2,2]` with hollow uprights, interior lattice and tier sockets. See [rigellian-scaffold-study.md](rigellian-scaffold-study.md). Prototype availability is registered in programme.json and linked to all twelve RIS2 dependencies in the generated inventory. It does not accept family geometry or calibrate game-world pitch.
