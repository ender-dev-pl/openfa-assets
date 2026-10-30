# Artemian Shielded Multi-Assault — first authored iteration (#1019)

`openfa:ship/artemian/shielded-multi-assault`, global type 27 / Artemian local type 2, role class 3. Catalogue data supplies combat-direct-approach, armour 50 and AI construction cost 25. No registered source study existed. This adds a missing first source while preserving previous models/refinements. Artistic refining remains deferred.

## Source evidence

AR2C.256 supplies 32 populated, correctly paletted headings, approximately 28–41×10 pixels. All were inspected, including enlarged 0/4/12/28; eight appear in ignored comparison evidence. They support a broad flat silver/grey silhouette, raised central volume, warm gold portions, small blue-grey accents and pale/amber marks. This is materially different visual evidence from All-Purpose Assault's green delta. No catalogue video or mapped functional narrative is located.

Exact planform, thickness, sections, spatial colour distribution and front/rear calibration remain unresolved. A broad pointed metal wing with a low central pressure body is the first interpretation. Port-gold/starboard-silver halves are explicitly authored material placement, not a recovered division: the gold appearance changes across headings, and the evidence does not fully distinguish surface distribution from viewing/lighting effects. The fixed half division needs later review alongside actual shape proportions. Blue-grey fittings, service construction and hidden backs are independently interpreted below source resolution.

Four equipment slots have no recovered mount coordinates or default equipment. Neither fittings nor amber marks are assigned to those slots or claimed as engines/weapons. The name alone does not establish visible energy-shield geometry or a shield animation. AlignmentForward is an authored local -Y helper, not a recovered 3D mount or calibrated source heading.

ENGLISH.CDB Artemian Architecture record 105 at 0x5734 provides contextual metal/alloy, edge and shell guidance. It does not prove spacecraft geometry or precise decorative alloy placement. The specific paletted sprite evidence guides the first source; no insignia or architectural interiors are invented. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only and are absent from geometry/texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/artemian/shielded-multi-assault/` contains editable Blend/GLB, four independent colour/roughness maps, metadata, nine native/imported rendered views, a gallery and technical reports. The 46 closed meshes/five materials comprise the broad wing/central body, four service covers/eight slots/sixteen fasteners, a forward inset/three slats, two fitted saddles/two blue-grey fittings and two curved side insets/six amber inserts.

The wing uses a closed tapered planform grid with dense subdivisions for two shallow dents. A separately authored elliptical longitudinal body has triangle-fan caps and its own dent. Primary triangulation precedes explicit corner-normal capture. The primary meshes retain independently editable silver/gold face assignments; the verifier checks the authored division in both formats without claiming source calibration. Twenty-eight overlays follow owner widths/skin heights, including nested slots, fittings and inserts. Fasteners align to normals sampled from actual support meshes. All components remain separately editable under PlacementRoot. All-Purpose Assault was not regenerated or registered as a shared source.

Three physical dents, independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Two packed image materials cover eight meshes; oxidized blue-grey fittings, carbon-dark seams and dull amber inserts use rough authored solids. Modifiers precede local box UV assignment. Existing models and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens the native asset and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, material parity/primary face assignments and measured dents. The central dent measures approximately 0.00495 model units; wing dents are approximately 0.00355 each. Maximum actual corner-normal error is approximately 0.000575.

Odd/even mesh containment verifies nine body/wing overlap points, 252 fitted-overlay contacts including both fitting/saddle interfaces, and sixteen fasteners. These scoped contact samples do not establish exhaustive structural/mechanical correctness. AlignmentForward is tested under four rigid root rotations without source heading, equipment mount or animation calibration claims.

The actual gallery and eight-heading comparison were inspected. Nine views passed framing/export review: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1019-shielded-multi-assault/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `ab21ccaf`.

## Deferred

Final wing/body proportions, precise planform, silver/gold distribution and surface treatment, blue-grey fittings and amber-mark meanings, hidden construction, four calibrated mounts, runtime scale/orientation and required damage/operational variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
