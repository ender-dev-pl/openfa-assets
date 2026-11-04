# Achaean missile reference audit and Frighteners brief (#1091)

This is a reference-analysis milestone, not an authored-model milestone. First missile-source coverage remains 61/69; all eight Achaean models remain to be authored. Existing reconstructions/refinements and renderer code are unchanged. Relates to #951 and #946. Refinement and scaffolding remain deferred.

## Bound evidence

Run `python tools/blender/audit_achaean_missile_references.py --check`. The audit binds ACM1-ACM8, eight definitions and 112 correctly BUTTONS-paletted indexed frames. It checks actual frame bytes, indexed canvas hashes, palette RGB hashes and transparency index zero, then records each crop, binary occupancy hash and occupied pixels per row. Original archive-entry hashes and catalogue/cultural index hashes are retained. No management preview is bound. This establishes source identity, not calibrated 3D geometry.

The actual frame-3 family comparison and full fourteen-state Frighteners sheet were inspected. They remain ignored at artifacts/issue-1091-achaean-reference/. Tracked files contain analytical data and prose, not copied original pixels. The general reference proof passed 69 definitions/966 frames/11 previews; the cultural index passed six source-anchored sections.

## Body and orientation finding

Frighteners flight frame 3 is 5x15. Launch frame 9 is also 5x15. Rotating flight frame 3 by 180 degrees produces exactly the same indexed pixels as launch frame 9: zero index differences and zero mask differences. The reproducible audit asserts this equality for Frighteners and records the corresponding comparison for every Achaean definition.

Thus the pale pointed end, brown shaft with three red/ochre transverse fields, wider pink region with lateral projections and short red terminal all belong to the shared body image in these two states. Do not discard the wider pink region as exhaust. In the launch presentation the pale tip is above the shaft, while the red terminal is below the wider pink region. Later frames 10-13 add a distinct flame/effect group below that terminal and have larger crops (Frighteners 5x25, 5x25, 5x20 and 5x23). Those larger bounds must not become solid model length. This relationship establishes relative presentation direction, not launcher socket coordinates, propulsion hardware or an animation mechanism.

Frames 0-6 show several inclined presentations. They are flight states, not a calibrated full turntable. A new model should compare its projected envelope against these presentations without claiming hidden dimensions recovered from them.

## First Frighteners model brief

ACM1, global type 61/local type 0. Catalogue explosive effect, ore units 18, budget cost 1 and production investment/updates 2 are confirmed. Functional text establishes the name; no mapped detailed missile narrative is established.

Author an elongated independent body with a narrow pale tip, brown shaft and three red/ochre transverse colour fields, a broader pink shoulder region with lateral projections, and a short red rear terminal. Curved sections versus flat plates, actual thickness, rotational symmetry, fin sections and small maintenance details remain interpretations. Preserve the observed relative widths before adding detail; do not reuse Mauna block geometry or Artemian spheres merely because their checks pass. The three colour fields do not establish external sub-warheads or separable rings. Do not model the additional launch flame as solid geometry.

Independent stains, scratches, grime and small physical dents are required. Produce editable Blend/GLB, actual multi-view renders, original/render comparisons and independent native/import validation of closure, UVs, materials, hierarchy and alignment helper. Final artistic acceptance and runtime socket calibration remain distinct gates.

## Culture and family scope

Achaean ENGLISH.CDB Architecture record 166 at 0x9d65, 339 bytes, describes curves, onion domes and occasional slender towers externally, decorated crowded interiors and comfort. That is direct building evidence. Curved vehicle sections may be a contextual choice where compatible with the actual sprite; domes, furnishings and towers are not justified on these missiles.

The actual family comparison shows shared broad pink shoulders but distinct long-body fields: Frighteners has red/ochre bands on brown; Harmers ochre bands; DripFire green fields; Seizure mixed green/ochre fields; Ground Breaker blue fields; Ground Maker green/yellow fields; Hold It There a long red/orange region; Thief-in-the-Night mostly brown. These are colour/layout observations, not confirmed hidden mechanisms. Preserve each definition independently.

## Remaining work and validation

No new Blend/GLB exists in this milestone. Frighteners geometry, independent wear/dents, native reopen/import verification and authored render review are pending under #1091. The analytical change requires no application smoke test. Required changed-code quality base: b40037c6.
