# Rigellian Health Unit RI05

Tracked in [#974](https://github.com/ender-dev-pl/ed-openfa-game/issues/974), relates to #948, #946 and source milestone #970.

The independently authored editable Blend, standalone GLB, maps, authored-only gallery and review reports are in `docs/assets/reconstruction/buildings/rigellian/health-unit/`. Preserve `openfa:building/legacy/044`, global type 44, definition class 34 and nominal 2x2 footprint. The identity `PlacementRoot` is at ground Z=0. Earlier models remain intact; runtime scale/projection/orientation calibration is pending.

## Source evidence and interpretation

The embedded-palette surface body and catalogue phases 0, 10, 20, 30 and 40 were inspected. RI05 has a broad flared pedestal, narrow neck, rounded head with three visible vertical grille regions, a low circular fitting and a compact three-prong gold fork on a narrow stem. The central grille has a paired pale grid. The narrow crown root is different from RI04's broad stepped gold foundation. Catalogue phases reveal and highlight one view, not a recovered turntable.

Source provenance remains in `rigellian-building-references.json`; original pixels, the enlarged surface and comparison sheet stay under ignored `artifacts/rigellian-building-reference-study/RI05/`. No original image or mesh is distributed in the new asset. Exact grille depths, louvre engineering, inspection-well floor, hidden surfaces and fork connections are authored inference. Wear placement and two small geometric dents are independently authored.

## Actual construction and refinement

Three rounded vertical openings are cut into the head mesh. Each has a recessed backing, continuous retaining frame and five levels of pale cooling bars; the middle grille uses two columns, giving twenty louvre solids in total. The pedestal and head are connected by an overlapping solid neck. The crown has a narrow mounting stem, flared fork bowl, taller slim centre conductor and two shorter side conductors.

Revision 1 put the low circular fitting too near the foot and represented it as a flat face. Surface/readable/highlighted source comparison led to revision 2: the fitting is raised and its centre is cut through both the retaining face and pedestal, with a dark floor embedded in the actual cut bottom. Rays verify that the face's axis is open, its annular face still embeds into the base, and the floor lies more than 0.06 authored units behind the annular face. The purpose and exact internal structure of this source feature remain inferred.

The shell has independent packed 1024x1024 colour/roughness maps, planar 512x512 cap maps, local contamination, stains, scratches and actual dents. The three coated solids use explicit world-placement cylindrical side UVs and planar cap UVs after final mesh construction. All four authored maps are packed in Blend and embedded in GLB; no external image dependency is required.

## Verification and remaining gates

`verify_rigellian_health.py` runs in Blender 4.5.15 LTS and reopens/imports both formats. It checks topology, positive closed-shell volumes, bounds, identity hierarchy, nominal footprint/ground, all three actual grille openings, twenty measured louvre/backing contacts, two measured dent depths, neck/cap overlaps, crown attachment and terminal positions, and the circular fitting/well contacts. A sampled contact graph adds connected-component evidence without claiming exhaustive solid-intersection proof.

Every mapped polygon loop and six planar cap surfaces are checked. Native packed images match authored hashes; full colour and roughness pixels survive GLB ORM packing. Eight material values are compared within one 8-bit quantization step. The imported model is actually rendered with the exact saved native camera. `review_rigellian_health.py` verifies six native 900x900 RGBA views plus the imported view, 24-pixel framing margin, identical threshold-128 silhouettes, tightly bounded antialiased-edge alpha differences and foreground RGB differences. The authored-only gallery and ignored reference comparison are generated separately.

Revision 2 contains 47 meshes and eight used materials. Actual native/GLB and seven render checks pass. No gameplay registration/renderer changed and no client integration is asserted. Final artistic acceptance, precise head/fork/pedestal proportions, fine grille/inspection engineering, comprehensive contacts, construction/damage states and runtime calibration remain open. This is a reference-refined study, not a completed accepted asset.
