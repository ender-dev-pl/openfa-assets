# Existing cannon and shield runtime evidence (#1103)

Read-only actual Blender 4.5.15 verification covers Photon Cannon, Plasma Cannon and Shield X10-X50. Relates to #1099, #950 and #946. Source Blend/GLB/metadata bytes remain unchanged; no geometry, material, texture or source export was regenerated.

## Existing source-specific checks

`verify_cannon_equipment.py` passed native/import checks for 47 Photon and 44 Plasma meshes: real axial barrel bores, actual Plasma rear aperture depth and ten casing ribs, material identity/bounds, geometry validity and no invented aiming animation. `verify_shield_equipment.py` passed all five tiers (45, 44, 51, 52, 48 meshes respectively), including sampled true shell thickness, actual window/closed-wall distinctions, geometry/material/bounds and no invented articulation. Both processes exited zero with all seven success markers; their existing tracked reports reproduced unchanged.

## Additional export evidence

`audit_early_equipment_runtime.py` independently reopens native files, captures evaluated per-object geometry/material values, renders fitted front/rear quarter cameras, removes native mesh objects and unused datablocks, imports existing GLBs and renders with identical camera/light settings. All object/material identities match. Six material value tuples per model match exactly. Source hashes are checked before and after. The process exited zero with all seven success markers.

Maximum bidirectional nearest-position error is 1.51277e-7 model units for Photon, 1.11511e-7 for Plasma and 8.97169e-8 for every shield. Maximum per-object bounds error across all seven is 8.99891e-8. Vertex seam duplication is not treated as changed geometry.

`review_early_equipment_runtime.py` binds actual pixel hashes and checks framing for 28 new 768-square renders, measuring differences without promoting acceptance. All fourteen matched camera pairs have identical threshold-128 silhouettes. Photon front-quarter has one differing alpha pixel; all other pairs have identical alpha. Maximum foreground mean RGB differences across each model's two views are:

| Model | Maximum mean RGB channel difference |
| --- | ---: |
| Photon Cannon | 0.1874/255 |
| Plasma Cannon | 0.0613/255 |
| Shield X10 | 0.1964/255 |
| Shield X20 | 0.2511/255 |
| Shield X30 | 0.5398/255 |
| Shield X40 | 0.2612/255 |
| Shield X50 | 0.5866/255 |

The actual combined comparison sheet was inspected. Reports, per-model comparison sheets and native/import renders are under `docs/assets/reconstruction/evidence/early-equipment-runtime/`. Differences remain nonzero; their causes are not established by these measurements. The previous light-ship normal diagnosis must not automatically be assigned as the explanation for unrelated equipment.

No final art, exhaustive UV/corner-normal, animation/state, calibrated gameplay socket or game-client integration acceptance is implied. No ledger gate was automatically promoted. Older assets were not retrofitted with wear. Refining and construction scaffolding remain deferred. Required changed-code quality base: `ab425ff3`.
