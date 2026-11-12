# Rigellian Databanks RI08

Tracked in [#978](https://github.com/ender-dev-pl/ed-openfa-game/issues/978), relates to #948/#946 and source milestone #970.

The independently authored editable Blend, embedded-texture GLB, authored-only gallery, maps and reports are in `docs/assets/reconstruction/buildings/rigellian/databanks/`. Preserve `openfa:building/legacy/047`, global type 47, definition class 255 and nominal 2x2 footprint. `PlacementRoot` is identity at ground Z=0. Existing models remain intact; runtime scale/projection/orientation calibration is pending.

## Evidence and interpretation

The embedded-palette surface body and catalogue phases 0, 10, 20, 30 and 40 show a lower drum with gold fields and dark vertical slots, narrow connecting neck, flared middle housing with a large gold circular fitting, upper head with a row of gold fields, twin supports, a small side module and a silver three-prong crown. The highlighted phase identifies two upper lower-drum fields and one beneath the right-hand field. Hologram phases reveal/highlight one spatial presentation, not independent camera rotations.

Provenance remains in `rigellian-building-references.json`; original pixels and comparison sheets stay under ignored `artifacts/rigellian-building-reference-study/RI08/`. Exact channel depth, fitting/casting engineering, small head fasteners, side-module depth, hidden surfaces and fork connections are independently authored inference. No original image or mesh is distributed in the new model.

## Construction and refinement

Three actual channels are cut into the lower drum with recessed supported backings. Six small gold fields sit in retaining bezels that embed into the drum or collar. A large brass pressure face and retaining ring meet a closed cast bezel on the flared housing. Twin pale supports overlap both the upper head and crown bowl; the side module embeds into a support and its dark inset embeds into the module casing.

Revision 1's flat-backed circular bezel failed an offset root-contact check near a profile break. Revision 2 replaces it with a body-fitted cast root sampled against actual housing geometry, maintaining a planar pressure face and embedding the back into the body. Verification checks five pressure-face points and 32 flange/root positions around the circumference. Actual source comparison then led to revision 3: the large fitting moves higher onto the sloped housing and the lower gold-field pattern becomes two upper fields plus one below the right field.

Three shallow geometric dents and independent packed 1024x1024 shell/512x512 cap colour/roughness maps provide localized contamination, stains, fine scratches and restrained roughness variation. Cylindrical side UVs and planar end UVs are assigned after construction. Analytic radial/profile normals preserve lower-drum shading around Boolean cuts. All four authored maps are packed in Blend and embedded in GLB.

## Verification and gates

`verify_rigellian_databanks.py` reopens the native file and imports standalone GLB in Blender 4.5.15 LTS. Checks cover topology, positive closed-shell volumes, evaluated bounds, hierarchy/footprint/ground, three actual slot/backing contacts, three dent depths, neck/housing overlaps, six small fitting contacts, five large pressure-face points, 32 embedded cast-root positions, twin-support/head/crown overlaps, side-module inset contact and crown terminal positions. A connected nearest-surface sample graph is supplemental evidence, not exhaustive solid-intersection proof.

Every mapped loop and eight planar end surfaces are checked. Native packed images match authored PNG hashes; full colour/roughness pixels survive glTF ORM packing. Eight used material values agree within one 8-bit quantization step. The imported model is actually rendered with the exact native camera. `review_rigellian_databanks.py` checks six native 900x900 RGBA views plus the imported view, 24-pixel framing margin, exact threshold-128 silhouettes, bounded antialiased-edge alpha and foreground RGB differences.

Close top inspection then exposed near-coincident surfaces at the upper-head/housing crossing. Revision 4 places the machined collar at that actual interface and aligns its dirt field with the joint. Eight radial ray pairs verify that the collar embeds into the housing and covers the crossing by more than 0.005 authored units, rather than merely sitting above the defect.

Revision 4 has 45 meshes and eight used materials. Native/imported and seven render checks pass. Only the scoped Blender `native_and_glb_runtime` gate is recorded against exact-file evidence under #976; all other gates remain false. Precise proportions, upper-head/side-module interpretation, fine casting/fork detail, comprehensive contacts, construction/damage states and game-client integration/calibration remain open. No gameplay renderer/registration changed; this is not final artistic acceptance.
