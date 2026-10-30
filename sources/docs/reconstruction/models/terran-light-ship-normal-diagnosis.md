# Terran light-ship normal diagnosis (#1102)

Read-only diagnosis continues #1101's measured native/GLB shading differences. Existing Combat Eagle and Scoutship assets are unchanged; this is technical export investigation, not artwork refinement. Relates to #1099 and #949.

## Actual normal measurements

`audit_terran_light_ship_normals.py` runs in Blender 4.5.15, captures evaluated world-space corner-normal sets, independently imports each GLB into a factory-empty scene, and matches geometric positions within 1e-5 model units. It compares both directions because export triangulation introduces additional corners. Exact source asset hashes are checked before and after. Both runs completed with success markers and exit zero.

Eagle has two objects with maximum vector error above 0.001: Swept structural wing (0.0021048 imported-to-native) and Wing trailing service panel.005 (0.0011789). Scout has fourteen objects above 0.001, with maximum 0.0013023, including aft cooling louvres. No measured direction exceeds 0.01. These are Euclidean unit-vector distances, not degrees. Per-object flat/smooth/custom-normal settings and all directional counts are recorded in `docs/assets/reconstruction/evidence/terran-light-ship-normals/`.

Nearest normal sets do not prove triangle/corner correspondence or interpolation equivalence. In particular, Blender's exposed custom corner vectors and the renderer's treatment of flat polygons must not be assumed interchangeable. Small vector-set errors alone do not explain the larger pixel differences.

## Controlled negative experiment

`probe_terran_light_ship_flat_shading.py` reopens the same source to recover camera/light settings, imports the unchanged GLB, and sets flat shading only on imported objects whose evaluated native polygons were entirely flat. It changes 106 Eagle objects and 129 Scout objects in memory. Mixed smooth/flat objects remain untouched. It renders two camera views per ship and never saves or reexports models. `review_terran_light_ship_flat_probe.py` binds previous baseline pixels, new probe pixels and reports, then measures the same foreground differences. Both actual comparison sheets were inspected.

| Ship/view | Baseline maximum mean RGB difference | Flat-flag probe maximum mean RGB difference |
| --- | ---: | ---: |
| Eagle front quarter | 0.594/255 | 2.831/255 |
| Eagle rear quarter | 0.426/255 | 2.504/255 |
| Scout front quarter | 1.960/255 | 2.081/255 |
| Scout rear quarter | 1.997/255 | 2.128/255 |

Alpha remains identical for every comparison. This experiment rejects blanket restoration of flat flags as a parity fix for these assets. It does not establish a sole root cause or accept the unchanged export's render fidelity. Further work should inspect corresponding triangles and actual shading interpolation rather than applying this rejected change.

All source Blend/GLB/metadata bytes remain unchanged. No accepted ledger gates were added. Final art, UV/state/animation completeness, calibrated mounts and game-client integration remain open. Refining and scaffolding remain deferred. Required changed-code quality base: `796e040d`.
