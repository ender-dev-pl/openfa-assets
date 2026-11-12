# Sampled open-boundary coverage (#1109)

This classifies #1107's 347 boundary meshes across 76 definitions using actual unchanged native evaluated geometry at frame 1. It does not repair models, clear the original topology findings or resume deferred refining. Relates to #1107, #1099 and #946.

## Method

`classify_catalogue_boundaries.py` reopens each affected source in Blender 4.5.15, verifies the previous topology/source hashes, reconstructs diagnostic-only world-space 1e-6 welded BMeshes and checks boundary counts against #1107. Other meshes with unflagged, closed components provide conservative cover candidates. Preview-only objects and the boundary mesh itself cannot provide coverage.

Boundary edges are grouped by connected vertices. A group is explicitly marked when it is not a simple closed wire loop. Each group samples at most twelve vertices and twelve edge midpoints. A point counts as inside a candidate only when three fixed oblique odd/even parity rays agree. Nearest surface distance <=1e-5 is ambiguous, not contained. Disagreement or exhausted ray limits remain unknown. This uses actual shell crossings rather than a bounding envelope; bounding boxes are only candidate pruning.

The process completed with success marker/exit zero. Original source hashes remained unchanged. No Blend was saved or GLB exported.

## Measurements

There are 722 connected boundary groups and 13,568 sampled points. Of those, 4,936 points are inside at least one qualifying closed mesh. One hundred points have at least one ambiguous candidate; this can overlap containment by a different candidate.

| Group classification | Groups |
| --- | ---: |
| Every sampled point inside closed geometry | 153 |
| Some sampled points inside | 222 |
| Coverage not established at sampled points | 347 |

For 67 of 347 boundary meshes, every sampled point in every group is inside another qualifying closed mesh. The other 280 have partial or unestablished sample coverage. These are review priorities, not counts of accepted or defective models. A finite set of contained points does not prove coverage between points or across an entire opening. The 238 branched/non-simple boundary networks require additional interpretation regardless of sampled containment.

## Evidence and tests

Per-definition samples include world positions, containing object names, ambiguity reasons, loop/network structure and exact source/topology bindings in `docs/assets/reconstruction/evidence/boundary-coverage/`. `check_boundary_coverage_evidence.py` checks current sources, report selection/hash bindings and sample/count consistency, producing `findings.json`; it does not rerun Blender containment. Evidence is exact-byte scoped to this checkout.

`test_boundary_coverage.py` passed in actual Blender with exit zero: closed-cube interior/exterior, surface ambiguity, a consistently oriented hollow cavity with two shell crossings, cavity wall material, a simple boundary loop and two touching loops forming a branched network. Recorded test output is retained.

This is native-only sampled coverage. It does not prove complete edges/opening coverage, self-intersection absence, intended function, watertight union, imported all-state coverage or final artistic/runtime acceptance. Existing topology findings and the deferred Assault Fighter tessellation concern #1108 remain open. No acceptance ledger gates changed. No model, material, texture or original report changed. Required changed-code quality base: `ad9b2b94`.
