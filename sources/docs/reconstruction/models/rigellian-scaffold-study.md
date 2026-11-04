# RIS2 modular scaffolding prototype (#983)

This is an independently authored editable prototype for the Rigellian 2x2 scaffold family, shared by twelve building definitions including RI11. It demonstrates stacking and is not a completed high-detail reconstruction or game integration. Function is scaffolding erected during construction, not a scaled unfinished final building.

## References and physical interpretation

RIS2 source descriptors 1/2 are 44x29 and 44x33 with offsets (138,83)/(138,79). They show green uprights, copper/brass ties and structure inside the footprint; descriptor zero is a separate perimeter-like mask. Original pixels remain reference-only under `artifacts/shared-construction-reference-study/RIS2/`. Geometry and materials are authored without sampling them.

The repeat relation is recovered separately in `scaffold-stacking-analysis.md`: a two-stage alien descriptor repeats eight screen pixels upward at full scale. The prototype's physical pitch is provisional: `8/44 * (1.8*sqrt(2))/sqrt(2/3)`, approximately 0.567. This uses a 1.8-square outer envelope, diagonal orthographic view at elevation atan(1/sqrt(2)) and the source width. It is a projection-consistent modelling hypothesis, not a recovered world-coordinate constant or final runtime calibration.

There are 24 perimeter and nine interior uprights, hollow square metal sections, copper ties, ground feet and hollow joining sleeves. Exact lattice count, profiles, joint design, hidden geometry and material finish remain inferred. Analytic independently authored colour/roughness maps add oxidation, grease and scuffs.

## Actual refinement

The first render contained only perimeter framing. Comparison with the source showed missing internal structure, so a nine-upright interior lattice and cross ties were added. Solid square bars and sleeves were replaced by hollow sections. GLB extras were enabled after reimport exposed missing stage metadata. Crossing ties initially had coincident top surfaces; staggered overlapping lap joints remove that artifact. Collinear segmented ties were replaced with continuous rails to remove coplanar overlapping end surfaces. These are actual rendered refinements, not polygon-count acceptance.

## Explicit states and joints

The initial revision had four standalone cases with total stages 1,2,3,6 and frame chains `[1]`, `[2]`, `[2,1]`, `[2,2,2]`. Stages 3/6 are synthetic stack tests, not claims about RI11's resource-derived stage ceiling. Each case has its own editable Blend and standalone GLB. Tier roots carry frame values and have BottomSocket/TopSocket empties separated by nominal pitch. A partial tier's TopSocket is its nominal completed attachment location; a subsequent tier may only attach after frame 2.

Lower complete tiers are translated by whole pitches, not stretched. Upright ends meet at exact tier boundaries and hollow copper sleeves overlap both adjoining uprights. Ground feet occur once across the entire assembly. There are no repeated foundations or closed end caps. The prototype has open tube ends and intentionally does not add a universal roof closure unsupported by RIS2 evidence.

## Verification scope

The verifier reopens every native Blend and imports every standalone GLB. It checks mesh topology/positive volume, evaluated per-object bounds, every parent and world matrix, preserved root/tier metadata, sockets, upright endpoint continuity, sleeve overlap across joints, single ground-foot set, footprint, packed image pixels and quantized materials. Imported renders use the exact saved native camera. Whole-object front/rear/imported framing and native/imported silhouette/alpha/pixel checks are recorded separately. Bounds and sleeve tests are not an exhaustive collision proof.

The manifest and technical/render reports bind source/export hashes. The main 303-definition inventory registers this study at the family level and exposes it on its twelve dependent buildings; it verifies native/export/render files and authoring-source evidence rather than promoting a final acceptance gate. The source reference index remains source evidence; available prototype studies are tracked in programme.json.

## Outstanding

Recover the actual resource ceiling and original ownership-based family selection. Calibrate physical pitch/orientation/origin in the target surface projection. Refine ties, relative upright density, finish and source silhouette; verify joints from additional headings and at supported scales. Investigate ARS2 before generalising closed/clad scaffold shapes. Add application presentation state and completion cleanup only with corresponding simulation/presenter design, runtime tests and required publication-ready colony setup. No game logic or renderer changed in this milestone.

