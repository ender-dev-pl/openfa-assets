# Rigellian retained-model review (#185)

This review covers the thirteen remaining building decisions in the full
35-model pass. They are retained studies, not thirteen newly refined models.
The separate twenty-two new studies contain the visible geometry/material
improvements described in the crown, structural and missile refinement notes.
The machine-readable per-model reasons and source hashes are in
`rigellian-retained-review.json`.

## Evidence and decisions

All 41 paletted catalogue phases for each of these buildings were inspected,
together with surface parts and fresh native/independent GLB renders. Catalogue
phases reveal/highlight a fixed presentation; they are not rotational views.
RI10 and RI18 base/cover activity layers and all sixteen RI19 heads were
composed using their original descriptor offsets. RI22 has sixteen complete
directional sprites and an empty body descriptor; its parts were not treated
as independent floating overlays.

| Models | Reason to retain the current major construction |
| --- | --- |
| RI02 Filtration Plant | Six gold ports, real lower slots, tall side channel and stepped shoulder are already present. |
| RI07 Science Labs | Slender stepped spindle, silver open fork, wells and flared lower bell match the source's distinct construction. |
| RI09 Construction Unit | Paired open wells, uprights and lower rim slots account for the visible equipment. |
| RI10 Ground Deck | Bronze buttresses, panels, two covers and open shaft are present; the existing clip remains usable. |
| RI11 Probe Launch | Open port, flat internal guides, flared collar and front fitting are present. The dark left patch does not establish another hole. |
| RI12 Deep Space Probes | Stepped tip, red middle, copper neck and slender coaxial pole/foot are present. |
| RI13 Gravitic Converter | Sphere, supports, actual grille, fittings and lower spindle preserve the source's broad divisions and gaps. |
| RI15 Energy Globe | Segmented sphere, green service face, ring, neck and foot already describe the visible assembly. |
| RI16 Shield Generator | Three globes/feet, separated mast supports and curved golden upper spindle are present. |
| RI18 Missile Launcher | Stepped shell, segmented bronze foundation, rungs and side rod remain; the two dome halves open sideways. |
| RI19 Thermal Lance | Composed headings support the tapered barrel, short rounded pivot, fittings and pedestal. |
| RI21 Storage racks | Five gold/bronze pods, green faces and pale rack reproduce the main source arrangement. |
| RI22 Ex-Fang | Directional views explain the dish's thin-edge/full-circle change. The quarter-view oval does not justify changing its physical inclination. |

These decisions avoid adding detail for its own sake. Exact dimensions, hidden
surfaces, dish concavity and mechanical calibration remain authored where the
source cannot resolve them. They are review decisions, not a claim of final
artistic acceptance.

## Actual runtime revalidation

The current inventory's exact Blend/GLB pair for each model was copied to an
isolated evidence workspace. Its unchanged source-specific validator ran in
Blender 4.5.15, producing fresh technical reports and renders. Original assertion
bodies and tolerances were not altered. All canonical source/material inputs
were hashed before and after and remain unchanged. New review media and reports
are published separately under
`gallery/media/docs/assets/reconstruction/rigellian-refining-review/riXX/`;
old accepted reports and models are preserved.

The RI10 validator checks all 61 authored poses, shaft clearance and native/GLB
state correspondence. Fresh imported closed/half/open and open-top renders were
inspected. RI18 was separately reopened/imported at frames 1, 16, 31, 46 and 61;
its original validator checks the closed cycle, population/vertex correspondence
and nine clear-aperture rays. Fresh native/imported closed/half/open renders were
inspected. RI19/RI22 retain their actual tested yaw hierarchy and stationary
bases; a yaw rig is not converted into an unsupported idle or firing animation.

RI18 was generated before the shared launch generator/recipe grew to cover
other facilities. Its original generation hashes therefore differ from the
current shared files. The new report records both identities explicitly and
states that no generator was executed. Retention evidence is the actual check
of unchanged model bytes, source chain, geometry and animated states; the old
generation metadata was not rewritten to imply new provenance.

Source-specific technical checks are not universal pixel-parity claims. Fresh
native/imported images were visually compared; their original validator camera
setups can differ. Quantitative matched-camera silhouette/RGB results for the
twenty-two newly refined studies remain in their separate validation reports.

## CDB and Sci-Tek

The complete Rigellian CDB entry and cross-culture mentions were read, with
original byte spans and hashes recorded in `rigellian-lore-evidence.json`.
Elegant, ergonomic, research-centred architecture supports integrated equipment;
it does not prescribe an alloy, an all-curved style, a hidden reactor or a new
operating mechanism. Green, bronze/gold and pale structural regions follow the
actual graphics. Building functional narratives were also read and hash checked.

All 36 research preview/information-film bindings were resolved from the actual
catalogue. Their preview subjects use PB/PH/PM/ST entries; none directly binds an
RI model. Every information film was decoded with the original FRAGILE.EXE
codec, including `Same` chunks that repeat the previous image. The ledger records
the actual variable update/timeline counts rather than treating repeated images
as missing frames. No game process or DOSBox was launched.

Three motion samples per film were inspected for subject identification. Ten
potentially relevant generic upgrades were then reviewed at eighteen spaced
updates spanning their motion: ST00, ST01, ST06, ST07, ST11, ST14, ST20, ST21,
ST23 and ST31. Their rotating/zooming highlighted diagrams provide context for
equipment on other/generic subjects, not proof of Rigellian shape, attachment
or operational motion. ST07 includes its own articulated construction equipment;
it is not a replacement for RI09 evidence. Exact reviewed update indices,
bindings and hashes are in `rigellian-scitek-review.json`. This is sampled
inspection, not a claim that every image of every film was viewed.

Original decoded images and private comparison sheets remain in ignored
`artifacts/`. No original pixels were added to source textures or gallery media.
Client integration, construction scaffolds, damage states and final artistic
acceptance remain separate. The subsequent all-35 source/gallery audit and
overall pass result are recorded in `rigellian-refining-completion.md`.
