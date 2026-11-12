# Artemian Geostationary Construction — first authored iteration (#1022)

`openfa:ship/artemian/geostationary-construction`, global type 30 / Artemian local type 5, role class 7. The catalogue establishes an orbital shipyard with zero speed, armour 130 and AI construction cost 80. No registered source study existed. This adds a missing first source while preserving prior reconstructions/refinements. Artistic refining remains deferred.

## Source evidence

AR5C.256 supplies two correctly paletted fixed-state sprites, 135×74 and 141×81 pixels, not independent cameras. State 0 supports a green axial assembly, copper shells/rim, dark circular face with raised green details/blue marks, axial projections and an off-axis dish. No catalogue video or mapped functional narrative is located. State 1 has a larger mesh-like presentation whose meaning and timing remain unresolved; it does not establish a deployment sequence, another spatial view or construction scaffolding. Both states are retained in ignored comparison evidence. This first model interprets state 0 and does not claim complete states.

The first source uses a green axial pressure body and central boss, copper aft shell, a large copper annular rim around a solid dark backing plate, six front modules/collars, twelve blue inserts, axial stems/tips and a concave side dish. Counts, sections, proportions, hidden backs and the local +Z axis are authored interpretations. A solid backing plate is not proof that the original dark field was solid, nor is the dark field proof of a portal or open shaft. Blue/amber inserts are rough non-emissive materials. Five equipment slots lack recovered mount coordinates/default equipment; visible modules are not assigned to slots or given proven weapon/engine functions. AlignmentAxis is uncalibrated.

ENGLISH.CDB Artemian Architecture record 105 at 0x5734 supplies contextual alloy/shell guidance rather than recovered spacecraft geometry. It does not establish interior architectural features or mechanisms. Specific paletted sprites guide the broad form and colours. Cultural, functional, reference and gameplay indexes plus helpers are hash-bound. Original pixels remain reference-only and never enter geometry/texture generation.

## Independent assembly

`docs/assets/reconstruction/ships/artemian/geostationary-construction/` contains editable Blend/GLB, four independent colour/roughness maps, metadata, nine native/imported rendered views, gallery and technical reports. The 65 closed meshes/six materials comprise three main shells/boss, six front modules, dark backing face, copper face rim/six collars, twelve blue inserts, two axial stems/tips, side dish/mast/feed/tip, and four service covers/eight slots/sixteen fasteners.

Independent radial pressure profiles retain separate geometry and nine shallow dents. Face rim and collars are closed annuli with explicit central voids; the backing plate is separately modelled. The side dish has a closed thin concave wall with an open mouth, independent of the feed/mast; it is triangulated before corner-normal capture. Twelve fitted overlays follow owner profiles, including nested slots, and fasteners align to normals sampled from actual hull meshes. All parts remain editable beneath PlacementRoot.

Independent analytic grime/stains, grain and issue-seeded scratches supply surface wear. Two packed image materials cover 24 meshes; oxidized service alloy, carbon-dark surfaces, blue inserts and amber tips use rough authored solids. Modifiers precede local box UV assignment and explicit corner normals. Existing model sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens native Blend and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, material parity and dents. Core/copper/boss dents measure approximately 0.00500/0.00576/0.00396 model units; six module dents measure approximately 0.00291 each. Maximum corner-normal error is approximately 0.000593.

Odd/even actual mesh containment checks four cap/core contacts, three core/backing-plate joins, sixteen face-rim roots, seven front module/boss roots, 48 collar roots, twelve blue-insert roots, axial stem/tip and side dish/feed/mast joins, eight dish wall witnesses, 108 fitted-overlay contacts and sixteen fasteners. Seven annular axes and the dish mouth have explicit void witnesses. These scoped samples do not prove exhaustive structural/mechanical correctness. AlignmentAxis is tested under yaw, pitch and roll, without source orientation, equipment-mount or animation calibration claims.

The actual gallery and both source states were inspected. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.003/255. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1022-geostationary-construction/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `dfa8eb99`.

## Deferred

Final proportions, green core/module geometry, dark-field construction, module/insert count/layout/function, side-dish interpretation, second-state presentation, hidden structure, five calibrated mounts, runtime orientation/scale and required damage/operational variants remain unresolved. Technical validity does not accept final art or state completeness. Artistic refining and construction scaffolding (#983) remain deferred.
