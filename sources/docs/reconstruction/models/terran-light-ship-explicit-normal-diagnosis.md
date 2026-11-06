# Native explicit-normal follow-up (#1102)

Follow-up to `terran-light-ship-normal-diagnosis.md` tests the opposite direction from the rejected imported flat-flag experiment. Existing model assets remain unchanged. This is export/runtime diagnosis, not artwork refining.

`probe_terran_light_ship_explicit_normals.py` reopened each native Blend in Blender 4.5.15, captured fitted baseline cameras, copied evaluated meshes in memory, captured native local corner-normal vectors, set all copied faces smooth and explicitly reassigned those captured vectors. Evaluated modifier geometry was copied before clearing modifiers to avoid double application. It rendered front/rear quarter views without saving a Blend or exporting a GLB. Exact native/export/metadata hashes remained unchanged. Process completed with both success markers and exit zero.

`review_terran_light_ship_explicit_normal_probe.py` verifies previous imported/native baseline pixel hashes and new probe hashes, and measures differences against the unchanged GLB target. Both actual comparison sheets were inspected. Evidence is under `docs/assets/reconstruction/evidence/terran-light-ship-explicit-normals/`.

| Model/view | Original native vs GLB max mean RGB difference | Explicit-native probe vs GLB |
| --- | ---: | ---: |
| Combat Eagle/front quarter | 0.594/255 | 0.0114/255 |
| Combat Eagle/rear quarter | 0.426/255 | 0.0113/255 |
| Scoutship/front quarter | 1.960/255 | 0.0324/255 |
| Scoutship/rear quarter | 1.997/255 | 0.0405/255 |

Alpha channels remain identical for every pair. The intervention strongly supports native corner-normal shading semantics as the dominant source of the observed disagreement, rather than changed geometry or material parameters. It changes evaluated-mesh representation and explicit smoothing/normal semantics together, so it does not isolate every Blender implementation detail or prove a sole cause. Residual differences remain and are not accepted as zero.

This identifies a possible technical normalization strategy for a later authorized asset update: align explicit corner-normal use between native and exported representation, then separately verify preserved intended appearance. It is not applied here. Replacing the original native appearance with the GLB appearance requires its own review; closer parity alone does not establish fidelity to legacy. No original mesh/material/texture file, source export or accepted ledger gate changed. Refining and scaffolding remain deferred, and final quality, UV/state/animation, attachment and game-client acceptance remain open.

Required changed-code quality base: `a92bbe96`.
