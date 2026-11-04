# Space Dock — first authored iteration (#999)

`openfa:space-dock`, Terran type 7. The authoritative inventory registered no source model. Existing reconstructions/refinements are preserved; this pass creates first versions only, with artistic refining deferred.

## Reference scope

`ship-reference-index.json` binds correctly paletted PS7C.256. It contains two fixed sprites, not a heading bank or a rotation video. Frame 0 shows a pyramidal upper body, long tapering lower hull, equatorial edge, antenna structures and lateral attachments. Frame 1 appears wireframe-like; its exact operational/state semantics is unresolved. It is not treated as a second camera view or used to infer hidden dimensions. Both actual paletted sprites were inspected and retained only in ignored reference evidence.

The functional text index has no mapped narrative. Four designer mount coordinates establish only a 2D arrangement. The four-arm radial layout, unseen faces, cross-sections, maintenance slots and 3D socket transforms are independent interpretations. No legacy image or mesh is used as a geometry or texture input.

## First assembly

`docs/assets/reconstruction/ships/terran/space-dock/` contains editable Blend/GLB, four independent hull/red colour and roughness maps, provenance, reports and actual render views. Thirty-nine meshes and five materials include separately editable upper/lower closed octagonal hulls, an equatorial rim, four radial arms with berth pods and diagonal supports, pod insets/markers, central/auxiliary antennas, a lower sensor, two fitted roof markings and three lower service slots with fasteners.

Two measured geometric dents, analytic stains, grain and seeded scratches implement new-object wear. Small parts use rough titanium, dark joint and bronze material values. Applied bevels precede box UV assignment. Octagonal hulls have subdivided planar faces and explicit triangle-fan end caps.

PlacementRoot uses local +Z as the station's authored axis. Four tentative equipment sockets use local +Z forward axes and remain explicitly uncalibrated. Their existence does not recover the legacy mounting geometry.

## Verification scope

Native Blender is reopened and GLB imported independently. Every native physical mesh must be closed with positive volume. Diagnostic-only welding at 1e-6 units accounts for imported UV/flat-normal seam splits; the result must be closed and have exactly the native geometric vertex count per object. Original files are not mutated. Checks also cover transforms/bounds, packed source image bytes and decoded colour/roughness pixels, UV projections, two dent depths, shared interior contacts for upper/lower hulls, rim, arms, braces, pods/insets, antenna/sensor roots and roof markings. Four socket positions/axes are tested at four rigid root rotations, without claiming that the fixed legacy sprite actually rotates.

Actual native/imported Blender renders exercise the standalone target runtime. Full-object framing, intentional dock-detail crops and matched-camera export comparisons are separate from artistic acceptance. Client renderer/integration is unchanged. Sampled contacts are scoped evidence rather than exhaustive structural proof.

## Deferred

Exact hidden body shape, asymmetric source attachments and markings, original material/panel detail, calibrated game scale/orientation/mounts, wireframe-like/state variant semantics and final artistic acceptance remain for later passes. The first octagonal layout does not establish how many operational berths the original has. No final artistic gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for 39 meshes and five materials. Nine actual rendered views passed framing and export comparison. Both matched-camera alpha channels and threshold-128 silhouettes are identical; foreground mean colour differences remain below 0.35/255 per channel. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `ba54e4de`. No existing model was regenerated or refined.
