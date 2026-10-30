# Mikotaj Na-Xanth — first authored iteration (#1016)

`openfa:ship/mikotaj/na-xanth`, global type 24 / Mikotaj local type 4, role class 7. The catalogue establishes an orbital shipyard with zero speed, armour 140 and AI construction cost 80. No source study was registered. This adds the missing first source; existing models/refinements are preserved and artistic refining remains deferred.

## Source evidence

MK4C.256 provides two correctly paletted fixed-state sprites, 159×65 and 174×82 pixels, not independent spatial views or a heading bank. State 0 supports three rounded slate/green chambers, a larger central volume, copper forward details, perimeter projections and axial discs. Hidden backs, exact chamber dimensions, number and radial arrangement of fittings, coupler construction and structural connections remain independently interpreted.

State 1 is larger and has a dark green mesh-like presentation. Its meaning, relationship to the first state and timing remain unresolved. It does not establish another camera, an opaque saucer, a physical deployment sequence or construction scaffolding. Both states are retained in ignored comparison evidence, with explicit fixed-state labels. This first model interprets state 0 and does not claim state completeness. No catalogue video is located.

The functional text index maps the name but no narrative. Four declared equipment slots have no recovered mount coordinates or default equipment. Neither the three forward details nor the perimeter fittings are assigned to those slots or given proven weapon/docking functions. AlignmentAxis is an authored local +Z helper, not a recovered source axis or equipment mount. The shipyard tag alone does not establish individual mechanisms.

Mikotaj Architecture in ENGLISH.CDB, record 76 at 0x39fa, distinguishes heavy metallic mining-colony structures from light resonant crystal architecture on home worlds. It supplies contextual guidance for robust metal interfaces, not proof of this spacecraft's construction. Green upper shells remain opaque and non-emissive; no universal crystal rule is inferred. Cultural, functional, visual-reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels are reference-only, absent from geometry and texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/mikotaj/na-xanth/` contains editable Blend/GLB, six independent colour/roughness maps, provenance, nine rendered views, a gallery and technical reports. The 113 closed meshes/six materials comprise three slate pressure chambers/three green upper shells, two structural necks, three fitted copper bezels/three forward couplers/three dark faces/nine small amber inserts, 24 perimeter stems/discs, six axial stems/discs, three curved upper panels/twelve inserts and twelve fasteners.

Chamber dimensions, eight perimeter fittings per chamber, symmetric hidden backs, neck layout and service construction are authored interpretations. Each green upper shell overlaps its slate pressure body; sampled necks connect adjacent chambers. Forward bezels have ray-fitted embedded backs rather than floating planar roots. Their bevel slivers receive targeted submicron cleanup before UV assignment. Fifteen curved patches follow their green support profiles, including nested inserts. All components remain editable beneath PlacementRoot.

Six physical shell dents, independent analytic stains/grime, grain and issue-seeded scratches supply new-object wear. Three packed image materials cover 74 meshes. Oxidized service alloy, carbon-dark recesses and dull amber inserts use authored rough solid materials. Modifiers precede local box UV assignment and explicit corner-normal capture. The new placement helper uses an explicit identity matrix for unrotated chambers: Blender's +Z track quaternion otherwise adds an unintended 180-degree roll and displaces the authored dent locations. Previously created sources/shared helpers remain unchanged.

## Verification scope

The standalone modelling runtime reopens native Blender and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, materials and actual corner normals within 0.001.

Odd/even actual mesh containment checks chamber overlaps, structural necks, perimeter/axial stem roots and disc joins, 96 bezel roots, coupler/face joins, nine face inserts, 135 fitted-panel/insert contacts and twelve fasteners. These are scoped contact samples, not exhaustive structural or mechanical proof. AlignmentAxis is tested under four rigid root orientations including pitch and roll, so both its position and axis change; source orientation, four equipment mounts and animation timing remain uncalibrated.

Actual native/imported renders exercise the modelling runtime without changing game-client integration. Whole-object framing, intentional detail crops and matched alpha/silhouette/pixel checks remain separate from artistic acceptance. The gallery contains only authored renders; original crops/comparison remain ignored evidence in `artifacts/issue-1016-na-xanth/`. Required changed-code quality verification uses milestone base `7732a02f`.

The actual gallery and both source states were inspected. Verification passed in Blender 4.5.15 for 113 meshes/six materials, including 74 mapped meshes. The two central chamber dents measured approximately 0.00571/0.00590 model units; the four side-chamber dents measured 0.00423/0.00437 per pair. Maximum actual corner-normal error was approximately 0.000578. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical, and maximum foreground mean RGB difference is below 0.004/255. Inventory validation passed for 303 definitions / 1444 reference occurrences; cultural validation passed for six architecture sections. All five Mikotaj ship definitions now have first sources, without implying artistic, attachment or variant acceptance.

## Deferred

Exact chamber proportions, copper coupler/fitting layout and meaning, hidden structure, second-state presentation, four calibrated mounts, runtime orientation/scale and required damage/operational variants remain unresolved. Technical validity does not accept final art or state completeness. Artistic refining and construction scaffolding (#983) remain deferred.
