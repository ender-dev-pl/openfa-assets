# Command Cruiser — first authored iteration (#1000)

`openfa:command-cruiser`, Terran type 8. The authoritative inventory registered no source model. This first iteration preserves existing reconstructions/refinements and defers further artistic refining under the current-pass instruction.

## Reference evidence

`ship-reference-index.json` binds correctly paletted PS8C.256 heading sprites and sixty-frame PS08.VID. Rotation frames 0/15/30/45/59 and enlarged frames 0/15 were inspected. Visible features include the elongated rectangular deck, rounded bow, raised rear block, red edge/outboard markings, dorsal panel divisions and bronze exhaust openings. The runtime index records even headings only; rigid model tests do not calibrate those sprite headings.

No functional narrative is mapped in the functional text index. Six designer mount coordinates are only 2D evidence. Hidden cross-sections, exact exhaust count/layout, service details and socket transforms remain independent interpretations. The initial assembly includes two visible-style exhausts without asserting the complete original propulsion arrangement. Original pixels and meshes are reference-only and absent from generated inputs.

## Initial assembly

Editable Blend/GLB, four independent hull/red colour/roughness maps, provenance and actual render evidence are under `docs/assets/reconstruction/ships/terran/command-cruiser/`. Seventy-six meshes and five materials form a continuous faceted deck hull, separate rounded bow, raised aft block with rear grille, two outboard wings/probes, red flank/wing bands, twin engine housings, hollow bronze exhaust annuli, recessed dark throats, cooling ribs and framed dorsal service panels/vents.

Two physical dents, analytic stains, grain and seeded scratches implement new-object wear. Small components use rough alloy/soot material values. Bevels precede local box UV assignment; main hull end caps use explicit nondegenerate triangle fans. Separate parameterized hull code preserves all older ship source geometry.

PlacementRoot has local -Y forward. Six tentative hardpoint sockets and two exhaust sockets use local +Z forward and explicit uncalibrated status. No recovered 3D mount or animation mechanism is claimed.

## Verification scope

The verifier reopens native Blender and imports GLB separately. Native physical meshes must be closed with positive volume. Diagnostic-only welding at 1e-6 units accounts for glTF UV/flat-normal seam duplicates and must recover exact native geometric vertex counts. Original meshes are not mutated. Additional checks cover bounds/transforms, packed image byte hashes and decoded colour/roughness pixels, UV projections, two dent depths, common interior contacts between main hull and bow/aft block/collar, engine roots, nozzle roots, wing roots, red flank/outboard bands and dorsal panels. Exhaust axes must remain open ahead of recessed throats. Eight socket positions/axes are tested at four rigid root rotations.

Actual native/imported Blender renders exercise the standalone target runtime. Whole-object framing, intentional engine macros and matched-camera export comparisons are separate from final artistic acceptance. Contact samples provide scoped evidence rather than exhaustive structural proof. Client integration is unchanged.

## Deferred

Exact source bow/block shape, detailed deck panel layout, machinery behind the aft block, exact original engine arrangement, operational/damage variants, calibrated game scale/orientation/mounts and artistic acceptance remain for later passes. No final artistic gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version verification passed in Blender 4.5.15 for 76 meshes and five materials. Nine actual views passed framing/export comparison. Both matched-camera threshold-128 silhouettes are identical; each comparison has one antialiased edge pixel differing by 4/255 alpha. Mean foreground channel differences remain below 1.08/255. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `8582fe2f`. Existing models were not regenerated or refined.
