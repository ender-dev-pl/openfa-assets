# RI23 Ultrathermal Lance remaster audit

Issue: ender-dev-pl/openfa-assets#253; building detail: #56.

The canonical model is `sources/objects/rigellian/ultrathermal-lance/model.blend`, with its independently verified `model.glb`. Gameplay, construction menus and SciTek must use this selection; technical wireframes derive from the same geometry. Earlier studies remain historical evidence, not additional runtime payloads.

## Evidence and interpretation

Reviewed actual paletted RI23 surface compositions for all sixteen headings, persistent base descriptor 1, shadow and catalogue phases 0/10/20/30/40. Upper directional overlays use descriptors 2–17; the current game selector uses `2+(((heading+8)>>4)&15)`. This is not RI22's empty-base/full-building arrangement. Original function record 923 describes an effective anti-ship weapon. CDB record 18 supplies Rigellian architectural context, not a recovered mechanism specification. Original pixels remain private.

One built-in ImageGen request was used, within the three-request maximum. Exact prompt and selected output are retained. Paired bronze lances, green bell body and tapered segmented bronze foot broadly agree. Invented root collars suggesting pitch articulation, reduced groove count and omission of the bronze front strip were rejected as model instructions. Latest assessed source refinement, including twelve foot segments, was retained instead.

## Geometry and runtime validation

The source is the latest `rigellian-refined/ri23/model.blend`, SHA-256 `5d5083c96504635d03c12f12f210dea9e5abfc7aa1924318bfd0ae1392f95b55`.

Nine upper/detail components preserve their evaluated source surfaces within 1e-6 model units. Thirteen foot components were reduced by dissolving nearly coplanar subdivisions (0.005 radians), retaining material and UV boundaries. This is tolerance-bounded simplification, not exact geometric identity. Raw source topology has 117,396 triangles; the evaluated source has 119,844. The final evaluated model has 54,344 triangles, 22 closed positive mesh nodes, 7 materials and 9 embedded maps. Packed authored colour/roughness maps remain unchanged.

The reduced foot retains taper, twelve segments, horizontal groove relief, dents and 36 segment-root contact samples. Maximum measured bidirectional source/candidate vertex-to-surface distance is 0.000059. Sampled UV correspondence uses all unique material/UV corners, barycentric interpolation and degenerate triangulation edges; maximum source/candidate error is approximately 0.0000166 UV units. This does not prove the continuous UV field or an exhaustive solid-volume identity.

Actual Blender 4.5.15 verification loads the saved native file and independently imports GLB. Forty-one renders comprise three source views, nineteen native views and nineteen imported views. Three source/native appearance comparisons and nineteen native/import pairs pass stated thresholds. Native/import maximum surface distance is approximately 0.000000121 model units; maximum imported UV error is approximately 0.00000424. Actual renders were inspected; numerical export equivalence is not a legacy-fidelity percentage.

## Integration contract and limits

Identity `PlacementRoot`; Blender -Y forward, +Z dorsal. Footprint 3×3, definition class 18, construction updates 57. Spatial bounds are recorded in `runtime-review.json` and the delivery manifest, in authored units; game placement and scale are not certified by these checks.

`YawPivot` at (0,0,1) rotates around local +Z. Its three moving meshes are the green head and both bronze lances; nineteen meshes remain fixed. Independent `LanceTipSocket -1` and `LanceTipSocket 1` point along local +Z, separated by 0.36 model units. All sixteen authored yaw poses validate tip positions/forwards, hierarchy, moving matrices and fixed-base invariance after export. The sockets are authored attachment references, not recovered ballistic origins. Heading phase/sign remains uncalibrated.

No pitch, firing, glow or operating timing has been invented. RIS3 construction is separate. Sampled contacts/poses do not prove continuous collision freedom. Client state, damage, mounting/scale, Android frame rate and final user artistic acceptance remain separate gates. The unfinished mobile-ship programme #248 remains unfinished.
