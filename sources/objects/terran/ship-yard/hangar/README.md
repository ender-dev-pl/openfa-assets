# Layered ship construction and hangar transfer

Issue [#227](https://github.com/ender-dev-pl/openfa-assets/issues/227), dependent on
[#225](https://github.com/ender-dev-pl/openfa-assets/issues/225). This is an authored
extension requested for OpenFA, not a recovered legacy animation.

The unique yard model is `model.glb` with editable `model.blend`. The three unique
ship models are under `sources/objects/terran/{assault-fighter,combat-eagle,scoutship}/construction/`.
The yard contains no ship mesh. Older studies are preserved as source history;
package the selected model once and reuse it across flight, build menu and SciTek.

## Construction layers

Each ship has cumulative named groups: `Build01_Frame` (progress 0),
`Build02_Systems` (0.25), `Build03_InnerPanels` (0.55), `Hull` (0.82).
Use actual simulation progress, independently of the demonstration's four-second
build window. During normal flight skip all three Build groups and draw Hull only.
Depth occlusion alone still costs draw calls; it does not provide this optimization.
The original hull world vertices and materials are preserved and batched by material.
New internals use the worn yard PBR atlas and are constrained by actual hull sections.

Ship mesh nodes are rigid; no skinning or bone support is required. The normal
static ship GLB has no build animation or zero-scale nodes. Visibility is an explicit
client binding requirement. `ShipLiftSocket` and three `LiftingContact_*` nodes
identify the suspension point and actual upper-skin contacts.

## Yard placement and timing

`model.json` stores all transforms in **yard-local Blender coordinates before the
PlacementRoot 0.3 scale**. The authored yard diameter is 9 local units, corresponding
to the configured 3-by-3 cells of 32 world units. Ship sizes use the game's largest-axis
normalization: Assault Fighter 30, Combat Eagle 32, Scoutship 28. These are a calibration
snapshot, not a promise that later game configuration will remain unchanged.

The square hatch is 3.7 local units / about 39.47 game units wide. Both rigid leaves
rotate down into a genuine through-opening. An underground receiver supports the load
after release. Terrain masking/cutout must hide the exterior underground well; the
gallery's neutral ground is preview-only.

The `Scene` clip is 480 frames at 30 fps. Consult `timeline` in `model.json`; this
export preserves frame-number time: a source frame maps to `frame / 30` seconds.
The clip starts at 1/30 second and ends at 16 seconds.

| Phase | Source frames |
| --- | --- |
| Build-window fixture | 1–120 |
| Crane approach and attachment | 120–150 |
| Raise complete ship | 150–190 |
| Open hatch downward | 195–235 |
| Lower into receiver | 245–330 |
| Release load | 335 |
| Raise hook and return trolley | 340–410 |
| Close hatch | 415–465 |
| Ready | 480 |

Before completion hold the working yard pose and drive ship layer visibility from
the real queue item. Once construction completes, run the transfer portion once;
do not loop it or restart simulation production as a renderer side effect.

The ship instance attaches to `ShipConstructionPlacement` using its `ships[*].matrix`.
The animated empty carries the load without embedding another copy of the hull.
While attached, `LoadAttachment` coincides with the ship's suspension eye.
The exported hoist and three `LoadSling_*` nodes are calibrated to Assault Fighter.
For Eagle/Scoutship, apply the local socket-height difference from the per-ship metadata
to the hoist, adjust cable length correspondingly, and orient/scale each sling from
the eye to its recorded contact. The all-frame verifier checks these height offsets
and envelopes. A generic static-clip player alone cannot select or rig another payload.

## Evidence and previews

`runtime-validation.json` binds native/import verification to exact source hashes.
All three original hulls are compared bidirectionally, and twenty yard poses are
compared against an independent GLB import. Door/well triangles are tested in all
480 frames; all three ship envelopes and attachment continuity are checked through
the complete timeline. The oversized-payload negative control must be rejected.

`showcase.json` binds the playable combined demonstration to the actual independent
GLBs, metadata and renderer source. No combined model is published. The demonstration
is an offline asset fixture, not a client screenshot or gameplay acceptance.
Stage PNGs and ship-specific completed-on-platform renders are linked in the gallery.

Reproduce with Blender 4.5 LTS, in this order:

```text
blender --background --python sources/tools/blender/build_ship_construction_layers.py
blender --background --python sources/tools/blender/build_shipyard_hangar.py
blender --background --python sources/tools/blender/verify_shipyard_construction.py
blender --background --python sources/tools/blender/render_shipyard_construction.py
blender --background --python sources/tools/blender/render_shipyard_construction.py -- --yard-preview-only
```

Client binding, underground terrain integration and GPU/frame-time acceptance remain
the responsibility of game integration. The main game thread receives the commit
and the canonical source hashes before any source pin should be changed.
