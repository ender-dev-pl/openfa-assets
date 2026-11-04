# Ship reference review — issue #952

This is reference preparation for #949, not model acceptance. The source identities,
palettes, selected frames and hashes are recorded in `ship-reference-index.json`.
Original pixels remain in ignored `artifacts/ship-reference-study/references/`.
The eight culture sheets were visually inspected at nearest-neighbour enlargement.
The Assault Fighter and Transporter inventory rotations were also inspected.

## Observations and modelling constraints

The following are visible silhouette/colour observations, not claims about hidden
mechanisms, exact physical dimensions, or socket transforms. Small sprites often
support only a silhouette; invented fine detail must be labelled authorial.

| Global type | Ship | Visible form to preserve |
| --- | --- | --- |
| 0 | Assault Fighter | Triangular swept hull, red edge bands; inventory rotation resolves rear engine cluster and top recesses. |
| 1 | Combat Eagle | Open swept arms around a narrow central body; red outer sections. |
| 2 | Scoutship | Broad compact wedge, blue-grey central shell, red side panels. |
| 3 | Destructor | Long tapered wedge, raised rear mass and orange rear exhaust. |
| 4 | Terminator | Broad flattened hull with paired raised shoulder housings and thin lateral projections. |
| 5 | Transporter | Angular cargo body, dorsal stepped structures, red side stripe, distinct rear engine assembly; rotation supports faceted rather than soft capsule construction. |
| 6 | Fleet Battleship | Wide arch-like swept body, open underside silhouette, red dorsal bands. |
| 7 | Space Dock | Tall pointed lower section, broad central hub, thin upper mast; only two fixed states. |
| 8 | Command Cruiser | Long slab hull, distributed dorsal equipment, red lateral stripe and projecting lower surfaces. |
| 9 | Spy Satellite | Tiny mast-and-crossbar silhouette; one 15×13 source frame cannot establish a detailed solid. |
| 10 | Lazzaro Research | Gold central plate and four grey extremities; only 14×9 pixels in sampled views. |
| 11 | Delphini Assault | Green low swept hull with copper end sections and projections. |
| 12 | Messier-Lukannon | Rounded green oval shell, copper perimeter pods and small gold dorsal bumps. |
| 13 | Transportation | Two linked elongated green shells with gold circular markings. |
| 14 | Observatory | Vertical spindles above/below a broad ring-like central section; two fixed states. |
| 15 | Rattlesnake | Very narrow copper spindle with brighter expanded end sections. |
| 16 | WidowMaker | Gold barrel-like body, copper rounded end, grey longitudinal side structures. |
| 17 | HeartsBlood | Broad clustered gold/copper lobes with repeated collar-like bands and grey end cluster. |
| 18 | Morning Glory | Compact copper body with bright central area and narrow projecting end. |
| 19 | SkyMech | Vertical central assembly and four rounded peripheral masses; two fixed states. |
| 20 | Hiero | Blue-grey radial/star-like silhouette, gold centre and thin projections. |
| 21 | Ylikt-shan | Narrow paired lobes around a central opening, small external tips. |
| 22 | Falari-Lourn | Thin wide green swept rim around a blue central dome. |
| 23 | Ruth-Strivakh | Long structure with rounded end pods and several smaller dorsal masses. |
| 24 | Na-Xanth | Three green rounded modules linked by copper structures; two fixed states. |
| 25 | Gerla-Kans Explorer | Narrow grey wedge with green lower edge. |
| 26 | All-Purpose Assault | Broad green angular footprint with grey central/side regions. |
| 27 | Shielded Multi-Assault | Low grey flattened hull with gold side tips and raised central portion. |
| 28 | Ultimate Mk II | Broad smooth grey upper oval, green lower band and repeated pale underside protrusions. |
| 29 | Hardcore | Paired gold domes linked across a narrow central body with grey outer details. |
| 30 | Geostationary Construction | Horizontal green assembly, copper curved frame and thin radial appendages; two fixed states. |
| 31 | Surveillance Craft Type 5 | Tall grey plate/block with irregular notches and narrow underside. |
| 32 | Combat Craft Type 1.5 | Small angular grey elongated hull with expanded end sections. |
| 33 | Max Combat Craft Type 6 | Long box-like grey hull, raised red dorsal elements and dark lower strip. |
| 34 | Elite Command Craft | Paired tall rectangular masses across central block, light blue face strips and side projections. |
| 35 | Transportation Craft Type 3 | Tall upright slab assembly above a rounded horizontal base; repeated recesses and vertical side columns. |
| 36 | Orbital Construction Area | Broad horizontal station with stacked upper/lower towers and side equipment rack; two fixed states. |
| 37 | Hunter/Prospector | Small red/green branched silhouette; fine structural interpretation unresolved. |
| 38 | Dedicated Fighter | Strong open crescent/claw silhouette with layered grey, red and gold swept blades. |
| 39 | Dedicated Ore Transporter | Copper central body inside long swept grey/red forked exterior arms. |
| 40 | Orbital Shipyard | Very wide thin platform with repeated vertical pylons and central raised mass; two fixed states. |

## Evidence limits and next acceptance work

- 33 directional sheets provide 32 source entries each; the review sheets sample
  entries 0, 8, 16 and 24. Runtime uses even entries only for eight specified ships.
- Seven orbital yards have two fixed states. Their second scan-like images are
  not alternate viewing angles. The single satellite frame is also not a rotation.
- Nine Terran inventory videos are decoded and indexed. Only the two rotations
  named above have been visually reviewed at this milestone; the other seven
  remain available for per-model study.
- All selected surface sheets carry embedded palettes. Palette binding for other
  asset categories, especially missiles, is a separate task.
- Designer mount coordinates are two-dimensional. They do not establish 3D
  hardpoint sockets, orientation, clearances, recoil travel, or firing arcs.
- Each model still needs native geometry, independently authored materials,
  multiple close views, silhouette comparisons, mechanical/animation checks,
  export/import checks, and explicit review tied to its exact revision.
- No review-ledger acceptance gate is changed by reference preparation.
