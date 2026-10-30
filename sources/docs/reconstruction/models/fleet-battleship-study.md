# Fleet Battleship — first authored iteration (#998)

`openfa:fleet-battleship`, Terran type 6. The authoritative inventory had no registered source model. Existing reconstructions/refined studies are preserved. This pass generates first versions only; further artistic refining remains deferred.

## Evidence and interpretation

`ship-reference-index.json` binds the original paletted PS6C.256 directional sprites and sixty-frame PS06.VID rotation. Frames 0/15/30/45/59 and enlarged comparison views establish the broad curved transverse wing, long forward spine, red upper markings, wingtip projections and large aft/underside engine opening. These are reference-only images and are absent from mesh and texture inputs.

The functional text index has no mapped narrative for this ship. Six ship-designer coordinates are 2D and do not establish recovered 3D hardpoint transforms. Wing/body sections, underside, nozzle interior, mechanical attachments, service collars and socket transforms are independent interpretations.

## First authored assets

`docs/assets/reconstruction/ships/terran/fleet-battleship/` contains editable Blend, standalone GLB, four independent hull/red colour and roughness maps, provenance, technical report and render gallery. The assembly has 35 meshes and five materials. One continuous closed arched wing crosses the central hull. A broad red band follows its crown through the central ridge, with two narrow outboard bands. Small wingtip fairings/probes, four spine collars, bow ring/probe, dorsal cover, central engine housing, hollow bronze exhaust, recessed throat and sixteen cooling ribs complete the first layout.

Two measured dents, analytic stains, grain and seeded scratches supply new-object wear. Smaller components use rough titanium, soot and heat-stained bronze material values. Bevels are applied before local box UV assignment. Wing end caps use explicit triangle fans; the independently authored forebody uses dense elliptical section transitions.

PlacementRoot uses local -Y forward. Six hardpoint sockets and one central engine socket have local +Z forward axes and explicit uncalibrated status. Their presence does not establish game mounting accuracy.

## Technical scope

The verifier reopens native Blender and imports GLB independently. Native parts must be closed with positive volume. Diagnostic-only seam welding at 1e-6 units accounts for glTF UV/flat-normal splits and must recover exactly the native geometric vertex count for each mesh. The imported files remain unchanged. Other checks cover bounds/transforms, packed texture source bytes and decoded colour/roughness pixels, UV projections, two dent depths, common hull/wing and hull/engine interior samples, nozzle roots, open exhaust axis and recessed throat, both tip fairings, bow probe and sampled contact along all three red wing markings. Seven socket positions/axes are checked under four rigid root rotations.

Actual Blender native/imported renders exercise the standalone runtime. Whole-object framing, intentionally cropped engine details and matched-camera export comparisons are checked separately from source visual fidelity. Game renderer/integration is unchanged. Contact samples are scoped correctness evidence, not exhaustive engineering validation.

## Later gaps

Exact source wing curvature and segmented panel layout, marking shapes, service-cover detail, underside construction, calibrated scale/orientation/3D mounts, operational/damage variants and final artistic acceptance remain for later passes. This initial smooth spine and continuous marking layout do not reproduce every original panel or marking subdivision. No final artistic acceptance gate is promoted. Construction scaffolding remains separately deferred under #983.

The native/imported engine macro retains a small shading residual: mean absolute channel differences approximately 2.115/1.720/1.586 out of 255, despite identical alpha and binary silhouettes. The whole view is approximately 0.080/0.081/0.083 out of 255. A persisted corner-normal comparison verifies the actual nozzle normals within 1e-5 (observed maximum about 3.4e-6), and material input checks remain active. The macro is therefore explicitly not pixel-identical; the first-version review retains a 2.5/255 mean-channel bound for this macro, while the full-view bound remains 1.5/255. This scoped residual is recorded for later rendering/finish review rather than described as resolved or used to promote final artistic acceptance.

First-version verification passed in Blender 4.5.15 for 35 meshes, five materials and nine rendered views, with the explicitly recorded engine shading residual above. Both matched-camera alpha channels and threshold-128 silhouettes are identical. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `9865a73e`. Existing models were not regenerated or refined.
