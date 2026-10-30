# Applied three-detail UV repair (#1111)

The user authorized obvious technical corrections on 2026-10-30. The previously reviewed three-detail UV proposal is now applied to the existing saved sources, without rerunning their geometry builders. Strategic Bunker advances from revision 2 to 3; Ultrathermal Lance advances from revision 1 to 2. Artistic refining, new wear on older models and scaffolding remain deferred. Relates to #1110, #948 and #946.

## Applied scope

- `RI06 upper mast neck retaining collar`: add the shader-required `Authored surface wear` chart using local dominant-face projection normalized to existing bounds.
- `RI23 bronze front strip`: supply that same missing chart.
- `RI23 bronze base fitting`: reuse the original UV coordinates, preserving the `UVMap` name and its exact data. Keep the shader-required chart first so shared bronze materials consistently use TEXCOORD_0 rather than requiring a material-specific second UV set.

No vertex position, polygon, smoothing flag, material assignment, corner normal, object hierarchy/transform or packed-image byte changed in the native/evaluated sources. Exact before/after snapshots, baseline file hashes, original backup locations and reopened-source checks are bound in [`detail-uv-repair`](../../assets/reconstruction/evidence/detail-uv-repair/findings.json). All original authored colour/roughness PNGs and wear metadata remain byte-identical. Both builders now reproduce the binding, and the existing verifiers explicitly check these formerly omitted details without relaxing their original material/structure assertions.

The migration preserves original directories under the unique `artifacts/issue-1111-applied-uv-repair/` paths recorded in each report. Its strict revision/baseline guard prevents accidental reapplication. The earlier read-only proposal and previews remain historical evidence; its checker identifies the separately verified replacement. The proposal helper implementation is archived with stable LF bytes.

## Actual native and GLB verification

Both original source-specific verifiers passed after the repair: Bunker's 53 meshes and Lance's 13 meshes retain their structural contacts, bounds, materials, packed pixels and mapped UVs. Lance's manual yaw assembly and paired tip sockets pass the existing orientation checks. Existing seven-view Bunker and eleven-view Lance framing/alpha/pixel reviewers passed, with unchanged acceptance thresholds. The before/after native binary silhouettes match exactly.

A separate close-up test evaluates every material-selected UV corner on the three repaired objects after modifiers and compares it bidirectionally with the actual imported GLB. Maximum position error is 3.59e-7 source units; maximum UV-coordinate error is 2.39e-7. No UV/material corner lacks a corresponding position/UV/material tuple. Source corner counts differ from imported triangle corner counts as expected; this is coverage of the tuples, not a false one-to-one topology assertion.

Matched-camera isolated detail renders are retained. Lance's maximum mean foreground RGB difference is 0.00514/255. Bunker's isolated collar still has a small shading discrepancy (maximum mean RGB difference 1.744/255, one threshold-128 edge pixel differs, maximum alpha difference 4/255). This is recorded explicitly, not presented as perfect shader equality or hidden by a whole-building average. The full-building render checks pass; the direct UV comparison establishes that the residual isolated shading discrepancy is not a missing/mismapped UV chart. Complete shader/normal/render equivalence remains a separate technical question.

Actual new renders and before/after sheets were inspected. Existing artwork and hidden geometry were not redesigned to address a UV dependency error.

## Dependent evidence and acceptance boundaries

All four existing 303-model audits were executed again: topology, UV dependencies, hierarchy and decoded material inputs. The fresh UV audit has **zero dependency diagnostics**, with 1,730 finite required GLB UV accessors and 3,465,687 coordinates. All 698 packed images still match their source PNGs. The 7,136 decoded four-input comparisons remain equal at the previously stated 8-bit readback precision. No new hierarchy or topology flag was introduced by this change.

Topology component traversal/floating-summation order can vary between Blender processes. After the full run, the 301 historical per-source topology measurements were retained only where the Blend, GLB and auditor hashes are exactly unchanged; the two changed source reports retain newly executed results. The summary records this reuse explicitly. All 76 boundary reports still bind byte-identical sampled sources/topology reports, so only their catalogue index was renewed. The 57 ship/equipment source bundles and other attachment inputs are likewise byte-identical; their unrelated inventory index was rebound only after revalidating every bundle. No sampled result or accepted calibration was fabricated by changing hashes alone.

The source-specific Rigellian revalidation executes only the two changed bundles and reuses 21 previous results after exact source/verifier/report checks. Its 23-model overview was renewed. First-source and state-coverage indexes were regenerated; the existing RI18 semantic review remains valid. Inventory verification passes for 303 definitions and 1,444 reference occurrences.

The Bunker's existing narrow native/import runtime evidence bundle is renewed for revision 3. There are still nine accepted technical ledger entries; no new gate or artistic acceptance was promoted. Lance remains a technically checked study, not final art. Existing unrelated topology, state, attachment and shader limitations remain open.

## Runtime and quality checks

`Run-ClientSmoke.ps1 -NoRestore -WindowSize 1600x900` built with one MSBuild node and disabled shared compilation/build servers, initialized the real client, entered gameplay, rendered and exited cleanly. Evidence is under `artifacts/issue-1111-client-smoke/a4d5ea1b5dbd47429faddab9c08c4361/`. This is a startup regression check, not proof that these study GLBs are integrated into gameplay. The dedicated Blender/native/import tests above verify the changed models.

The required `./tools/Verify-ChangedCodeQuality.ps1 -BaseSha 894aaf5e0` gate passes. Relevant commands:

```text
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_rigellian_bunker.py
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_rigellian_ultrathermal_lance.py
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/test_detail_uv_proposal.py
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_detail_uv_roundtrip.py
python tools/blender/check_detail_uv_repair.py
python tools/blender/check_detail_uv_proposal.py
python tools/blender/verify_reconstruction_inventory.py
```

The repair resolves the three confirmed UV dependency failures. It does not complete the long-term reconstruction goal or accept artistic fidelity, full state coverage, calibrated attachments or game integration.
