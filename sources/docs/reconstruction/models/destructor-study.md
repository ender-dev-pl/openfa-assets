# Destructor — first authored iteration (#996)

`openfa:destructor`, Terran ship type 3. The authoritative inventory contained no registered source model for this ship. Existing Assault Fighter, Combat Eagle, Scoutship and Transporter studies are preserved. The current pass supplies first iterations only; further artistic refining is deferred.

## Source evidence

`ship-reference-index.json` binds correctly paletted PS3C.256 directional surface sprites and the decoded sixty-frame PS03.VID inventory rotation. Actual original rotation frames 0/15/30/45/59 were inspected. They show a broad triangular wedge, red flank and aft markings, paired rounded aft engine housings, dorsal vent and small bow/outboard projections. The mesh and maps are independently authored; no source pixels or meshes enter deliverables.

No functional narrative is mapped to this ship in the functional index. Catalogue role/default equipment data does not establish additional operational mechanisms. Three designer mount coordinates are 2D and do not prove any 3D socket transform.

## First geometry

A single closed continuous faceted hull uses authored section transitions, with two small local geometric dents. Separate conformal red flank strips, rounded aft housings, hollow bronze exhaust annuli, recessed dark throats, cooling ribs, outboard wings/prongs, bow projections, dorsal vent fins and four crown service plates complete the initial assembly. Exact cross-sections, underside, hidden connections and maintenance details are interpretations. No animated or luminous firing effect is invented.

Fifty-seven editable meshes and five materials are saved under `docs/assets/reconstruction/ships/terran/destructor/`. Four independent hull/red colour and roughness maps contain stains, grain, handling dirt and seeded scratches. Smaller components use worn alloy/soot material values. Applied bevels precede per-face local box UV assignment to keep the export mapping stable.

PlacementRoot uses local -Y forward. Three tentative hardpoint sockets and two exhaust sockets use local +Z forward axes. Their authored positions are explicitly uncalibrated, rather than presented as recovered legacy mounts.

## Technical and visual scope

The verifier reopens native Blender and imports standalone GLB. Every physical part must be closed with positive volume. It checks bounds/transforms, source/helper provenance, packed texture bytes and decoded colour/roughness pixels, UV projection, two measured dents and common interior samples at hull/pod, pod/nozzle, hull/wing, hull/red strip and hull/vent contacts. Exhaust axes must remain open ahead of recessed dark throats. Five socket positions/directions are checked under four rigid root rotations. Samples are scoped evidence, not exhaustive structural validation.

Technical fixes embed nozzle roots into the aft housings and seat the vent surround in the sloping hull; these correct first-version attachment failures without an artistic refinement cycle. Actual Blender native/imported renders exercise the standalone runtime. Matched-camera comparisons check export fidelity; original comparisons remain in ignored artifacts. Client integration is unchanged.

## Deferred

Final silhouette/proportions and finish, more source-level panel detailing, antenna/mount calibration, operational/damage variants, game scale/orientation and final artistic acceptance remain for later passes. No final acceptance gate is promoted. Construction scaffolding remains separately deferred under #983.

First-version checks passed in Blender 4.5.15 for 57 meshes and five materials. Hull end caps use explicit nondegenerate triangle fans. glTF UV/flat-normal seams split vertices; diagnostic BMesh welding at 1e-6 model units restores closed positive-volume geometry and exactly the native geometric vertex count for every mesh. No source/imported mesh is mutated by this check, and actual gaps remain rejected. Nine render views passed framing/export comparison; both threshold-128 silhouettes match exactly. Whole-object alpha is identical; engine macro has one edge pixel differing by 4/255 alpha. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `552ce7b0`.

Comparison leaves the aft shoulder shape, fine source panel divisions and exact marking widths as later artistic gaps; the current independently authored first layout is retained. No final silhouette or material acceptance is inferred from technical export checks.
