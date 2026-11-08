# OpenFA extension missile models

Issue [#240](https://github.com/ender-dev-pl/openfa-assets/issues/240). These models reproduce the existing user-supplied OpenFA extension artwork. They are not missile bodies recovered from Fragile Allegiance. Original extension references already live in `sources/artwork/interceptor/` and `sources/artwork/decoy/`: their RGB/RGBA colours are authoritative; no legacy palette is applied. All151 frames of each menu GIF were available; sampled rotation phases were reviewed together with the full-resolution body, bundle and separate-segment images. The earlier menu GIF is a turntable, so separation is an explicitly requested new presentation.

## Canonical deliverables

| Product | Source/export | Package |
| --- | --- | --- |
| `openfa:missile/interceptor` | `interceptor/model.blend`, `interceptor/model.glb` | `openfa.interceptor-missle` (intentional spelling) |
| `openfa:missile/decoy` bundle | `decoy/model.blend`, `decoy/model.glb` | `openfa.advanced-munitions` |
| Decoy individual visual segment | `decoy/segment.glb`, exported from the same editable source/mesh | `openfa.advanced-munitions` |

There is one editable Decoy source, one shared segment mesh and four independent segment nodes. The standalone segment export is a required product view, not a separately remodelled body. `openfa:missile/decoy-segment` in authored node extras is a **proposed visual binding**, not a new gameplay product. The game worker must map the existing separation targets to that visual. Do not add either extension's rules or products to the standard package. Existing Classic rasters remain available.

Prefer reusing the shared mesh/subtree from the bundle resource for individual targets if the game renderer supports this, recentering its placement and disabling menu animation for flight. `segment.glb` is the portable fallback for consumers requiring a standalone resource; do not automatically package/load both exports when one shared resource suffices. The four bundle nodes already reference one glTF mesh, not four duplicated model payloads.

Interceptor retains the dark blue elongated body, pointed golden nose, yellow shoulder/fin plates and silver vent/latch face. Decoy retains silver slender bodies, blue rounded nose shells, side mechanisms, twin coupling bands, aft blue pods and dark nozzles. Hidden sections, exact fins/rear fittings, subdivisions and moderate paint wear are authored interpretations. Broad quiet shells, joint grime and sparse scratches preserve the reference identity; there is no invented weapon equipment or recovered socket calibration. Two shared1024-square PBR maps and one material serve both products.

Reference review corrected the first Interceptor's excessively thin radial section: its final fin-span/length ratio is approximately0.282, compared with roughly0.29 in the supplied artwork. This is a proportion diagnostic rather than a physical-scale claim or automated artistic score.

## Motion and menu contract

`DecoyMenuSeparation` is a six-second clip in `decoy/model.glb`. Named roots `DecoySegment0` through `DecoySegment3` retain a shared mesh. At0–0.5s the module remains joined;0.5–3s spreads all four segments radially,3–4s holds them apart,4–6s returns them for a seamless menu loop. This return is menu-only. A one-way flight presentation can stop/hold at3s; do not replay the return as simulated reassembly. The source keyframes are native30fps; the actual imported-GLB WebM preview is24fps/144frames. Every frame is rendered, not a slide sequence.

Each projectile retains its own collar/lock parts during separation; the neighbouring contact pads meet in the joined state and move apart with their projectile. Geometry/nodes are directly animated. Clip timing is an authored menu choice and must not replace package simulation timings. Package data currently defines four harmless Decoy targets, range96 and midpoint separation; these are simulation settings, not physical dimensions or recovered animation durations. Interceptor engagement/launch/interception values likewise do not establish model size.

## Axes, scale and attachment proposal

These new assets use native Blender forward-Y and up+Z, exported glTF forward-Z/up+Y. Bounds, geometry counts and imported motion are measured in each `runtime-verification.json`. Native lengths are approximately10.4/10.49 authored units. WorldSize48 is a proposed compatibility fitting value taken from the current generic surface-missile resolver, not metres or a calibrated new missile size. A bundle and its single segment must share one length-based scale; independently fitting each by width would break that relationship.

The existing Terran Stasis refined source documents **+Z nose**, so these exports are not an implicitly calibrated drop-in rig match. Converting native-Y nose to that older+Z convention requires a-90-degree X rotation; verify its equivalent in the game's imported coordinate space. Client axis/scale mapping must be explicit and tested. `ExhaustOrigin` is an optional authored helper at the centre aft end (Interceptor Y5.1; Decoy Y5.24); it is not a recovered hardpoint. For the four Decoy exhausts, derive each segment's aft point from its own node transform. No exhaust shader, flight trajectory or projectile AI is embedded in the model.

## Verification and budget

Interceptor:6,628 triangles,1 mesh/draw batch. Decoy:10,944 triangles per segment,43,776 submitted for four instances,4 mesh nodes referencing1 shared mesh. Both use1 material and2 packed1024-square maps (about8MiB decoded RGBA texels before mipmaps, before any cross-asset GPU deduplication). Semantic construction groups survive as editable vertex groups in the native source.

The cleaned saved Blend sources and independent GLB imports are checked in Blender4.5.15, including closed nonzero geometry, UVs/materials/packed maps, bounds, multiple-frame geometry correspondence, shared instancing, four moving roots and sampled non-overlapping segment bounds throughout the full clip. The standalone segment is checked against the exact bundle mesh. Actual imported renders and the WebM carry source/export/verifier hashes. Native/import render pixel comparisons and video decoding provide additional delivery checks. These establish asset-runtime validity; artistic review and actual game/Android integration, lighting, separation visibility and performance acceptance remain separate.

Both interactive and Markdown galleries include the models and a playable separation preview. Authored outputs are reproducible with `generate_extension_missile_materials.py`, `author_extension_missiles.py`, publication cleanup and `verify_extension_missiles.py`. The renderer streams through one overwritten task-local PNG instead of retaining a frame archive. Existing models, source artwork and legacy caches are unchanged.

Reproduction requires Blender4.5.x, Python with Pillow/NumPy, and ffmpeg/ffprobe on PATH. `OPENFA_MISSILE_VERIFICATION_ARTIFACTS` may select a task-owned output folder; otherwise verifier scratch output stays under the repository ignored `artifacts/extension-missile-models/`.
