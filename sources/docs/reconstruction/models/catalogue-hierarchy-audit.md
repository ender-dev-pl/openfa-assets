# Catalogue hierarchy and sampled existing animation (#1112)

All 303 selected native models and independent GLB imports were inspected in Blender 4.5.15 LTS without changing asset files. The audit compares mesh/empty asset nodes, ancestors, selected helper properties and world matrices. It excludes explicitly tagged preview-only context; it does not invent calibrated sockets or animation.

## Actual results

There are 11,037 nodes in each representation (10,727 meshes and 310 empties). No missing/extra nodes, type differences or parent differences were found. Maximum sampled world-matrix entry difference is 3.83705e-7; no node exceeds 1e-5. Existing helper-axis/calibration metadata is compared where present, without interpreting an authored uncalibrated helper as a recovered gameplay mount.

Twenty-three models contain existing active node animation; their exports contain twenty-three clips, one per animated model. Active action and unmuted CLIP NLA strip ranges select normalized phases 0, 0.25, 0.5, 0.75 and 1. World transforms agree at these samples. Muted tracks do not extend the range. No unsupported active NLA strip, driver or multi-clip case was encountered. The final full-catalogue pass completed with all 303 markers and final success marker, exit zero; source Blend/GLB hashes remained unchanged.

The initial diagnostic considered active actions only and conservatively flagged all NLA tracks. Ground Deck's source uses active NLA without a current action, while importer stash tracks can be muted. The implementation was corrected to include active CLIP strip timeline ranges and ignore muted tracks, then the full catalogue was rerun. No transform tolerance was relaxed.

## Metadata transport distinction

Nineteen older Rigellian exports omit three native PlacementRoot custom properties: catalogue_id, footprint_width and footprint_height. Per-model IDs are listed in `findings.json`. The external model.json for every affected model still contains the matching ID and footprint; the evidence checker verifies and hashes these files. This is a root-extras transport difference, not evidence of missing geometry, incorrect placement or a gameplay failure. A final export-consumer contract must decide whether to use embedded extras or companion metadata before any optional reexport. No asset was reexported here.

## Evidence and tests

Reports: `docs/assets/reconstruction/evidence/catalogue-hierarchy/`. `check_catalogue_hierarchy_evidence.py` binds current selected source/report/parser hashes and external metadata where properties differ; it does not execute Blender itself. Evidence is exact-byte scoped to this checkout.

The controlled Blender test creates a separate synthetic cube/root/socket hierarchy, compares active-action and active-NLA motion, excludes a muted distant track, then performs a single-action GLB round-trip. Parent/metadata transport and normalized pose matrices match (maximum 1.81295e-7). Deliberately altered parent/calibration fields are detected. Test process exited zero with success marker; output is retained. Synthetic fixture exports remain ignored in artifacts/ and are not game assets.

This is node-transform sampling, not complete deformed/skinned geometry validation, continuous collision clearance, every keyframe/all possible state coverage, source-function or legacy-timing fidelity. No final art, calibrated attachment, game-client or ledger acceptance was promoted. Model updates/refining and scaffolding remain deferred. Required changed-code quality base: `824978380`.
