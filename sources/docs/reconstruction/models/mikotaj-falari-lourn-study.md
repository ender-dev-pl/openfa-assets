# Mikotaj Falari-Lourn — first authored iteration (#1014)

`openfa:ship/mikotaj/falari-lourn`, global type 22 / Mikotaj local type 2, role class 6, cost 50 and armour 70. This adds a previously missing source; existing reconstructions and refined versions remain unchanged. Artistic refining is deferred.

## Source evidence

All 32 populated MK2C.256 headings were inspected with their embedded palette. MK2A is absent; no catalogue video is located. Canonical headings 0/8/16/24 measure 59×15 pixels; heading 4 reaches 83×15 and headings 12/28 are 24×16. The images support a rounded blue central body, a very long thin green pointed surface and small gold accents. Colour-mask inspection finds no clear longitudinal opening in the green projection. A continuous lozenge wing beneath the body is the first interpretation, not proof that the original had one continuous physical plate. Overlapping structures, exact profile, thickness, proportions and heading calibration remain unresolved.

The functional text index supplies the name but no mapped narrative. Five catalogue equipment slots have no recovered mount coordinates or default equipment. Gold fixtures and body details are not assigned to those slots or given a proven weapon/engine function. AlignmentForward is an independently authored, uncalibrated local -Y helper.

ENGLISH.CDB Mikotaj Architecture record 76 at 0x39fa distinguishes heavy metallic mining-colony construction from light resonant crystal architecture on home worlds. This offers contextual guidance for robust interfaces, not direct evidence of this ship's material or geometry. Blue/green/gold opaque materials follow visible source colours; neither universal crystal construction nor a mining role is inferred. Model metadata binds the cultural, functional, reference and gameplay indexes plus authoring helpers. Legacy pixels remain reference-only.

## Independent construction

`docs/assets/reconstruction/ships/mikotaj/falari-lourn/` contains editable Blend/GLB, six independent colour/roughness maps, provenance, nine rendered views, a gallery and technical reports. Thirty closed meshes/five materials comprise the blue pressure body, continuous green wing, four fitted saddles/four gold fixtures, paired body bezels/faces, two hull service covers/four slots/eight fasteners, and two wing insets. Layout and fine construction below source resolution are authored interpretations.

The body uses dense elliptical longitudinal sections and triangle-fan caps. The wing has a tapered closed shell and explicit triangulation before corner-normal capture, avoiding a native/export shading discrepancy on nonplanar grid faces. Body bezels have ray-fitted embedded roots; their bevel slivers receive local submicron cleanup before UV assignment. Twelve overlays follow their hull/wing support surfaces, and fasteners align with normals sampled from the actual hull mesh. All components remain editable under PlacementRoot.

New-object wear comprises three physical dents, analytic grime/stains, grain and seeded scratches. Three packed image materials cover fourteen meshes; oxidized service alloy and dark seams use rough solid materials. No original image is read by the wear generator. Applied modifiers precede local box UVs and explicit corner normals. Previous models and shared helpers were not modified.

## Verification scope

Blender 4.5.15 reopens the native asset and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, material parity, box UVs and actual corner normals within 0.001. Measured dents are approximately 0.00598, 0.00384 and 0.00395 model units; maximum normal-vector difference is approximately 0.000575.

Odd/even mesh containment verifies nine wing/hull joint samples, twenty fixture/saddle roots with underlying wing contacts, 64 bezel roots, two bezel/face joins, 108 fitted-overlay contacts and eight fasteners. Two additional witnesses verify material inside the continuous wing. These are scoped contact samples rather than exhaustive structural proof. The alignment helper's position/axis is checked under four rigid root rotations. No recovered 3D mounts or animation timing are claimed.

The actual gallery and eight-heading comparison were inspected. Nine views passed framing/export review. Both matched-camera alpha channels and threshold-128 silhouettes are identical; maximum foreground mean colour difference is below 0.004/255. The standalone modelling runtime is exercised through native and imported renders; game-client integration is unchanged. Original crops/comparison remain ignored evidence in `artifacts/issue-1014-falari-lourn/`; tracked gallery images contain only authored models.

Inventory validation covers 303 definitions / 1444 reference occurrences. Functional-source validation covers 303 definitions and cultural validation covers six architecture sections. Required changed-code quality verification uses milestone base `f020c54b`.

## Deferred

Wing continuity, body/wing proportions, gold-detail placement/function, hidden construction, five calibrated mounts, runtime scale/orientation and required damage/operational variants remain unresolved. Technical correctness does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
