# Hardpoint reference review — issue #955

All sixteen explicitly mapped PH00–PH15 inventory videos were decoded offline
using the original codec and its per-frame palette state, then inspected at nine
samples per definition. Source IDs, video/decoder/executable hashes, frame hashes
and palette hashes are recorded in `hardpoint-reference-index.json`. Original
pixels and reference sheets remain in ignored `artifacts/hardpoint-reference-study/`.
No new model or final acceptance gate is implied by this reference milestone.

## Observed shapes

| Type | Equipment | Visible features to preserve |
| --- | --- | --- |
| 00 | Ion Cannon | Long rounded central housing with red/copper end; broad collar, several rear prongs, two side cylinders on short stems, and a raised rectangular bracket. |
| 01 | Disruptor | Tapered cylindrical body with frontal aperture; large spherical rear mass, smaller rounded body masses, angular side shields and copper connecting pipes. |
| 02 | Napalm Orb | Pointed elongated front shell, bronze rounded rear housing, lateral dark fittings and broad segmented transverse rear rail. |
| 03 | Chaos Bomb | Multiple parallel rounded cylinders with red end caps, visibly arranged in tiers around a central support and upper rectangular bracket. Preserve the tiers rather than flattening into one row; exact tube count must be resolved in close-up modelling. |
| 04 | Vortex Mine | Long segmented cylindrical shell, clipped rear collar, red circular end details and small side openings/projections; not a flat disk mine. |
| 05 | Laser | Tapered front fairing with thin forward tip, elongated rear body, prominent red longitudinal dorsal tube and a dark recessed equipment opening. |
| 06 | Photon Cannon | Low broad rounded top plate with central circular cap, two long slim forward rods/barrels with red ends, and blockier rear equipment with additional red tips. |
| 07 | Plasma Cannon | Thick rounded wedge-like housing, single pointed projecting forward assembly, red ribbed flank region, central top fitting and a large dark circular rear opening. |
| 08 | Static Inducer | Hemispherical studded end with red tips, layered circular collars, and a cluster of three blue rounded lobes on the opposite side. |
| 09 | Warp Generator | Spherical end with yellow concentric bands, separated cylindrical core with copper struts and a broad curved dish-like opposite shell; internal separation is visible. |
| 10 | Deflector | Broad spherical main body, long red-banded pointed projection, circular side boss and exposed rear bracket/connector hardware. |
| 11 | Shield x10 | Tapered connector end, broad annular collar and open swept outer shell exposing dark interior and a small gold central component. |
| 12 | Shield x20 | Related shell and connector, but with different open shell lobes/edges and exposed internal gold element. Do not substitute a scaled x10. |
| 13 | Shield x30 | More enclosed rounded end with layered bands, conspicuous side opening and small external lower cylindrical fitting. |
| 14 | Shield x40 | Cylindrical/bulbous shell with rectangular side window, large dark circular end region and lower external fitting; differs from x30's opening. |
| 15 | Shield x50 | Most enclosed rounded end, smooth broad cap and circumferential bands; lacks the large open petal arrangement of x10/x20. |

These descriptions are observations of visible shape/colour. Names such as
"barrel", "collar" or "connector" are modelling descriptions, not reverse-engineered
mechanical semantics. Exact hidden structure, dimensions and mount orientations
remain unresolved.

## Rig and variant decisions

- All sixteen equipment definitions are global catalogue entries. The decoded
  inventory presentations do not prove that every race uses identical mounted
  geometry, nor that seven cultural versions exist. Preserve that uncertainty.
- The videos rotate the presented equipment. This alone does not establish an
  independently rotating head, a fixed base, an elevation axis, recoil stroke,
  launch motion, or a mechanical hinge. No turret rig is accepted on that basis.
- Model clear visible component boundaries separately, but label inferred pivot
  transforms until additional code/assets establish their function.
- Shield x10–x50 have distinct opening/closure geometry. Their relationship is
  not adequately represented by uniform scaling or colour variants. Opening
  shapes are not evidence that shells animate between tiers.
- Chaos Bomb's tiered cylinders and Photon Cannon's paired thin projections
  require careful count/orientation checks before modelling; avoid generic
  single-barrel substitutes.
- Tiny mounted/catalogue overlays and information icons are separate sources.
  Their external palette bindings and archive-presence questions in the inventory
  are not solved by correctly decoding these videos.
- The ship designer's two-dimensional mount coordinates remain insufficient for
  three-dimensional sockets. Register no invented gameplay transform.

## Verification

Run `prepare_hardpoint_references.py` with the legacy Pillow/Unicorn Python
runtime, then `verify_hardpoint_references.py`. The verifier independently checks
all sixteen inventory mappings, original source hashes, all decoded frame names,
144 selected PNG/palette hashes and review sheet dimensions. Regeneration must
preserve index bytes. Reference-only analysis does not require a client smoke
test and does not constitute model quality acceptance. The next step is actual
independent geometry, rendered comparison and refinement under #950.
