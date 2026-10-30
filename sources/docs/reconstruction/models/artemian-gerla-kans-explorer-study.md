# Artemian Gerla-Kans Explorer — first authored iteration (#1017)

`openfa:ship/artemian/gerla-kans-explorer`, global type 25 / Artemian local type 0, role class 2. The catalogue establishes a scout with armour 32 and AI construction cost 15. No registered source study existed. This adds a missing first source while preserving all previous models/refinements. Artistic refining remains deferred.

## Source evidence

AR0A.256 supplies 32 populated, correctly paletted headings. All were inspected; eight are retained in the ignored comparison sheet. Sprites are approximately 9–19 pixels wide and 6–12 high, supporting a flat elongated pointed green silhouette and a grey raised upper surface. AR0C is absent; no catalogue video is located. Such small images do not establish precise thickness, sections, front/rear calibration, mechanisms or fine surface construction.

The first source interprets this as a pointed green lower wedge beneath a raised, faceted grey shell. The relative volumes, taper, truncated rear, panel layout and two rear interfaces are authored interpretations. The grey surface is opaque alloy, not a proven canopy. Rear interfaces are not labelled engines or weapons. The functional index maps the name but no narrative. Two equipment slots have neither recovered mount coordinates nor default equipment; neither visible interface is assigned to a slot. AlignmentForward is an independently authored local -Y helper, not a calibrated source heading or 3D equipment mount.

ENGLISH.CDB Artemian Architecture record 105 at 0x5734 describes metal/advanced alloys, planes, edges and shell forms in architecture. This gives contextual guidance for ambiguous metal interfaces and faceted construction; it does not prove spacecraft geometry, comfort facilities or decorative insignia. The specific sprite silhouette and grey/green division remain the primary visual evidence. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Legacy pixels remain reference-only and do not enter geometry or texture generation.

## Independent assembly

`docs/assets/reconstruction/ships/artemian/gerla-kans-explorer/` contains editable Blend/GLB, four independently authored colour/roughness maps, metadata, actual native/imported renders, a gallery and technical reports. The 38 closed meshes/four materials comprise the lower wedge/upper shell, four fitted service covers/eight slots/sixteen fasteners, a forward service inset/three alloy slats and two fitted rear bezels/interfaces.

The closed lower and upper shells use independent planform/profile grids with dense subdivisions for shallow physical dents. Explicit rows at longitudinal width/profile breaks and columns at roof-facet breaks preserve the authored geometry. Primary surfaces are triangulated before explicit corner-normal capture, making the native and exported shading contract consistent. Sixteen curved/faceted overlays follow owner-shell width and skin height; their nested slots/slats remain separate editable meshes. Fasteners align to normals sampled from the actual supporting mesh. Rear bezels have ray-fitted embedded roots, with targeted submicron bevel cleanup. All components remain separately editable beneath PlacementRoot.

Two physical dents, independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Two packed image materials cover six meshes; oxidized service alloy and carbon-dark seams use rough authored solids. Modifiers precede local box UV assignment. No previous model or shared helper is modified.

## Verification scope

Blender 4.5.15 reopens native Blend and independently imports GLB. Checks cover positive closed geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, materials and measured dents.

Odd/even actual mesh containment verifies nine lower/upper hull contacts, 64 rear-bezel roots, two rear interface joins, 144 fitted-overlay contacts and sixteen fasteners. These scoped contact samples do not prove exhaustive structural correctness. AlignmentForward is tested under four rigid root rotations; no recovered heading, mount or animation timing is claimed.

Actual native/imported rendering exercises the standalone modelling runtime. Whole-object framing, intentional detail crops and matched alpha/silhouette/pixel checks remain separate from artistic acceptance. Original crops/comparison stay ignored in `artifacts/issue-1017-gerla-kans-explorer/`; tracked gallery images show only authored models. Game-client integration is unchanged. Required changed-code quality verification uses milestone base `e1861846`.

The actual gallery and eight-heading comparison were inspected. Verification passed for 38 meshes/four materials, including six mapped meshes. Green/grey dents measured approximately 0.00361/0.00500 model units; maximum actual corner-normal error was approximately 0.000593. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Inventory verification passed for 303 definitions / 1444 reference occurrences; cultural validation passed for six architecture articles. This is the first registered Artemian ship source, not final artistic or attachment acceptance.

## Deferred

Final shell/wedge proportions, precise taper/thickness, bow/rear calibration, surface division and details, hidden construction, two calibrated mounts, runtime scale/orientation and required operational/damage variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
