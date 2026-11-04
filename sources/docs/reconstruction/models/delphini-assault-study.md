# Delphini Assault — first authored iteration (#1003)

`openfa:ship/rigellian/delphini-assault`, global type 11, Rigellian local type 1. The authoritative inventory had no registered source model. Existing reconstructions/refinements are preserved. This pass creates first versions only; further artistic refining remains deferred.

## Reference evidence and limits

`ship-reference-index.json` binds RI1C.256, a 32-entry correctly paletted heading bank of approximately 31-33 by 14-15 pixels, without a located large catalogue animation. Actual headings 0/4/8/12/16/20/24/28 were inspected. They show a rounded elongated green body, narrow grey-green projection, gold upper details and brown lower/lateral masses. Hidden sections, detailed joints and the function of the brown masses are not resolved by these pixels.

The functional text index has no mapped narrative. Catalogue role class/name does not establish individual weapon or propulsion parts. No hardpoints/default equipment or designer mount coordinates are declared; none are invented. AlignmentForward is an authored uncalibrated helper, not an equipment socket, weapon axis or recovered heading calibration.

Original images remain reference-only, absent from mesh/texture inputs. The render reviewer validates embedded palette metadata/canonical decoded image hashes and records comparison-heading hashes. No fabricated large original view is used.

## First assembly

`docs/assets/reconstruction/ships/rigellian/delphini-assault/` contains editable Blend/GLB, four independently authored green/bronze colour/roughness maps, provenance, technical evidence and actual render gallery. Twenty-two meshes and five materials interpret the source as a closed rounded green hull, narrow opaque fore projection, brown tail detail, two brown ventral bodies, two gold upper patches, small dorsal crest, two green service covers/slots and ventral fittings. The latter are authored maintenance detail, not confirmed barrels or exhausts.

Two measured geometric dents, analytic stains, grain and seeded scuffs supply new-object wear. Small parts use rough alloy/joint/bronze material values. Bevels precede box UV mapping; explicit custom corner normals maintain the native/imported shading contract. PlacementRoot uses authored local -Y forward.

The first flat upper patch failed the hull-skin interface check and partly disappeared into the convex surface. It is replaced with a closed 13x13 curved patch following the analytic hull surface, with embedded back thickness. This is a first-version contact/visibility correction, without an artistic refining cycle or changes to previous models.

## Technical scope

The verifier reopens native Blender and independently imports GLB. Native physical parts must be closed with positive volume. Diagnostic-only 1e-6-unit seam welding accounts for glTF UV/normal splits and must recover exact native geometric vertex counts. Files are not mutated. Other checks cover bounds/transforms, packed texture bytes and decoded colour/roughness pixels, local UV projections, actual explicit corner vectors within 0.001 difference, two measured dents and shared interior samples at fore/tail/crest roots, ventral-body joints, curved patches, covers and six ventral fitting roots. AlignmentForward is checked at four rigid root rotations without establishing legacy animation timing.

Actual native/imported Blender renders exercise the standalone runtime. Whole-object framing, intentional hull-detail crops and matched-camera export comparisons are distinct from final artistic acceptance. Contact samples provide scoped correctness evidence, not exhaustive structural proof. Client renderer/integration is unchanged.

## Deferred

Exact body proportions, source marking shapes, brown mass arrangement/function, hidden underside, finer source detail, required operational/damage variants and calibrated game scale/orientation remain for later review. Fine mechanical detail is independently authored below the available source resolution. No final artistic acceptance gate is promoted. Construction scaffolding remains separately deferred under #983.

Final first-version checks passed in Blender 4.5.15 for 22 meshes and five materials. Nine actual views passed framing/export comparison. Both matched-camera alpha channels and threshold-128 silhouettes are identical; foreground mean channel differences remain below 0.006/255. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `98670245`. No existing model was regenerated or refined.
