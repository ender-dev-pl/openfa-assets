# Achaean building remaster: preservation baseline

Tracking: openfa-assets #256; relates to #9 and #7. This is the initial inspection milestone, not completed model delivery. The dedicated branch is based on the committed Rigellian programme (#253 / PR #254) to reuse its current authoring and gallery infrastructure; that PR was still open when this branch was created. No additional checkout was created.

## Scope and existing sources

| Key | Definition | Building | Footprint | Existing native / GLB triangles |
| --- | --- | --- | --- | ---: |
| AC01 | 151 | Footprint | 3 x 3 | 7,528 / 7,528 (silhouette-study) |
| AC02 | 152 | Anti-Rad Screen | 2 x 2 | 9,352 / 9,352 (silhouette-study) |
| AC03 | 153 | Environmental Control | 2 x 2 | 5,548 / 5,548 (silhouette-study) |
| AC04 | 154 | Filtration Vats | 2 x 2 | 6,332 / 6,332 (silhouette-study) |
| AC05 | 155 | Nutrient Vats | 2 x 2 | 7,628 / 7,628 (silhouette-study) |
| AC06 | 156 | Habitat | 2 x 2 | 12,572 / 12,572 (silhouette-study) |
| AC07 | 157 | Pharmacopeion | 3 x 3 | 8,824 / 8,824 (silhouette-study) |
| AC08 | 158 | Gathering Ground | 3 x 3 | 9,608 / 9,608 (silhouette-study) |
| AC09 | 159 | Market | 3 x 3 | 11,788 / 11,788 (silhouette-study) |
| AC10 | 160 | Communications Central | 3 x 3 | 7,528 / 7,528 (silhouette-study) |
| AC11 | 161 | Shipyard | 3 x 3 | 9,352 / 9,352 (silhouette-study) |
| AC12 | 162 | Landing Pad | 2 x 2 | 2,804 / 2,804 (silhouette-study); 4,096 / 4,096 (verified-launch-mechanism) |
| AC13 | 163 | Missile Launcher | 2 x 2 | 7,272 / 7,272 (silhouette-study); 8,476 / 8,476 (verified-launch-mechanism) |
| AC14 | 164 | Data Gatherer | 3 x 3 | 9,352 / 9,352 (silhouette-study); 10,556 / 10,556 (verified-launch-mechanism) |
| AC15 | 165 | Listening Device | 2 x 2 | 8,908 / 8,908 (silhouette-study) |
| AC16 | 166 | Manoeuvring Device | 2 x 2 | 9,708 / 9,708 (silhouette-study) |
| AC17 | 167 | Destination Beam | 2 x 2 | 7,528 / 7,528 (silhouette-study) |
| AC18 | 168 | Reactor Cores | 2 x 2 | 4,764 / 4,764 (silhouette-study) |
| AC19 | 169 | Asteroid Shield | 2 x 2 | 3,368 / 3,368 (silhouette-study) |
| AC20 | 170 | Defence Battery | 2 x 2 | 5,156 / 5,156 (silhouette-study) |
| AC21 | 171 | Commonbore | 3 x 3 | 10,648 / 10,648 (silhouette-study) |
| AC22 | 172 | Deepbore | 3 x 3 | 10,904 / 10,904 (silhouette-study) |
| AC23 | 173 | Ore Yard | 2 x 2 | 8,436 / 8,436 (silhouette-study) |
| AC24 | 174 | Goods Yard | 2 x 2 | 7,272 / 7,272 (silhouette-study) |
| AC25 | 175 | Stun Tower | 2 x 2 | 5,156 / 5,156 (silhouette-study) |
| AC26 | 176 | Power Tower | 2 x 2 | 6,300 / 6,300 (silhouette-study) |

The read-only Blender 4.5.15 inspection opened all 29 existing candidate pairs for 26 definitions and independently imported each GLB. It counted evaluated native triangles and actual exported index accessors, and recorded frame-1 mesh bounds, materials and animation clip names. Both binaries remained byte-identical. These checks do not establish visual/material parity, legacy fidelity, complete state coverage or client performance. Exact source hashes and per-mesh results are in [the baseline JSON](achaean-building-remaster-baseline.json).

AC12, AC13 and AC14 already have launch-facility refinements in addition to their coarse studies. Preserve useful geometry and mechanisms, then verify them against current references and contracts. The AC12 export contains LaunchFacilityCycle; AC13 and AC14 currently have no exported animation clips. Existing inventory stage labels are historical claims, not fresh exhaustive acceptance.

## Reference interpretation

Actual embedded-palette surface layers for AC01–AC26 were decoded privately from the original building archive. Names and functional records 1012–1037 were checked directly, along with Achaean architecture record 166. Original pixels and verbatim lore are not published here. The culture supports curved forms, onion domes and occasional slim towers, with crowded comfortable interiors; object-specific evidence takes priority over generic decoration. The surface set shows a coral/copper family with gold details and blue-gray fittings.

AC01 Footprint is the essential colony-support building: an asymmetrical tall narrow segmented column above two rounded lower chambers. Its original 41-frame catalogue sequence was freshly decoded; the sampled phases show reveal/highlighting of a fixed view, not proof of mechanical operation or additional camera headings. Further catalogue, technical and coloured _MA sequences require per-object inspection before authoring. Do not assume only ST animations are relevant.

## Delivery gates

For each building: inspect function/culture and actual paletted references, generate and assess up to three real ImageGen concepts, author/refine one canonical editable Blend and GLB, preserve named parts and pivots, apply appropriate readable wear, inspect real saved-native and independent-import renders against legacy/concept, verify actual export budgets and relevant states, update both galleries, run source-bound/project/quality checks, sign the milestone and hand off the asset for all game presentation paths. Existing good geometry must not be discarded or duplicated in the package. No canonical inventory selection or final visual acceptance changed at this baseline.

Asset-only runtime verification uses Blender. Final artistic acceptance, game scale/state calibration, package integration and Android performance remain separate gates. Disk capacity was checked before reference/model inspection; work reuses the existing asset checkout. Only task-created temporary outputs may be cleaned.

## Reproduction

Run Blender with `--background --threads 2 --python-exit-code 1 --python sources/tools/blender/inspect_achaean_building_baseline.py -- --root . --output <review-output.json>`. The inspector reads current present Achaean building studies and never saves their sources or exports.
