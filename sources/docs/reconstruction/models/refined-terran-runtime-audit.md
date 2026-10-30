# Existing refined Terran building runtime evidence (#1104)

Forty existing Terran building sources were revalidated without rebuilding or changing artwork. Relates to #1099, #948 and #946. The older refined sources and subsequent radiation-filter/screen-generator corrections are preserved; no wear was retrofitted.

## Actual source-specific runtime

`verify_refined_terran.py` completed all forty native/import checks in Blender 4.5.15 LTS, with forty `REFINED_TERRAN_VERIFIED` markers and final `REFINED_TERRAN_VERIFICATION_OK 40`, exit zero. Full recorded output is retained in `docs/assets/reconstruction/evidence/refined-terran-runtime/source-specific-verifier-output.txt`.

Checks include generator/source provenance, expected object/detail counts and roles, materialled geometry, bounds, asset metadata and independent GLB imports. Source-specific checks confirm splayed filter intake directions and wall radii, inclined crystalline screen emitters/emission, turret moving/static hierarchy with sampled native/import rotation and fixed bases, and the eight-leaf silo iris. Iris rays hit leaves when closed and a lower surface through the open hatch. These sampled checks do not exhaustively accept all mechanisms/states or legacy fidelity.

## Additional evaluated export evidence

`audit_refined_terran_runtime.py` independently reopened all forty sources and imported existing GLBs, comparing all 2801 mesh identities, evaluated world-space geometry and material values. Native frame 1 and imported frame 0 select corresponding start poses. Every source Blend/GLB/metadata hash remained unchanged. Maximum bidirectional nearest-position error is 3.42403e-7 model units, maximum bounds error 2.38419e-7, and material parameter error zero. All object and material identities match.

Sixteen new actual 768-square renders cover Solar Panel (PB04), Radiation Filter (PB05), Screen Generator (PB10) and Missile Silo (PB14), each from front/rear quarters in native/imported scenes. Cameras/lights are matched, and the actual combined comparison sheet was inspected. All eight threshold-128 silhouettes match. Alpha differs in five pixels for Solar Panel/front, one Filter/front and one Screen Generator/rear; remaining pairs are identical. Maximum foreground mean RGB channel differences across each model's two views are 0.0447/255, 1.4613/255, 0.0137/255 and 0.0111/255 respectively. Filter shading remains an unresolved render-parity difference; no cause is inferred from the previous unrelated ship diagnosis.

The first diagnostic pass completed geometry comparisons but omitted selected imported renders because a loop variable shadowed the building index. The diagnostic script was corrected and the full forty-model pass rerun successfully, producing all expected selected views. No assertion or pixel threshold was weakened.

`review_refined_terran_runtime.py` verifies actual render hashes/framing and records pixel differences. `summarize_refined_terran_runtime.py --check` binds the reports, current sources, scripts and complete recorded source-specific verifier output. This summarizer itself does not execute Blender. Reports are exact-byte evidence for this checkout; they do not automatically establish portable normalized-text ledger evidence.

No source asset/export changed, and no accepted ledger gate was added. No final quality, exhaustive topology/UV/corner-normal, animation/state completeness, calibrated gameplay attachment or game-client integration acceptance follows. Refining and construction scaffolding remain deferred. Both Blender runs completed successfully; required changed-code quality base: `f673c1c5`.
