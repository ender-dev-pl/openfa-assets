# Complete model reconstruction inventory

Programme #946; inventory #947. Workstreams: buildings #948, ships/vehicles #949, hardpoints #950, missiles #951.
Rebuild with `python tools/blender/inventory_reconstruction.py --legacy-root ../legacy`; validate with `python tools/blender/verify_reconstruction_inventory.py`.

This is an evidence and work ledger, not a claim of finished art. All final acceptance gates remain open.

| Category | Definitions | Available authored studies | UI profiles |
| --- | ---: | ---: | ---: |
| buildings | 177 | 177 | 177 |
| ships | 41 | 41 | 9 |
| hardpoints | 16 | 16 | 16 |
| missiles | 69 | 69 | 11 |

## Culture coverage

| Culture | Buildings | Ships/vehicles | Missiles |
| --- | ---: | ---: | ---: |
| terran | 40 | 10 | 13 |
| rigellian | 23 | 5 | 7 |
| braccatian | 23 | 5 | 10 |
| mikotaj | 21 | 5 | 9 |
| artemian | 23 | 6 | 12 |
| mauna | 21 | 6 | 10 |
| achaean | 26 | 4 | 8 |

The 16 hardpoint definitions are global. Culture-specific geometry is unresolved; 16 is not a proven number of final hardpoint meshes.

## Confirmed gaps and constraints

- Every ship and missile has a runtime mapping, even when the separate UI presentation domain lacks a profile.
- Ship candidates preserve runtime fallback order. Archive presence and payload hashes come from the actual installed archives, not filename guesses.
- External-palette sprite references are flagged. A grayscale export is not an accepted colour reference.
- 145 ship equipment slots are declared, with only 29 explicit catalogue mount coordinates. Those coordinates are 2D designer positions, not 3D socket transforms.
- Existing building/transporter files are registered as studies. Final silhouette, construction detail, materials, mechanisms and attachment acceptance are not inferred from their existence.
- Catalogue definitions do not establish the number of unique meshes. Shared bodies, cultural variants, launch states, construction stages and visual effects need explicit investigation.

## Evidence required for acceptance

For each record, first read the original functional description and establish what the object does; use that evidence to distinguish shafts, walls, platforms and mechanisms before interpreting pixel features. Retain multiple correctly paletted reference views and an observed/inferred feature sheet; review actual renders; record refinement decisions; verify editable/native and imported GLB geometry, materials, pivots, attachments and animation; link technical checks and final visual acceptance to a commit.
Only then may the corresponding gates change. Technical exports and polygon counts alone do not establish visual acceptance.

## Functional source evidence

[shared-construction-references.json](shared-construction-references.json) indexes 28 culture/footprint families and maps all 177 buildings to shared construction sprites; decoded references do not accept replacement state models.

[functional-text-index.json](functional-text-index.json) links original ENGLISH.TXT records to all 303 definitions. Read mapped descriptions before modelling; source-function review and located text do not accept geometry. See [functional-source-review.md](functional-source-review.md) for coverage, unresolved text banks and the reference-only reading aid.

[cultural-architecture.md](cultural-architecture.md) and [cultural-architecture-index.json](cultural-architecture-index.json) summarize six original ENGLISH.CDB Architecture sections with source offsets and hashes. Consult them for new ambiguous details, distinguishing direct building evidence from contextual ship interpretation; do not retrofit older models or resume refining.

## Persistent review state

`programme.json` routes categories to linked issues and registers additional authored studies. Add a category/id/stage/blend entry to `additional_studies` when introducing a new model.
`review-ledger.json` is authored review evidence, separate from the generated inventory. A review contains category/id, a model {blend, sha256}, gates {gate: boolean}, and evidence {gate: [commit/reference/render/check citations]}. Regeneration preserves this ledger. Accepted gates require the exact registered model hash and nonempty evidence; modifying a reviewed model invalidates verification until it is re-reviewed.
The native_and_glb_runtime gate is a scoped Blender native/imported-GLB check. Its model.runtime_evidence binds the export, metadata, reports, scripts and rendered pixels; JSON/Python text uses LF-normalized hashes, while binary files use exact byte hashes. verify_reconstruction_inventory.py rejects missing, changed or mismatched evidence. This gate does not accept artistic quality, animation/state completeness, calibrated attachments or game-client integration.
No existing model has been marked finally accepted by this inventory milestone.
