# Read-only proposal for the three missing detail UV bindings (#1111)

This is the **historical read-only proposal**, subsequently superseded by the [authorized applied UV repair](detail-uv-repair.md). At the proposal milestone no source or acceptance evidence was changed. Its original previews and exact baseline hashes remain preserved. Relates to #1110, #948 and #946.

## Proposed change

| Existing detail | In-memory change |
| --- | --- |
| Strategic Bunker: `RI06 upper mast neck retaining collar` | Add the shader-required `Authored surface wear` chart using local dominant-face box projection normalized to existing mesh bounds. |
| Ultrathermal Lance: `RI23 bronze front strip` | Add the same named chart with the same projection rule. |
| Ultrathermal Lance: `RI23 bronze base fitting` | Copy existing `UVMap` corner coordinates exactly into the shader-required named chart; retain the original chart. |

These mappings use the existing authored images. No new wear, material assignment, mesh component or artistic redesign is proposed. Box projection is a technical first-pass mapping, not acceptance of seams, texel density or final texture art. The fitting has 384 original mesh loops; the earlier dependency audit's 1,920-loop figure describes its evaluated mesh after modifiers, not a contradictory source revision.

## Executed verification

Blender 4.5.15 LTS opened both original sources. `test_detail_uv_proposal.py` confirmed that the checker rejects each original missing chart, accepts all three in-memory proposals, preserves every existing chart and every untargeted mesh, and changes nothing on a second invocation. The actual saved sources were never exported or saved.

`audit_detail_uv_proposal.py` compares exact native and evaluated vertex coordinates, edges, polygon indices, polygon material assignments, smoothing flags, corner normals, material-slot names, object matrices and hierarchy before and after the proposal. It also compares packed-image bytes and SHA-256 values of **every file in each original asset directory**. All comparisons passed. Every shader-selected UV face has finite coordinates and nonzero mapped area.

Four actual native renders were produced with the unchanged source camera and scene, before and after the in-memory change. Their alpha channels are identical. Mean foreground RGB differences, on the 0–255 scale, are at most 0.00463 for the Bunker and 0.03888 for the Lance. The changes are small at the overview scale; the comparison sheets were visually inspected. This does not establish a repaired GLB's material or UV parity: no repaired GLB exists yet.

Evidence and before/after sheets are in [`detail-uv-proposal`](../../assets/reconstruction/evidence/detail-uv-proposal/summary.json). The per-model reports bind all original files, proposal scripts, exact geometry snapshots, packed images and preview files. Existing catalogue audits continue to describe the unchanged original models.

## Reproduction

Run the following with the repository's Blender wrapper, then the project's Python with Pillow:

```text
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/test_detail_uv_proposal.py
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/audit_detail_uv_proposal.py
python tools/blender/check_detail_uv_proposal.py
./tools/Verify-ChangedCodeQuality.ps1 -BaseSha 80ee1d078ec4187e5986c599324fcab111290040
```

The original proposal tooling contains no model-save/export path and its revision guard intentionally rejects the repaired sources. The baseline is preserved in Git and in the repair's verified original backups; its helper implementation is archived beside the previews. The current proposal checker explicitly identifies the separately bound replacement rather than claiming the baseline is still current. The user subsequently authorized obvious technical fixes; builder integration, actual native/GLB checks, renewed runtime evidence and refreshed dependent audits are documented in the applied repair. Scaffolding and artistic refinement remain deferred.
