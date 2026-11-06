# RI18 Missile Launcher state semantics (#1114)

This consolidates existing #970/#990 findings and resolves the historical recipe discrepancy highlighted by #1113. It supplies source-bound classification, not a new reconstruction, rig or renderer change.

## Confirmed source evidence

The original ENGLISH.TXT record 918 at 0x11774 identifies the Missile Launchers as missile silos. The current definition catalogue and functional-source index both assign global type 57 / RI18 to definition class 14. The original palette-bound RI18 surface contains eighteen descriptors: shadow/base and additional layers 2..17. Actual layer composites and five catalogue phases were inspected. They show a green shell opening toward a circular aperture; catalogue phases reveal/highlight the same spatial presentation rather than proving camera rotation.

`review_ri18_state_semantics.py` independently checks the original archive/source payload hashes, decodes all eighteen indexed layers with their embedded VGA palette, verifies offsets/sizes/index hashes and exact RGBA output against the retained reference PNGs. It also checks original VID/source hashes and the five existing selected phase hashes. No original pixels were copied into distributable model assets and no new image files were generated.

## Legacy dispatch distinction

The unchanged canonical decompilation's analyst-labelled `UpdateAsteroidSurfaceBuildingAnimationDescriptors` (0x450F0) reads the per-global-type definition class. Its class-14 branch calls `UpdateMissileSiloLaunchSpriteFrame` (0x44C70), separately from `UpdateBuildingTurretSpriteFrame` (0x44B80). This is class-based dispatcher evidence, not a mechanism inferred from a filename or frame count.

The launch function uses the attached launch record's signed vertical position/velocity; with no attached record it selects descriptor 2. Launch activity maps to descriptors 2..17. The heading function instead derives its descriptor from the resolved heading with offset/shift/mask. Their shared sixteen-slot domain does not make them the same animation.

These facts establish the silo launch/activity role. They do not recover 3D leaf construction, exact hidden cap kinematics, complete final mixed-colour composition or calibrated 3D motion. The angled bronze attachment is not automatically a weapon barrel requiring a yaw head.

## Preserved prototype and current-client scope

The old recipe calls this assembly a turret and includes a Weapon pivot, so the generic historical authoring rule flags it. That heuristic is preserved for historical-source provenance. `reviewed-mechanism-semantics.json` records the reviewed silo/activity role and that a yaw-head requirement is not established by these sources. The state-coverage audit now consumes and verifies those exact source bindings rather than repeating the unresolved heuristic conflict.

Current C# selector/renderer files and gameplay configuration are hash-bound as reviewed inputs. Their special activity selection uses configured definition IDs. This analysis does not execute a current-client RI18 launch, establish all cross-culture aliases/attachment mapping, or claim an end-to-end gameplay failure. That remains separate from the confirmed legacy class-based dispatcher role.

## Verification and limits

`review_ri18_state_semantics.py --check` passed eighteen layer/palette/offset/index/pixel checks, five retained phase bindings, functional text, catalogue class and decompile/source bindings. `audit_catalogue_state_coverage.py --check` passed the updated 303-record state inventory and existing Ground Deck descriptor-export evidence. Original models, geometry, materials, textures, exports, historical rules and renderer code remain unchanged. No review-ledger acceptance changed.

This is analytical work; no application smoke test is required. Required changed-code quality base: `fcdc45eab`. Exact opening-state reconstruction, final art/game integration and model updates/refining remain deferred; construction scaffolding remains deferred separately.
