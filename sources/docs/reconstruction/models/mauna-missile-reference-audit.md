# Mauna missile reference audit (#1081)

This milestone establishes source evidence for the first Mauna modelling pass. It adds no authored model and changes no existing reconstruction, refinement or renderer. First missile-source coverage remains 51/69. Relates to #951 and #946.

## Reproducible evidence

Run `python tools/blender/audit_mauna_missile_references.py --check`. The audit binds all ten MAM1-MAM10 definitions, 140 indexed flight/launch frames, original archive-entry hashes, decoded frame hashes, exact BUTTONS RGB palette hashes, transparency index zero and catalogue data. Each frame records its crop, binary occupancy hash and occupied pixels per row. These checks establish reference identity, not a recovered three-dimensional shape or animation mechanism. No management preview is bound. Flight/launch states must not be treated as a turntable.

The ignored comparison at `artifacts/issue-1081-mauna-reference/flight-comparison.png` shows actual frame 3 for all ten definitions. It was visually inspected alongside all fourteen enlarged Minor Hurt Unit states. No original pixels are embedded in tracked deliverables. The general archive/reference proof also passed 69 definitions, 966 frames and 11 independent previews.

## Culture scope

The source-anchored Architecture section is ENGLISH.CDB record 137 at 0x7bea, 661 bytes. Its indexed summary describes rejection of decoration and most comfort, immediate practical purpose, angular concrete mining structures. This directly describes buildings. Blunt functional masses and maintenance detail may inform missile authoring, but literal concrete construction or elimination of observed curved components would be unsupported extrapolation. The cultural index check passed six source-anchored sections.

## Minor Hurt Unit first-model brief

MAM1, global type 51/local type 0. Flight frame 3 has a 6x10 crop with row occupancy `[4,4,6,6,6,6,6,6,4,4]`: narrow four-pixel end sections and a wider six-pixel central section. The visible object is elongated and stepped, unlike the near-circular Artemian family. It is grey with a pale feature on the right in source-screen coordinates. That feature has a longitudinal spine, three transverse pale bars and two dark intervening fields. Those fields may be recesses, shadow, material colour or gaps; the source does not establish through-holes. The handedness of a calibrated three-dimensional mount remains unresolved.

The first independent source should preserve the elongated stepped envelope and asymmetric pale feature. Start with editable blunt central and terminal masses and finite fitted pale detail, then verify actual occupied volumes, joints and any deliberately modelled recesses. Thickness, hidden faces, seams and maintenance fasteners must be labelled authored interpretations. Independent grime/stains/scuffs and small physical dents are required. Do not reuse Artemian spherical geometry simply because its exporter checks already pass.

Catalogue explosive behaviour, ore units 35, budget cost 1 and production investment/updates 2 are confirmed data. The functional-text index establishes its name but no mapped detailed missile narrative. These data do not justify adding a drill, an exposed payload or moving parts.

## Distinctions to preserve in later first studies

The common stepped family silhouette does not make the ten definitions interchangeable. Actual selected frames show: Major Hurt Unit has red terminal/left fields; Burns Unit has dark longitudinal fields; Multiple Burns Unit has red ends and a patterned central face; Multiple Hurt Unit has two red/orange transverse fields; Lightning Destruction Unit has red/ochre ends; Radiation Sickness Unit combines red ends and two red transverse fields; Ground Breaking Unit includes ochre right-side fields; Anti-Ground Breaking Unit has yellow/ochre transverse fields; Ore Dissolver has blue end fields. These are observed colour/layout differences, not confirmed separate mechanisms or materials.

## Open work

The Minor Hurt Unit model, independent texture maps, native Blender reopen, independent GLB import, UV/material/hierarchy/socket checks and actual authored render comparison are still pending. All Mauna artistic acceptance and calibration gates remain open. Refinement and scaffolding stay deferred. This analytical milestone requires no application smoke test. Required changed-code quality base: c72bb6b0.
