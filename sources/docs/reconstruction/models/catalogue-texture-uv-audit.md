# Catalogue texture packaging and UV dependencies (#1110)

All 303 selected native sources and their existing GLB payloads were inspected without changing assets. Relates to #1099 and #946. This checks dependency packaging and declared coordinate availability, not final UV art quality or decoded native/import texture parity.

## Actual inspection

`audit_catalogue_texture_uv.py` ran in Blender 4.5.15 LTS, reopening native sources and evaluating all 10,727 asset meshes at frame 1. It walks connected nodes backwards from active material outputs in actually used material slots, checks used image packaging and original PNG bindings, follows supported image coordinate paths, and checks existing native UV arrays for finite values/loop counts. Unused image nodes do not create dependencies; generated/object coordinate paths do not automatically require UV maps.

The GLB side parses actual JSON/BIN chunks, embedded image/buffer ranges, material texture coordinate selectors including texture-transform overrides, and required primitive TEXCOORD accessors. It checks accessor ranges/strides and finite float/integer values. It does not instantiate the GLB in Blender or decode/re-render texture pixels in this milestone. Sparse/unmapped layouts and unsupported graph paths would remain uninspected, not silently accepted.

The current post-repair pass completed with all 303 per-model markers and final success marker, exit zero. Blend/GLB hashes stayed unchanged during inspection. There are 698 used native image records across 124 models: all are packed and match their current source image bytes. GLB packages contain 698 embedded image records. No unsupported graph/accessor path was encountered. All 1,730 inspected required GLB UV accessors (3,465,687 coordinates) contain finite values. There are no remaining dependency diagnostics in this scope. Equal image totals do not prove decoded pixel/channel equivalence; the separate #1116 audit records that narrower decoded-input evidence.

## Confirmed coordinate gaps

The original #1110 pass found three details lacking the explicitly requested `Authored surface wear` chart. These baseline observations are retained here; [repair #1111](detail-uv-repair.md) now fixes all three:

| Model | Detail | Actual coordinate state |
| --- | --- | --- |
| Strategic Bunker, legacy 045 | RI06 upper mast neck retaining collar | No native UV layer; two exported material primitives lack required TEXCOORD_0 |
| Ultrathermal Lance, legacy 062 | RI23 bronze front strip | No native UV layer; exported primitive lacks required TEXCOORD_0 |
| Ultrathermal Lance, legacy 062 | RI23 bronze base fitting | Existing finite UVMap with 1920 loops and exported TEXCOORD_0; explicitly requested native chart name is absent |

The baseline produced three native diagnostics and three GLB primitive diagnostics across two models, not six independent model defects. Direct inspection distinguished the base fitting's existing alternate chart. The applied repair reuses those values, preserves `UVMap`, supplies the two missing charts and keeps the shader-required chart at TEXCOORD_0. The fresh catalogue audit confirms zero native/GLB dependency diagnostics; actual native/import rendering is separately bound by #1111.

## Evidence, tests and limits

Reports: `docs/assets/reconstruction/evidence/catalogue-texture-uv/`. `check_catalogue_texture_uv_evidence.py` checks current selected files, source PNG/report bindings and aggregates findings; it does not execute Blender itself. Evidence is exact-byte scoped to this checkout.

Controlled Blender tests passed active-output reachability/unused-image exclusion, implicit UV, explicit named UV, generated coordinates, interleaved finite UV data, NaN detection, explicit sparse-layout deferral and truncated accessor rejection, exit zero. Test output is retained. Required changed-code quality base: `36d5f2138`.

The original #1110 inspection changed no model. The later authorized #1111 repair updates exactly two source/export revisions and their verified evidence, preserving geometry, material assignments and all authored wear. No new ledger gate was promoted; the Bunker's existing narrow runtime evidence was renewed for the corrected revision. Complete shader equivalence, UV overlap/distortion/seams, animation/state completeness, calibrated attachments, final artistic fidelity and game integration remain open. Artistic refining and scaffolding remain deferred.
