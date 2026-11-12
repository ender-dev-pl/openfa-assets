# Missile reference review — issue #958

All 69 definitions across seven cultures have original `_M` surface references
decoded directly from their archive payloads. All 966 frames were rebound to the
correct base palette. Eleven separately bound Terran management previews retain
their own embedded palettes. Sixteen culture pages were visually inspected;
original pixels remain in ignored `artifacts/missile-reference-study/` only.
Source/frame/palette hashes are in `missile-reference-index.json`.

## Palette proof

`GameplayAssets.cs` obtains the terrain palette from the `buttons` sprite,
catalogue-mapped to standalone `_MS/BUTTONS.256`. The surface renderer passes the
active combat/surface palette to both CPU and GPU missile sprite paths.
`CreateAsteroidSurfacePalette` changes only indices 128–159, as specified by the
packaged surface-palette rules. This matches the legacy surface-palette binding
documented in `docs/legacy/missile-mechanics.md`.

Every decoded runtime frame was checked for used indices. None uses 128–159.
Therefore the base BUTTONS colours equal the active asteroid-surface colours
for these missile pixels, independent of asteroid variant/seed. This conclusion
is specific to the checked payload hashes; it is not a blanket palette rule for
all sprites. Index zero remains transparent. PNG channels use masked 6-bit VGA
values expanded to 8-bit RGB, preserving original indexed geometry.

The verifier parses archive/frame tables independently and checks output indices
against the existing legacy exports. Grayscale originals can serve as an index
cross-check, but never as colour evidence. It also verifies all recorded PNG and
palette hashes, source/culture mappings, frame geometry, preview bindings and the
absence of mutable palette pixels across the complete runtime set.

## Reference interpretation and modelling directions

| Culture | Definitions | Visible family traits and limits |
| --- | ---: | --- |
| Terran | 13 | Distinct elongated bodies, red end housings, silver shafts and differing side pods/fins. Eleven management previews resolve substantially more structure than flight sprites: Napalm has separated teardrop-like masses, Hellfire an elongated smooth shell, Nuclear a dark pointed body with side fittings, Virus/Anti-Virus distinct oval side equipment, and Stasis a green cylindrical case. Bug Hunter and Meat-Eater lack bound management previews. |
| Rigellian | 7 | Green central bodies with long split/forked outer prongs, gold or red end fittings, and distinct blue/gold central regions. Preserve open spaces and prong counts rather than generic cylindrical rockets. Hidden transverse geometry remains uncertain. |
| Braccatian | 10 | Gold/copper spindle-like structures with repeated expanded collars, lobes and red/brown tips. Variants alter the arrangement and thickness of repeated masses. Small sprites do not resolve their exact mechanical construction. |
| Mikotaj | 9 | Long green/grey axial structures with visibly separated paired cages/lobes, repeated copper/grey nodes and side rails. Several silhouettes contain real negative space; they are not plain solid rods. |
| Artemian | 12 | Extremely small radial/orb-like glyphs, commonly only 5×5 pixels, with green/gold/blue/orange regions and bands. Frames often do not change orientation. These establish colour/silhouette constraints, not a detailed sphere or any particular hidden solid. High-detail 3D interpretation must be clearly authored. |
| Mauna | 10 | Small grey canister/block-like glyphs, often 6×10 pixels, with repeated slots and coloured end/band variants. Repeated frames do not supply new spatial views. Do not infer unseen cylindrical versus rectangular cross sections solely from enlargement. |
| Achaean | 8 | Slender coloured stems with conspicuous red/pink expanded end clusters and pale tips, plus different axial band colours. Tiny profiles support the placement of expanded masses but not exact hidden equipment. |

All sixteen culture pages were inspected, including every definition. Enlarged
nearest-neighbour images intentionally expose their true pixel resolution; an
enlargement is not added geometric evidence.

## Frames, reuse and unresolved work

- These are indexed flight/launch states, not inventory turntable rotations.
  The documented launch formula uses frames 7–13; later frames include exhaust.
  Do not turn flame trails or isolated effect pixels into solid model geometry.
- The 69 runtime sheets contain 68 distinct complete decoded indexed sequences.
  Virus and Anti-Virus share exactly the same runtime sequence, while their
  management previews visibly differ. Sequence equality does not prove that
  the final editable models should be identical.
- The 11 Terran previews are independent sources, not higher-resolution versions
  of every culture's runtime sprite. No additional preview or rotation is
  fabricated for the remaining 58 definitions.
- Source mappings remain explicit catalogue entries; alien filenames are never
  extrapolated from Terran naming patterns.
- Hidden geometry, dimensions, body/effect separation and launch orientation
  still require per-model investigation. Register no invented socket or hinge.
- No model or programme acceptance gate is completed by palette/reference work.
  Modelling, multi-view rendering, reference comparison/refinement, native/GLB
  validation and final high-detail acceptance remain required for every asset.

Reproduce using `prepare_missile_references.py` followed by
`verify_missile_references.py` with Pillow. Regeneration must be byte-stable.
This analytical milestone changes no gameplay or model runtime; no client smoke
test is required.
