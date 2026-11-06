# Terminator — first authored iteration (#997)

`openfa:terminator`, Terran ship type 4. The authoritative inventory had no registered source model. This first iteration preserves all existing reconstructions and refinements; artistic refining remains deferred by the current-pass instruction.

## Reference evidence

`ship-reference-index.json` binds the original correctly paletted PS4C.256 heading sprites and sixty-frame PS04.VID inventory rotation. Frames 0/15/30/45/59 and an enlarged frame 15 establish the broad swept wings, paired red wing bands, raised central hull, twin bow projections and paired aft exhausts. These images are reference-only; no original pixels or meshes enter the new files.

The functional index provides no mapped narrative. Four catalogue designer mount coordinates establish only a 2D arrangement. Hidden hull sections, wing cross-sections, maintenance details and six 3D socket transforms are independent interpretations; no unproven firing mechanism or animation timing is introduced.

## First authored assembly

Editable Blend and GLB files, four independent hull/red colour and roughness maps, metadata and actual render evidence are under `docs/assets/reconstruction/ships/terran/terminator/`. Fifty-one meshes and five materials include the continuous closed faceted hull, two swept wings, four conformal red bands, inner wing fairings, two aft engine housings, hollow bronze exhaust annuli, dark recessed throats, cooling ribs, bow barrels/probes, shoulder strips, crown vent parts and an aft dorsal tab.

Two measured geometric dents, stains, grain and seeded scratches implement the worn finish. Small components use independent rough alloy/soot materials. Bevels precede box-projected UV assignment; hull ends use explicit nondegenerate triangle fans. Stable helpers are reused, with a separate parameterized hull implementation so old ship geometry and source hashes remain unchanged.

PlacementRoot has local -Y forward. Four authored hardpoint sockets and two exhaust sockets use local +Z forward and remain explicitly uncalibrated.

## Technical evidence scope

The verifier reopens native Blender and imports GLB independently. Native physical parts must be closed with positive volume. GLB UV/flat-normal seam duplicates are welded only in a diagnostic BMesh at 1e-6 model units; closure and exact native geometric vertex counts are required. Original files are not mutated. Other checks cover transforms/bounds, packed source bytes and decoded colour/roughness pixels, local UV projections, two dent depths, common interior contact samples for hull/wing/fairing/engine/barrel/tab, pod/nozzle roots and conformal red wing bands, plus open nozzle axes with recessed throats. Six socket positions/axes are checked through four rigid root rotations.

Actual native/imported renders exercise the standalone target runtime. Whole-object framing, intentional engine macro crops and matched-camera comparisons establish scoped export correctness. Client integration is unchanged. Technical results do not establish artistic acceptance or calibration in the game.

## Later gaps

Final proportions, exact wing profiles, panel layout and crown vent recess/visibility remain for a later artistic pass. The first crown vent interpretation does not yet reproduce the original deep rectangular recess. Hidden underside details, operational/damage variants and calibrated game scale/orientation/mount transforms remain unresolved. No final artistic gate is promoted. Scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for 51 meshes and five materials. Nine actual render views passed framing and export comparison. Both matched-camera threshold-128 silhouettes match exactly; whole-view alpha is identical, while the engine macro differs at four antialiased edge pixels by at most 4/255. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `94aadba5`. No existing model was regenerated or refined.
