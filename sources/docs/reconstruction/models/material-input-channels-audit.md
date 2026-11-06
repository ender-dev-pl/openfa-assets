# Decoded material input channels (#1116)

All 303 selected native sources and their existing GLB exports were inspected in Blender 4.5.15 LTS. This fills the decoded-channel gap left explicitly open by dependency audit #1110. It does not repair UVs or accept complete shaders, final artwork or game integration. Relates to #946 and #1110.

## Executed result

Actual native reopen and GLB import completed for every definition. The sources contain **1,783 used materials**; imported GLBs contain **1,784** material datablocks because one duplicated GLB material name receives an importer suffix. All **7,136 supported input comparisons** match at the stated 8-bit readback precision, including four comparisons for that duplicate. There are no unresolved input paths or decoded mismatches in the final pass.

Both sides decode **698 used image datablocks across 124 models**. The native input descriptors cover 1,360,036,962 channel components; imported descriptors cover 1,705,286,409. These totals include constant descriptors and repeated uses of the same packed channels, not that many distinct source texels. Imported metallic inputs often use the ORM image's blue channel multiplied by a constant, explaining the larger imported descriptor total and 1,050 image-driven inputs versus 698 native image-driven inputs. Each image-to-image primary input comparison also checks the recorded image colour-space roles: all 698 agree.

Per-object sets of used material names match for all 303 sources after the single narrowly verified four-input alias described below. This does not check per-triangle assignment order. Blend and GLB SHA-256 values remained unchanged before/after inspection and match the current authoritative inventory. Existing images, model metadata, builders, original reports and acceptance gates were not changed.

Exact source bindings, decoded hashes/ranges, input provenance, object/material sets, comparison results and the alias are retained under [`material-input-channels`](../../assets/reconstruction/evidence/material-input-channels/findings.json).

## Precision and supported semantics

The four inspected Principled inputs are **Base Color RGB, Roughness, Metallic and Alpha**. The active material output must connect directly to a Principled surface. Supported paths are constants, image Color/Alpha, RGB channel separation, reroutes, and scalar multiplication including an explicitly enabled Math-node clamp. A direct colour-to-scalar path is accepted only if its RGB components are exactly grey; no luminance conversion is guessed.

For each supported input, the tool reads all relevant Blender-decoded pixels, then computes `rint(value * 255)` into unsigned bytes. This is explicitly rounded 8-bit **Blender pixel-readback** equality, not equality of unquantized floats or an assertion about encoded PNG byte layouts. Nonfinite and out-of-range/HDR values are reported as unsupported rather than silently clipped. A truly uniform input can be broadcast against an image; differently sized nonuniform images are not resampled to manufacture a match. Colour-space roles are retained and compared separately where both inputs are image-driven.

The first pass left imported metallic multiplication paths uninspected. Controlled tests were extended to verify that operation, followed by a complete rerun over all 303 sources. Unsupported operations still produce explicit findings; success is not inferred from report presence or from matching image counts.

## Filtration Plant's duplicate name

Rigellian Filtration Plant (`openfa:building/legacy/041`) contains two GLB material definitions both named `RI02 | aged jade shell`. Blender imports the second as `RI02 | aged jade shell.001`. The suffix alone is not evidence of equivalence. The alias is accepted only for this four-input report because the actual GLB repeats the original name, does not contain the suffixed name, and all four decoded inputs match the native material. The original raw names and binding difference remain in the report. This does not accept complete shader, sampler or UV equivalence between the definitions.

Controlled tests reject aliasing a genuinely distinct GLB name, a suffix without a duplicated GLB name, and an otherwise similar material with a changed input. Other tests cover a one-byte pixel difference, constant-image equivalence, distinct nonuniform dimensions, invalid/HDR values, non-grey implicit scalar conversion, RGB channel extraction, multiplication and an unsupported Math operation.

## Reproduction and remaining limits

```text
[local]/openfa-blender.ps1 -Background -PythonScript tools/blender/test_material_input_channels.py
[local]/openfa-blender.ps1 -Background -PythonScript tools/blender/audit_material_input_channels.py
python tools/blender/check_material_input_channels.py
./tools/Verify-ChangedCodeQuality.ps1 -BaseSha cb9958c5f
```

The final full pass produced 303 per-source markers, its final success marker and exit zero. The bound-evidence checker and controlled Blender tests passed. The required repository quality gate passed against `cb9958c5f`. This analytical milestone changes no application code; no application smoke test is required.

These checks do **not** establish UV coordinate parity or sampling, seams/distortion, interpolation/wrapping, normals, emission, specular or other uninspected Principled settings, full rendered appearance, animation/state coverage, assembled attachments or high-detail artistic fidelity. In particular, the three original UV chart gaps in #1111 remain unchanged; identical decoded image inputs do not make an absent UV chart correct. There is no gate promotion. Refining, modifications to older models and scaffolding remain deferred. The long-term reconstruction goal remains open.
