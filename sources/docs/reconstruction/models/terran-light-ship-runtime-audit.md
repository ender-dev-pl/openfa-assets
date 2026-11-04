# Existing Terran light-ship runtime evidence (#1101)

Actual Blender 4.5.15 verification was performed on unchanged Combat Eagle and Scoutship native/export files. Relates to #1099, #949 and #946. Existing artwork, including earlier refinements, was preserved; no wear retrofit or source regeneration occurred.

`verify_terran_light_ships.py` passed native and independent imported checks for both models. Eagle checks include twelve clear notch rays, eight solid rear-arm rays, substantial arm depth and required components. Scout checks include the real recessed oval centre, closed raised rear rim, separate pod and fitted crown/shoulder elements. Existing checks also cover geometry validity, seven materials, source hashes and imported bounds. Re-running this verifier reproduced its tracked reports without tracked differences.

`audit_terran_light_ship_runtime.py` then reopened each native asset and evaluated actual mesh geometry, rendered two fitted camera views, removed native mesh objects/unused datablocks, imported the unchanged GLB and rendered at the exact same camera/light settings. Source Blend/GLB/metadata bytes remained unchanged. Per-object geometry/material reports and eight actual renders are in `docs/assets/reconstruction/evidence/terran-light-ship-runtime/`. Both comparison sheets were inspected.

| Model | Meshes | Max bidirectional position error | Max bound error | Material value error | Maximum foreground mean RGB difference |
| --- | ---: | ---: | ---: | ---: | ---: |
| Combat Eagle | 112 | 2.70283e-7 | 1.19210e-7 | 0 | 0.594/255 |
| Scoutship | 135 | 2.40275e-7 | 2.38419e-7 | 0 | 1.997/255 |

All mesh and material identities match. Alpha channels and threshold-128 silhouettes are identical in all four camera pairs. `review_terran_light_ship_runtime.py` verifies actual pixel hashes and framing and measures differences without concealing them behind a permissive pass threshold. The remaining RGB differences are not zero; cause is not established by this milestone. Native/export normals and shading need separate investigation before claiming full render parity. Geometry/material parameter equality does not prove corner-normal equality.

No final artistic, UV, animation/state, attachment or game-client integration acceptance follows from this evidence. No ledger gate was automatically promoted. Existing models remain untouched and refining/scaffolding remain deferred. Both Blender processes completed with their success markers and exit zero. Required changed-code quality base: `01549bb5`.
