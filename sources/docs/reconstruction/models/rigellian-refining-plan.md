# Rigellian refining programme

Tracked in [asset issue #185](https://github.com/ender-dev-pl/openfa-assets/issues/185).
Baseline: `9ed4dfd6bcabd6b367443ac3225dd501645ee7a4`. Scope is all 35 registered
Rigellian definitions: 23 buildings, five ships and seven missiles. Earlier
studies remain available. New studies require source-bound native Blender and
independent GLB verification and actual rendered inspection before registration.

User clarification: prioritize missing visible components and a general increase
in detail/fidelity, not imperceptible micro-details. Evaluate additions at normal
gallery/game presentation sizes: recognizable mechanisms, ribs, body divisions,
covers, fittings and coherent structural assemblies take priority over tiny
scratches, fasteners or numerically detectable surface defects. Materials,
shapes and design choices must also respect the complete relevant Colony
Database culture entry, not just a generic science-fiction style.

## Evidence and review limits

`tools/prepare_rigellian_refining_references.py` checks archived payload hashes
against the existing reference indices, decodes the embedded building/ship VGA
palettes and binds missiles to the actual BUTTONS palette. It decodes all 943
building catalogue frames and all building surface descriptors, 130 ship frames
and 98 missile frames. Original pixels and comparisons stay in ignored
`artifacts/issue-185/references/`; they are not deliverables or textures.

The baseline review inspected building surface bodies and readable catalogue
phase 20 alongside current front-quarter and side renders, selected directional
ship views, both Observatory states, and missile flight frames 0 and 6. Decoding
a frame is not evidence of visual inspection. Remaining headings, highlighted
phases and mechanism states require focused review as each model is refined.
The alien catalogue clips show reveal/highlight presentation, not recovered
turntable views. RI19 and RI23 surface bodies require separate turret layers;
RI22 has an empty static body descriptor. Do not treat those bodies as complete
assemblies or confuse a rendered open RI18 surface with its closed state.

All 23 functional narratives were read from the indexed original ENGLISH.TXT
byte spans and verified against their SHA-256 values. Ships and missiles have
catalogue names/roles/effects but no established descriptive narratives. The
Rigellian Architecture article was read from ENGLISH.CDB record 18, bytes
2417–3185: integrated ergonomic and elegant facilities, including mining, with
research central to colony life. This does not establish arbitrary hidden
mechanisms, a universal metal or a mandatory curved form.

Sci-Tek animations must be consulted where a relevant research binding exists.
Their subject and depicted culture must be established before using a diagram
as shape evidence. Generic Terran equipment diagrams do not override Rigellian
sprites. Construction scaffolds, damage states and calibrated game integration
are separate from this refinement pass.

## Baseline decisions

These are review targets, not completed changes. Dimensions and hidden surfaces
remain authored interpretation unless additional evidence establishes them.

| Model | Evidence-led refinement target / constraint |
| --- | --- |
| RI01 Central Unit | Gold crown currently reads as thin bent wire; original has broader tapered lower arms. Retain open roof well and actual neck grille; review saucer/waist ratios. |
| RI02 Filtration Plant | Retain six gold ports and true lower slots; review shoulder steps, tall side channel, upper collar and port depth against highlighted phases. |
| RI03 Nourishment Bank | Review stacked vessel elongation and vertical service faces; broad round modules currently dominate slender source silhouette. Preserve three-module stack. |
| RI04 Community | Correct gold crown arms and central stem; review two-body waist and lower red grille against source. |
| RI05 Health Unit | Correct gold crown arms; retain two distinct upper grille faces and flared foundation; review roof and neck transitions. |
| RI06 Strategic Bunker | Correct gold crown arms; retain three saucers and their roof wells; review tall stepped spindle proportions. |
| RI07 Science Labs | Silver open crown is source-supported; review stepped spindle and lower bell, rather than imposing the gold crown shape. |
| RI08 Databanks | Preserve twin mast rods and side housing; review upper perforated body and the relative sizes of saucer/lower body. |
| RI09 Construction Unit | Preserve open paired wells. Review visible lower rim ribs and upright/well contacts; no invented door motion. |
| RI10 Ground Deck | Preserve authored door pivots, open shaft, exported states and animation. Review buttress thickness and surface panels in closed/open comparisons. |
| RI11 Probe Launch | Retain open port and flat internal guides. Reassess collar/shoulder proportions and front fitting; dark left patch may be cast shadow, not a second opening. |
| RI12 Deep Space Probes | Review stepped tip, red centre housing and exposed copper neck lengths; retain slender coaxial construction. |
| RI13 Gravitic Converter | Preserve sphere/supports and real central grille; review side supports and lower-module proportions. |
| RI14 Energy Gatherer | Compare crown bowl profile/prongs, gold body divisions and vertical pale rail; power-generation internals are unknown. |
| RI15 Energy Globe | Retain sphere, neck and green service face; refine ring/face integration and lower foot proportions. |
| RI16 Shield Generator | Review golden top curvature and three globes/legs; preserve real gaps between mast supports. |
| RI17 Arms Unit | Source crown has lateral gold arms, currently absent from model's single spike. Review open well, front column and lower rim ribs. |
| RI18 Missile Launcher | Preserve the verified sideways dome halves and pivots. Review stepped shell/gold foundation using matching open and closed states. |
| RI19 Thermal Lance | Review assembled directional layers, tapered barrel and short pivot housing; do not infer body shape from base alone. |
| RI20 Extractor | Review source's pronounced lower shoulder, ribbed lower mechanism, side step and gold inset regions; current body reads as a smooth capsule. |
| RI21 Storage racks | Retain five visible gold pods and pale rack; review pod profile, central neck and green face proportions. |
| RI22 Ex-Fang | Review assembled directional dish/support angles and source's thin dish silhouette; static body descriptor is empty. |
| RI23 Ultrathermal Lance | Retain paired gold emitters and asymmetric side projection; review actual turret layers before adjusting spacing or inclination. |
| Lazzaro Research | Tiny 14×9 sprites support lateral lobes; current thin rectangular plates need review against all headings. Hidden sections remain uncertain. |
| Delphini Assault | Review forebody taper, narrow nose projection and separate copper lower/lateral masses; avoid generic gold rectangles as substitutes. |
| Messier-Lukannon | Review flattened hull/ventral masses and copper termination; current large pointed side plates are an interpretation requiring correction where headings support it. |
| Transportation | Compare both rounded inline masses and narrow join across headings; retain broader blue forward mass and greener rear mass. |
| Observatory | Source has a substantial lit equatorial equipment belt and slender upper/lower fins. Current plain saucer understates belt. Second wireframe-like state is unresolved, not proven deployment motion. |
| Detonator | Review fork taper/spread and blue centre face; retain green body and gold/red nose. No solid exhaust. |
| Multi-det | Review fork taper/spread and gold central insert; preserve distinct nose colour bands. |
| Flamejell | Review open fork taper and broad segmented blue centre; retain green nose and pale forward bands. |
| Maxi-det | Review fork taper, gold centre and wide forward collar/side tips; distinguish effect pixels from structure. |
| Flare | Review taper of gold-edged fork and two blue centre regions; retain short gold tip. |
| Viral Repair | Review open fork taper and pale-banded body; preserve red tip. No new inferred repair mechanism. |
| Temporal Stasis | Review gold-edged fork taper and red centre panel; preserve green forward body and gold end. No inferred stasis mechanism. |

## Completion contract

Each per-model result must state the observed improvement, remaining inference,
preserved earlier source hashes, actual geometric checks and rendered native/GLB
comparison. An unchanged model can be retained after focused review with a
reasoned evidence record; it must not be counted as newly refined. Animated
studies need gallery WebM previews from their actual exported GLB clips. Final
artistic acceptance stays open for user review. Notify the authorized integration
chat of committed model updates and exact source paths; do not edit its checkout.