Deliverables: `docs/assets/reconstruction/scaffolds/rigellian/size-2/`; reference-only comparison: `artifacts/shared-construction-reference-study/RIS2/authored-comparison.png`.

## Actual required range identified after the prototype

The original definition-byte ceiling is now indexed for all buildings. RI11's limit is two stages (one tier), but RIS2 Databanks reaches stage 17 (eight full tiers plus one partial). The stage-6 prototype does not yet cover the required family maximum. See `scaffold-stage-limits-study.md`; source discovery does not calibrate physical pitch or accept this model.

## Revision 2 — full required RIS2 stage range

The exported range is now derived directly from the RIS2 maximum in `scaffold-stage-limits.json`: every stage 1..17 has an editable native source and standalone GLB. Stage 16 has eight complete tiers; stage 17 has eight complete tiers and a half-height ninth. These are required family boundary cases, not a claim that RI11 itself stacks. The source limit index and maximum stage/tier values are bound in model metadata and rechecked against original-data requirements by the catalogue verifier.

Repeated tube/rail/foot geometry is evaluated with its bevels and normals once per identical template and reused as linked mesh data. The sharing key includes raw local vertices, polygon/material/smoothing assignments, UV layers and controlled authoring modifier settings. All node transforms and stage/socket metadata remain independent and editable. Native and imported unique-mesh counts plus the glTF mesh table are checked, so export cannot silently expand the instances. This changes storage representation, not the intended scaffold geometry or stage semantics.

The overview gallery now shows all seventeen stages. Every stage retains separate 900x900 front/rear native views and a matching imported front view. The render reviewer also constructs reference-only diagnostic stacks from the original descriptors and their original offsets, using the recovered eight-pixel per-tier displacement. Both lower-first and upper-first composites are retained because the original composition order has not been verified here. A six-row comparison highlights stages 1,2,3,6,16,17. Normalized body height/width differences are reported independently of the 3D pitch; these extent measurements are not pixel-mask fidelity or final runtime calibration.

Full-range export and technical checks do not settle source silhouette details, exact joint engineering, final wear/material quality or game integration. The physical pitch remains provisional, and no final acceptance gate is promoted.

Two additional regression tests assert that the prototype exports every source-required stage and that the GLB mesh table reuses geometry while retaining all mesh-bearing nodes. Together with the six original-data limit tests and eight arithmetic tests, these guard both the input range and the representation of repeated pieces. The stage-17 assembly contains 764 mesh objects but six shared mesh templates; source/import inspection still checks every object's transform and attachments.

Revision-2 verification results: all 17 native/imported cases and 51 framed views passed. Maximum native/imported RGB channel mean difference is about 0.085/255; alpha matches exactly in every case. Across the diagnostic body-stack extent comparison, the largest normalized height error is about 0.345 pixel at source width 44 (stage 16). This demonstrates the chosen repeat relation in this diagonal view, not source pixel-mask fidelity.

Visual review of the six-row stack comparison also exposes remaining art work: the source reads as denser, darker framing than the current open lattice. Exact vertical tie/cladding interpretation and finish need refinement after composition order is resolved. Neither the close extent match nor successful instancing accepts that appearance difference.

## Body order evidence follow-up

Original-instruction fixtures now establish bottom-to-top body callback dispatch for nonwrapping positive priorities through eleven levels. The lower-first comparison is the supported body order; reverse order is a diagnostic contrast. See `scaffold-composition-study.md` and `scaffold-composition-evidence.json`. The complete pixel compositor (including palette/shadow effects) remains unverified. New alpha-occupancy diagnostics expose the outstanding structural-density difference explicitly: approximately 64% source versus 47% authored at stage 2 and 87% versus 72% at stage 17. No model geometry changed or acceptance gate advanced in this analytical update.
