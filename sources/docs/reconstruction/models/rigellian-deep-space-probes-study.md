# RI12 Deep Space Probes — initial editable study (#984)

Catalogue ID `openfa:building/legacy/051`, global type 51, nominal footprint 2x2. This is a newly authored missing-model study, not a replacement of an existing refined model or final artistic acceptance.

## Function and evidence

Original ENGLISH.TXT record 912, byte offset 0x1142B, describes research and neighbour-observation sensors. Correctly paletted `RI12/surface-01.png` and catalogue phases show a circular low green pad with a small gold fitting, a stepped pedestal, a long narrow mast, exposed copper-coloured neck, dark/red side module, enlarged head and segmented tapering tip. Catalogue phases reveal/highlight the object; they are not additional spatial angles.

Exact hidden surfaces, rotational profiles, dimensions, collar construction, captive fasteners and side-module attachment are independently authored engineering interpretations. The lower pedestal's dark area remains ambiguous; it has not been converted into an invented functional trench. Original pixels are reference-only and are absent from model textures and geometry inputs.

## Deliverables and verification

`docs/assets/reconstruction/buildings/rigellian/deep-space-probes/` contains editable Blender source, standalone GLB, authored colour/roughness maps, metadata, nine actual rendered views and review reports. Five radial painted parts have real shallow geometric dents. Analytic maps add restrained contamination, handling stains and scratches; end caps have separate planar UVs. The neck and fittings use independent metal materials.

The Blender verifier reopens the saved native model and independently imports GLB. It checks closed positive mesh topology, identity placement root, nominal footprint, actual bounds, individual object transforms/bounds, five measurable dents, neck overlap with the head and mast, side inset contact, 32 curved-pad fitting flange root samples, the fitting face, packed texture source bytes, all decoded colour/roughness pixels, UV mapping and material export quantization. These are scoped checks, not proof of every possible contact.

Matched-camera whole-object and neck-detail renders are compared separately. All six whole-object views and imported whole-object view require unclipped transparent framing; intentional macro crops are labelled. The gallery and original comparison are inspected as actual rendered images. The original comparison remains in ignored reference artifacts rather than distributable model assets.

## Review and remaining quality work

The first render established the source's narrow segmented silhouette and visible copper neck. Macro inspection exposed a side cover using the painted UV material without a corresponding authored map; the cover now uses the green neck-alloy material. Native/imported verification was rerun after that correction.

This is still an initial study. The broad painted surfaces and metal neck need a further high-detail finish review; the pedestal shadow feature and exact head/tip proportions need additional reference scrutiny. Rear details, operational/damage presentation and game orientation/scale/placement are not established. No moving mechanism is inferred from catalogue reveal frames. Construction scaffolding stays explicitly deferred under #983. No final artistic or game-runtime review gate is accepted by this milestone.

## Revision 2 — profile and manufactured finish

Reinspection of the readable catalogue phase showed a relatively straight segmented tip. Revision 2 removes the first study's excessive mid-tip narrowing and gives the ground pad distinct shallow steps. Precise profiles remain inferred from low-resolution evidence; the ambiguous pedestal shadow has not been turned into an invented trench or mechanism.

The copper spindle now has its own independently generated 512x512 colour and roughness maps: fine circumferential machining variation, darker contamination near the retaining collars and a local green oxidation patch. Painted surfaces receive a stronger but restrained grain/roughness variation. These additions read no legacy image pixels.

The expanded verifier found that the spindle's unapplied bevel caused its UVs to interpolate away from the analytic cylindrical mapping during GLB export. The builder now applies the spindle's bevel geometry before assigning UVs, keeping the original UV checks intact. Native and imported texture evidence covers three materials, six source images and twelve planar end surfaces, together with the prior geometry/contact checks. Actual macro and whole-object renders are regenerated after correction.

This is a targeted refinement of the existing study, not a replacement reconstruction. It does not establish final high-detail artistic acceptance, damage presentation or game calibration. The remaining pedestal/profile and finish questions stay open.

Revision 2 verification passed in Blender 4.5.15 for native and imported assets. The gallery now contains eleven views, including matched base-detail and neck-detail pairs. All three compared pairs have identical threshold-128 silhouettes and alpha; maximum foreground RGB mean difference remains below 0.006/255. The full inventory verifies 303 definitions and 1444 reference occurrences. Required changed-code quality verification passed against milestone base `5435d0a0`.
