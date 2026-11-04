# RI15 Energy Globe — initial reference-refined study (#987)

Catalogue ID `openfa:building/legacy/054`, global type 54, nominal 2x2 footprint. This fills a missing authored study without replacing any existing reconstruction or refined version.

## Function and source evidence

Original ENGLISH.TXT record 915 at byte offset 0x115C1 identifies storage of generated energy. Correctly paletted surface body (27x33) and readable catalogue phase show a segmented grey globe, exposed brass stem, low grey base, offset green circular fitting with dark vertical detail, smaller grey side fitting and small brass base detail. Catalogue reveal/highlight phases are not rotations and do not establish moving or operating machinery.

The exact sphere profile, complete meridian/equator layout, unseen rear/bottom geometry, fitting castings, fasteners and stem interfaces are independently authored engineering interpretations. The source shows visible divisions and features, not their hidden construction. The green face has no invented emission. Original pixels are used only for reference, absent from authored textures and mesh inputs.

## Actual render refinement

The first render under-represented the meridian grooves and exposed a flat circular top cap. Grooves were widened to a readable physical recess, and the pole closure was reduced to remove the unintended top-button appearance. The globe retains real geometric meridian and equatorial seams, rather than painted dark lines alone. Four meridians at two heights are checked against the nominal radial profile; the equator is independently ray-checked. Actual source comparison also exposed the wrongly centred green face and missing smaller grey side fitting. The green face was moved to the source-visible right side and the grey feature added; exact angular placement remains inferred.

Three main radial parts have measured shallow geometric dents. Independent bronze/grey colour and roughness maps add joint contamination, handling marks, grain and seeded scratches. Cylindrical side UVs use the actual local angle and Z/2.4; end caps have separate planar mapping. A further actual-render review found that the physical meridians still read weakly. Grey-shell dirt is now concentrated at the same angular/height coordinates as the measured grooves, improving their readability without substituting painted lines for geometry. Source images are not read by any authoring script.

## Deliverables and verification scope

`docs/assets/reconstruction/buildings/rigellian/energy-globe/` contains editable Blender source, standalone GLB, eight authored maps, metadata, technical/render reports and eleven actual 900x900 views. Original comparison pixels remain in ignored `artifacts/rigellian-building-reference-study/RI15/comparison.png`, outside distributable model assets.

The verifier reopens native Blend and imports GLB independently. It checks closed positive topology, identity root, footprint/bounds and individual object transforms/bounds; base/stem/globe overlap; three physical dents; actual meridian and equatorial grooves; 32 curved-body flange-root samples on each of three fittings; embedded fitting faces, vertical inset and six captive fasteners. It verifies cylindrical/planar UVs, six planar caps, packed source bytes, decoded colour/roughness pixel equality and material export quantization. Contacts are scoped samples rather than exhaustive engineering proof.

Whole-object views require transparent unclipped framing. Face-detail and base-detail macro crops are intentional. Three matched-camera native/imported pairs compare silhouette, alpha and RGB difference. The standalone asset milestone uses Blender native/imported GLB as its target runtime; client integration is not changed or claimed.

## Remaining quality and acceptance

This remains a reference-refined study, not final high-detail artistic acceptance. Globe/base proportions, precise source seam placement and manufactured finish need more review. Rear construction, operational/damage presentation and game scale/orientation/placement are unresolved. Construction scaffolding stays explicitly deferred under #983. No final review-ledger gate is promoted.

Final study verification passed in Blender 4.5.15 with sixteen mesh objects and eight materials. Eleven views passed framing and all three matched-camera pairs have identical threshold-128 silhouettes and alpha. Full inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `d7829430`.
