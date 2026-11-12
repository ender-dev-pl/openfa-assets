# RI03 Nourishment Bank: canonical remaster

Tracking: openfa-assets #253, per-building #33. Identity `openfa:building/legacy/042`, definition class 37, footprint 2x2 and construction updates 20 are preserved. Original function record 903 describes production of species-appropriate nutritional substances. Original culture record 18 calls for ergonomic, elegant architecture including industrial equipment; no hidden manufacturing mechanism is inferred.

## Reference and concept feedback

Correctly paletted surface body and catalogue phases were inspected. Three jade vessels, exposed brass interstages, a broad pale equipment face/spine, flared foot and low gold closure are retained. Catalogue reveal/highlight phases do not establish rotation or moving machinery. One actual built-in ImageGen request used the original body and colour phase 20. Its exact prompt is `ri03-concept-prompt-1.txt`; the authored concept is in the gallery. Original pixels remain private. The concept wraps more of each vessel in pale alloy; that sleeve section is interpretation, so the established machined recess/backing/insert layout is preserved rather than copied blindly.

## Current source and geometry

Use only `sources/objects/rigellian/nourishment-bank/model.blend` and `model.glb` for current gameplay, build catalogue and SciTek. Prior sources remain historical, outside current inventory selection. This is one canonical payload, not a separate menu upgrade. Native `PlacementRoot` is identity, local -Y forward, +Z dorsal, ground Z0. Actual world bounds and exact hashes are in `rigellian-building-remaster-delivery.json` and the model runtime report. Gameplay scale/orientation calibration remains a client task; footprint is not a claim of calibrated scene-unit scale.

Evaluated geometry falls from 79,668 to 50,018 triangles while retaining all 43 editable physical component identities, three recesses, spine, foundation, gold necks and authored wear/dents. Each reduction is measured against its own prior evaluated surface in both vertex-to-surface directions and must retain closed positive volume. Maximum accepted deviation is below 0.000619 source units; this sampled surface measure is not exhaustive Hausdorff proof. Existing bevels are applied before measurement, avoiding misleading pre-modifier counts. Seven used materials and four embedded images remain. No batching or Android frame-rate certification is claimed.

## Actual validation and current limits

Blender 4.5.15 independently reopened the saved native and imported the GLB. Unchanged anatomy assertions check exact established vessel dimensions, broad frame width and clearance, real recess depth, embedded backing, recessed inserts and three spine bridges. All 43 native/imported physical components are closed with positive volume. Per-component material bindings and triangle counts match; maximum bidirectional vertex-to-surface export error is below 5.79e-7. An initial material-slot comparison incorrectly included unused native slots; the corrected check compares materials actually used by faces.

Three native/imported camera pairs were rendered and inspected. Alpha is identical; maximum whole-image mean colour-channel difference is below 0.020/255, with at least 58 pixels of framing margin. The actual GLB retains the original stack/foot/equipment relation; exact pocket section and hidden closures remain authored interpretations. Existing material detail is simpler than the artistic concept. Source-bound runtime and visual reports bind all current tools, native/export files, concept and render pixels. The new explicit evidence format is checked by the project verifier; earlier runtime reviews are preserved separately as history, not rebound to the new source.

RI03 is static with no exported clips or movable assemblies. Presentation reveal/highlight remains separate. Construction/damage variants, client calibration, mount/state integration and final user artistic acceptance are not certified. Integrate this canonical source across all consumers and verify it in the real client before treating those separate tasks as complete.

## Reproduction and disk care

Run `remaster_rigellian_nourishment.py`, then `verify_remastered_rigellian_nourishment.py` in Blender background mode with Python exit code 1. The author preserves the earlier source byte-for-byte and uses task-owned temporary export folders with inherited Windows ACLs; they are cleaned by the exporter. Finished authored previews remain outside sources in the gallery. A failed initial OS-temp folder was empty and is eligible for exact-path cleanup only after verifying ownership and contents. No new checkout, build or archive is needed.
