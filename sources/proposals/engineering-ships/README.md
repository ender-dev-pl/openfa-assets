# Engineering ship proposals Ă˘â‚¬â€ť issue #265

Fourteen new authored OpenFA asset proposals: Terraforming Ship and Repair / Construction Assist Ship for seven cultures. These are not recovered legacy units. The selected supplied concepts and their identities are in `concepts.json`.

This directory is deliberately separate from canonical legacy unit catalogues. No unit, blueprint, production route, client package or game mechanic is registered by these files. Model dimensions use provisional proposal units; production and hangar clearance need a separate future integration decision.

Each completed model has editable named tool pivots, authored material maps, a looping four-second `ToolOperation` animation, a Blend source and GLB export. Normal flight can keep the tools in their first-frame pose; the clip demonstrates articulation only. No behaviour is automatically enabled in OpenFA.

The runtime verifier opens the saved Blend and independently imports GLB, checks closed geometry and a physical support graph at six animation poses, compares animated surfaces and texture pixels, verifies a single exported clip, and renders both playback paths. This does not certify swept collision avoidance between every pair of intermediate frames or establish gameplay acceptance.

Run author scripts with Blender and `--root` pointing to this asset repository. Run `verify_engineering_refinement.py -- --culture <culture> --role terraform|repair`. Publish encoded previews with `publish_engineering_proposals.py`; it requires FFmpeg and FFprobe. These asset-specific scripts and resulting assets have the asset license specified by the repository licensing policy.

The dedicated [proposal gallery](../../../gallery/engineering-proposals.html) shows only models with current runtime evidence. Concepts without a finished model remain proposals, not completed assets. Older concept iterations remain in the private evidence workspace.

## Delivered tool articulation

All fourteen proposals contain one looping `ToolOperation` clip, authored at 24 fps over frames 1Ă˘â‚¬â€ś97 (four seconds). The lightweight gallery videos sample playback at 6 fps; the GLB contains continuously interpolated animation. First/last poses match. Tool pivots are named editable nodes; engines and hulls remain stationary.

| Culture | Terraforming Ship | Repair / Construction Assist Ship |
| --- | --- | --- |
| Terran | Continuous horizontal milling drum rotation | Independent shoulder/elbow motion on both arms |
| Rigellian | Two pivoted copper-ended precision horns | Separate shoulder/elbow tool chains |
| Braccatian | Opposing hinged crusher jaws | Single rooted ventral service yoke |
| Mikotaj | Hinged working plates on the open frame | Tilting clamp support and two closing fingers |
| Artemian | Two direct sliding wedge tools | Separate sliding gripper and service blade |
| Mauna | Pivoted grading blade with mounting blocks | Separate short clamp and service-head slides |
| Achaean | Ventral silver-edged crescent grading tool | Curved lower support about the side bearing |

`verify_engineering_delivery.py` validates all fourteen source/export hashes, selected concepts, material maps, runtime and visual reviews, clip channels, preview hashes and gallery links. Pass `--base <commit>` to additionally check that canonical/runtime catalogues have not changed from that revision. Artistic user acceptance and future gameplay integration remain separate decisions.

## Revision 2 refinement

Refinement retains defined hull planes, clipped corners and structural breaks. Curved surfaces are reserved for the culturally established shell forms, bearings, nozzles and genuinely curved tools. Material definition and mechanical detail must not turn angular housings into pill-shaped shells or add dense decorative panel grids.

The current refinement uses authored colour, packed roughness/metallic and tangent-space normal maps, including sparse scuffs and shallow dent shading. Maps are embedded in GLB. Named joints, tool motions and proposal-only integration status are preserved. Geometry has a 40,000-triangle guard per ship; this is an authoring bound, not a measured game performance guarantee. Runtime draw calls, texture sharing and platform profiling remain future integration work.

The delivery audit additionally pins the refinement helper, verifies GLB PBR channels and actual native/imported per-material image assignments, and binds the before/refined/concept comparison to the current GLB. During refinement, pass `--cultures <name> ...` to verify a completed subset; the default requires all fourteen revision-2 models. Original revision-1 sources and exports remain in Git history, without duplicate model payloads in the catalogue.

### Achaean repair wing correction

The repair ship uses two mirrored longitudinal red/silver wings with matching roots and bosses. This user-requested correction supersedes the selected concept's asymmetric overhead/side arches; the original concept is retained as provenance rather than edited to imply it already contained the correction. The ventral articulated service tool remains functionally asymmetric. `verify_achaean_engineering_symmetry.py` checks both native and imported wing surfaces at five animation poses and rejects a deliberately distorted wing; its source-bound result is `achaean/repair/wing-symmetry-review.json`.

## Canonical-fleet style refinement

The next refinement uses at most three generator-correction / actual GLB render / visual comparison cycles per model. Follow the [canonical-fleet refinement protocol](../../../../docs/workflow.md#engineering-ship-refinement-against-the-canonical-fleet); the current comparison is `gallery/engineering-style-comparison.json`. Preserve the actual cycle history and unresolved findings. A fourth cycle requires a new user decision; technical checks alone do not establish style agreement.
