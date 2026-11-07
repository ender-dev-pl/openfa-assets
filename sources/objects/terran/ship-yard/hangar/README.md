# Layered ship construction and hangar transfer

Issue [#227](https://github.com/ender-dev-pl/openfa-assets/issues/227), dependent on
[#225](https://github.com/ender-dev-pl/openfa-assets/issues/225). This is an authored
extension requested for OpenFA, not a recovered legacy animation.

The unique yard model is `model.glb` with editable `model.blend`. The three unique
ship models are under `sources/objects/terran/{assault-fighter,combat-eagle,scoutship}/construction/`.
The yard contains no ship mesh. Older studies are preserved as source history;
package the selected model once and reuse it across flight, build menu and SciTek.

## Construction layers

Each ship has five cumulative named groups: `Build01_BaseFrame` (progress 0),
`Build02_ExpandedFrame` (0.16), `Build03_Systems` (0.38), `HullPartial` (0.65),
and `HullFinal` (0.88): frame foundation, expanded frame, frame with solid components,
partly fitted skin, and complete skin.
Use actual simulation progress, independently of the demonstration's four-second
build window. During normal flight skip all three Build groups and draw both
HullPartial and HullFinal, the two children of Hull. These disjoint face sets
reconstitute the original hull without overlapping duplicate skin geometry.
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
The `ships[*].source_glb_sha256` values record the payload revisions used when
the yard rig was authored. Later interior-only revisions preserve those envelopes;
their current hashes are bound by `runtime-validation.json` and `showcase.json`.

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

## Production coverage and individual movies

The small ground-yard construction sequence covers Assault Fighter, Combat Eagle
and Scoutship. As clarified by the project owner, Space Dock is constructed in
orbit through the Command Center; it is not a payload for this platform or hatch
and requires no addition to these construction assets. Spy Satellite uses the
separate satellite silo.

An earlier audit incorrectly inferred the physical construction location from
`ship-yard` capability requirements and the absence of `requires-space-dock` in
the current game catalogue. Those fields alone do not establish the original
construction workflow. Any discrepancy in client/catalogue routing is separate
game reconstruction work, not grounds for adding Space Dock to this asset sequence.

Earlier standalone eight-second `construction-stages.webm` / `.mp4` files show the
five verified Blender stage renders with fixed camera/scale and hard visibility
changes. They are historical stage presentations, superseded by the full movies
below. Their original provenance is retained in the historical preview metadata.
Reproduce these earlier presentation videos with
`python sources/tools/blender/encode_ship_construction_previews.py`.

The current yard and individual-ship players select full 3D movies named
`complete-3d-<ship>.mp4` / `.webm` in this yard's media directory. Each is 20 seconds,
480 individually rendered frames at 24 fps. During eight seconds of construction,
successive rigid mesh batches settle into their final positions and the trolley
services the platform. The complete transfer follows: attach, raise, open hatch,
lower onto the receiver, release, return hook/trolley and close the hatch.

Every frame evaluates the canonical GLBs in Blender Eevee. Hoist height and all
three sling directions/lengths are calibrated separately for each ship, with
attachment/contact assertions throughout the suspended part of the cycle. The
preview-only batch placement controller is in `render_complete_shipyard_movies.py`;
it does not change canonical geometry or embed these assembly movements in the
static ship GLBs. Client construction progress and animation binding remain required.
The five structural stages and the complete final hull remain the canonical ones.

`complete-3d-<ship>.json` binds the movie to actual source files and records evaluated
3D state counts. `complete-motion-audit.json` records distinct decoded frames, in
addition to codec/frame-count/duration checks. To reproduce, run this once for each
of `assault-fighter`, `combat-eagle` and `scoutship`, then rebuild the movie index:

```text
blender --background --python sources/tools/blender/render_complete_shipyard_movies.py -- --ship assault-fighter
python sources/tools/blender/index_complete_shipyard_movies.py
```

The earlier eight-second `shipyard-build-<ship>` and isolated `construction-stages`
files are retained as historical static-stage presentations, not full animations.
They are no longer the selected gallery movies. Their original provenance remains
in `yard-build-previews.json` and the historical preview metadata.
