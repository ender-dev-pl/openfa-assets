# Catalogue state and variant evidence (#1113)

This analytical inventory maps existing selected sources to declared authored mechanisms, actual #1112 hierarchy/animation evidence, current runtime selectors and registered state exports. It does not create states, regenerate models, refine art or resume scaffolding. All 303 selected Blend/GLB hashes and the source-bound hierarchy reports are checked.

## Existing motion classes

| Evidence class | Models |
| --- | ---: |
| Authored heading preview clip | 21 |
| Authored iris cycle | 1 |
| Source-evidenced authored mechanism cycle | 1 |
| Manual unkeyed yaw assembly | 3 |
| No keyed node clip established | 277 |

The three manual yaw assemblies are Rigellian Thermal Lance, Ex-Fang and Ultrathermal Lance. Their declared pivot and moving-mesh ancestry exist in the inspected hierarchy. Absence of a clip therefore does not mean absence of an articulated assembly. Conversely, a heading preview clip is not evidence of an operating cycle. For example, an inventory video labelled rotation-video must not be treated as proof of mechanically moving components or exact timing.

The two mechanism clips are the Terran Missile Silo iris and Rigellian Ground Deck cover cycle. Their existence does not accept hidden engineering, operating timing or all gameplay states.

## Runtime selectors and historical authoring rules

The current gameplay catalogue explicitly lists nine directional-body IDs and sixteen directional heading slots (mask 15, first body descriptor 2, heading offset 8 and shift 4). Every listed ID has a declared heading rig or manual yaw pivot. This does not establish calibrated mapping from native 3D heading to the original descriptor orientation.

The historical source-recipe rule requires a rig for 25 building recipes, sixteen outside the current runtime allowlist. Current selected studies declare 24 heading/manual-yaw assemblies. Rigellian Missile Launcher (legacy 057) matches the historical recipe rule but has neither audited rotation_rig/yaw_pivot declaration. The source-bound reviewed-mechanism registry now resolves that discrepancy: class 14 follows the legacy missile launch/activity path, and correctly paletted overlays show the shell opening. Existing #970/#990 findings are linked through the #1114 semantic review. The prototype rule is not evidence requiring a yaw head. Exact opening kinematics and 3D state coverage remain unresolved; no rig or asset is regenerated to satisfy the old heuristic.

Current runtime activity selectors identify Terran Landing Pad, Satellite Silo and Missile Silo. Landing Pad and Satellite Silo have no keyed node clip in selected sources. This alone does not prove missing geometry: activity can include attached-ship or descriptor composition, and required body changes must be established separately. These selectors are configuration evidence, not an exhaustive recovered state domain for every race.

## Registered descriptor state exports

Ground Deck is the only selected study with a registered source-bound descriptor export index. Existing `verify_state_exports` revalidated its exact source/revision, mechanism evidence, generator and rendered exports: sixteen descriptors (2 through 17) map to fourteen distinct GLB pose exports. Original state PNG/GLB hashes, sample geometry/collision/visibility reports and render checks remain intact. This is existing technical state evidence, not final visual acceptance or exhaustive client integration.

No registered state export for another model is inferred from clip count or reference frame count. A static source can legitimately serve several presentations; its complete state/variant acceptance remains unestablished until the relevant composition evidence is reviewed. Raw source references are deduplicated by asset with roles retained, preserving the distinction between UI views, runtime sprites and construction sources. All 177 construction-reference dependencies are explicitly marked deferred; none were regenerated or accepted here.

## Reproduction and scope

Run `python tools/blender/audit_catalogue_state_coverage.py --check` to validate `docs/reconstruction/models/state-coverage-audit.json` against current sources. It binds the inventory, gameplay configuration, recipes/rule, #1112 reports and selected metadata, and invokes the existing strict registered-state verifier. The script itself does not execute Blender. Prior actual runtime pose evidence remains separate from this analytical classification.

All final moving/state/variant/artistic and calibrated attachment/game-client gates remain open. No acceptance ledger changed. Required changed-code quality base: `59842e8e6`. This milestone is analytical, with no application runtime changes; an application smoke test is not required. Refining, updates to existing models and construction scaffolding remain deferred.
