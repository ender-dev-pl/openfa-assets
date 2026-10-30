# Selected older alien building runtime evidence (#1105)

The current inventory selects 114 older `silhouette-study` sources outside Terran/Rigellian: Braccatian 23, Mikotaj 21, Artemian 23, Mauna 21 and Achaean 26. These 2431 mesh objects remain existing first studies, not accepted high-detail final art. Selection comes from the last present study per definition, preserving all later refined replacements. Relates to #1099, #948 and #946.

## Actual Blender checks

`verify_older_alien_building_runtime.py` derives the selected IDs from the inventory, binds native/export/metadata hashes, and invokes the existing `verify_full_catalogue.py` for exactly those IDs. Blender 4.5.15 LTS completed all 114 native reopen/independent GLB import checks with the full marker set, final success marker and exit zero.

The inherited catalogue checks cover generator/recipe provenance, catalogue identity and footprint, native object/recipe component presence, expected mesh count, scene settings/asset collection, materialled nonempty geometry, absence of external image dependencies, native bounds and camera-fit projection checks, and imported mesh count/dependencies. These do not establish actual native/import material parameter equality, pixel parity or exhaustive topology/UV validity.

Fifteen selected metadata records have existing rotation rigs. The wrapper also invokes `verify_directional_catalogue.py` for exactly those IDs. All fifteen pass native hierarchy/pivot/moving-static membership and sampled rotation checks, independent animation import, stationary base, nonzero head motion and return to starting geometry. This is sampled technical motion evidence, not validation of a recovered gameplay mount, exhaustive operating states or exact legacy timing.

All source Blend/GLB/metadata bytes were checked unchanged after both verifiers returned. `docs/assets/reconstruction/evidence/older-alien-building-runtime/source-specific-review.json` records current identities, hashes, counts and directional membership. The complete recorded Blender output is retained beside it. `check_older_alien_building_evidence.py` checks current inventory selection, exact files/scripts and per-ID catalogue/rig success markers; it does not execute Blender itself. The report is exact-byte evidence for this checkout, not normalized portable runtime-ledger proof.

## Limits and preserved scope

No model, material, texture or export was rebuilt/refined and no wear was retrofitted. No new rendered views were produced in this milestone; camera-fit mathematical checks do not constitute visual review or render parity. No accepted ledger gate was promoted. Legacy image fidelity, high-detail final quality, exhaustive topology/UV/normals, required state/variant completeness, calibrated attachments and game-client integration remain open.

Refining and construction scaffolding remain deferred. This milestone supplies missing technical evidence for current sources without mistaking broad catalogue presence for final reconstruction acceptance. Required changed-code quality base: `7b7be0cc`.
