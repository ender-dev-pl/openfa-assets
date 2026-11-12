# Engineering ship proposals - issue #265

Fourteen new authored OpenFA asset proposals: Terraforming Ship and Repair / Construction Assist Ship for seven cultures. These are not recovered legacy units. The selected supplied concepts and their identities are in `concepts.json`.

This directory is deliberately separate from canonical legacy unit catalogues. No unit, blueprint, production route, client package or game mechanic is registered by these files. Model dimensions use provisional proposal units; production and hangar clearance need a separate future integration decision.

Each completed model has editable named tool pivots, authored material maps, a looping four-second `ToolOperation` animation, a Blend source and GLB export. Normal flight can keep the tools in their first-frame pose; the clip demonstrates articulation only. No behaviour is automatically enabled in OpenFA.

The runtime verifier opens the saved Blend and independently imports GLB, checks closed geometry and a physical support graph at six animation poses, compares animated surfaces and texture pixels, verifies a single exported clip, and renders both playback paths. This does not certify swept collision avoidance between every pair of intermediate frames or establish gameplay acceptance.

Run author scripts with Blender and `--root` pointing to this asset repository. Run `verify_engineering_refinement.py -- --culture <culture> --role terraform|repair`. Publish encoded previews with `publish_engineering_proposals.py`; it requires FFmpeg and FFprobe. These asset-specific scripts and resulting assets have the asset license specified by the repository licensing policy.

The dedicated [proposal gallery](../../../gallery/engineering-proposals.html) shows only models with current runtime evidence. Concepts without a finished model remain proposals, not completed assets. Older concept iterations remain in the private evidence workspace.

## Delivered tool articulation

All fourteen proposals contain one looping `ToolOperation` clip, authored at 24 fps over frames 1-97 (four seconds). The lightweight gallery videos sample playback at 6 fps; the GLB contains continuously interpolated animation. First/last poses match. Tool pivots are named editable nodes; engines and hulls remain stationary.

| Culture | Terraforming Ship | Repair / Construction Assist Ship |
| --- | --- | --- |
| Terran | Continuous horizontal milling drum rotation | Shoulders/elbows on both arms and independently closing clamp jaws |
| Rigellian | Two pivoted copper-ended precision horns | Shoulder/elbow chains and independently closing clamp jaws |
| Braccatian | Opposing hinged crusher jaws | Rooted positioning yoke and two independent fingers |
| Mikotaj | Hinged working plates on the open frame | Tilting clamp support and two closing fingers |
| Artemian | Two direct sliding wedge tools | Separate sliders, a wrist and two independent clamp jaws |
| Mauna | Pivoted grading blade with mounting blocks | Separate slides, independent clamp jaws and a service-head wrist |
| Achaean | Ventral silver-edged crescent grading tool | Curved lower support, a wrist and two independent claws |

`verify_engineering_delivery.py` validates all fourteen source/export hashes, selected concepts, material maps, runtime and visual reviews, clip channels, preview hashes and gallery links. Pass `--base <commit>` to additionally check that canonical/runtime catalogues have not changed from that revision. Artistic user acceptance and future gameplay integration remain separate decisions.

## Revision 2 refinement

Refinement retains defined hull planes, clipped corners and structural breaks. Curved surfaces are reserved for the culturally established shell forms, bearings, nozzles and genuinely curved tools. Material definition and mechanical detail must not turn angular housings into pill-shaped shells or add dense decorative panel grids.

The current refinement uses authored colour, packed roughness/metallic and tangent-space normal maps, including sparse scuffs and shallow dent shading. Maps are embedded in GLB. Named joints, tool motions and proposal-only integration status are preserved. Geometry has a 40,000-triangle guard per ship; this is an authoring bound, not a measured game performance guarantee. Runtime draw calls, texture sharing and platform profiling remain future integration work.

The delivery audit additionally pins the refinement helper, verifies GLB PBR channels and actual native/imported per-material image assignments, and binds the before/refined/concept comparison to the current GLB. During refinement, pass `--cultures <name> ...` to verify a completed subset; the default requires all fourteen revision-2 models. Original revision-1 sources and exports remain in Git history, without duplicate model payloads in the catalogue.

### Achaean repair wing correction

The repair ship uses two mirrored longitudinal red/silver wings with matching roots and bosses. This user-requested correction supersedes the selected concept's asymmetric overhead/side arches; the original concept is retained as provenance rather than edited to imply it already contained the correction. The ventral articulated service tool remains functionally asymmetric. `verify_achaean_engineering_symmetry.py` checks both native and imported wing surfaces at five animation poses and rejects a deliberately distorted wing; its source-bound result is `achaean/repair/wing-symmetry-review.json`.

## Canonical-fleet style refinement

The canonical-fleet pass has an author visual review for all fourteen models. The
[whole-fleet review](canonical-style-review.json) binds current sources, exports,
runtime/animation evidence, comparison images and per-model cycle histories. The
[overview image](../../../gallery/media/proposals/engineering-ships/canonical-style-overview.png)
and the [comparison gallery](../../../gallery/engineering-proposals.html#style-comparison)
show engineering proposals beside the current canonical fleet in the same review
studio. Display fitting is independent and does not establish game scale.

| Culture | Terraforming attempts | Repair attempts |
| --- | ---: | ---: |
| Terran | 2 | 2 |
| Rigellian | 1 | 1 |
| Braccatian | 3 | 3 |
| Mikotaj | 3 | 3 |
| Artemian | 2 | 2 |
| Mauna | 3 | 2 |
| Achaean | 2 | 2 |

Failed attempts remain in the histories. Mauna repair's second actual export uses
shared author revision 3; revision 2 stopped before exporting that role. Mikotaj's
final same-studio canonical reference renders reuse its existing engineering
models and consume no additional generator attempt.

Follow the [refinement protocol](../../../docs/workflow.md#engineering-ship-refinement-against-the-canonical-fleet)
for subsequent work. A fourth generator cycle requires a new user decision.
Artistic user acceptance, physical game scale, platform profiling, continuous swept
clearance and gameplay integration remain separate from this asset review.
