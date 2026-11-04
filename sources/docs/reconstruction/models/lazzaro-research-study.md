# Lazzaro Research — first authored iteration (#1002)

`openfa:ship/rigellian/lazzaro-research`, global ship type 10, Rigellian local type 0. The authoritative inventory contained no source model. Existing reconstructions/refinements are preserved; this pass generates first versions only.

## Reference limits

`ship-reference-index.json` binds RI0A.256, a 32-entry correctly paletted heading bank of approximately 14x9 pixels. No large catalogue image/video is located for this definition. Actual heading samples 0/4/8/12 were inspected along with the bank. They show a compact green body, gold/ochre central region, grey lateral lobes and small brown corner pixels. This sparse evidence does not establish exact sections, hidden surfaces or detailed mechanical structure.

The functional text index has no mapped narrative. Catalogue name and role class are data, not a basis for invented machinery. No hardpoints/default equipment are declared. The first model does not invent weapons or claim confirmed engine/sensor locations. An alignment helper is explicitly uncalibrated and is not an equipment socket.

Original pixels remain reference-only. The reviewer checks embedded palette metadata and the canonical indexed decoded-frame hashes, and records hashes for the four actual comparison headings. New geometry, colours, textures, wear and joints are independently authored. These renders are not substitutes for missing large legacy views.

## First authored assembly

`docs/assets/reconstruction/ships/rigellian/lazzaro-research/` contains editable Blend/GLB, four independent green/bronze colour/roughness maps, provenance, technical report and actual render gallery. Twenty-six meshes and five materials interpret the tiny sprite as a compact oval green hull, raised gold centre and four grey lobes with brown tips. Hidden braces, fasteners, two shoulder service covers and their dark slots are authored maintenance details. The four-lobe division is an explicit interpretation rather than a proven original mechanical arrangement.

Two measured dents, analytic stains, grain and seeded scratches provide new-object wear. Small components have rough alloy/joint/bronze material values. Applied bevels precede box UV mapping. Explicit authored corner normals preserve the same shading contract in native Blender and GLB. PlacementRoot uses authored local -Y forward; AlignmentForward is the sole nonphysical helper.

## Verification scope

The verifier reopens native Blender and imports GLB separately. Native meshes must be closed with positive volume. Diagnostic-only welding at 1e-6 units accounts for imported UV/flat-normal seam splits and must recover exactly the native geometric vertex count per part. Files are not mutated. It checks bounds/transforms, packed image byte hashes and decoded pixels, UV projection, explicit actual corner-normal vectors within 0.001 vector difference, two measured dent depths, shared interior crown/hull, lobe/hull, brace/hull, brace/lobe, tip/lobe and shoulder-cover samples. The alignment helper position/axis is tested at four rigid root rotations; this is not a calibrated heading mapping or an asserted animation.

Actual native/imported Blender renders exercise the standalone runtime. Whole-object framing, intentional hull-detail crops and matched-camera export comparisons are separate from final artistic acceptance. Client integration is unchanged; contact samples provide scoped correctness evidence.

## Later gaps

Silhouette/section interpretation, gold region proportions, lobe division, source colour matching, hidden surfaces, required variants and calibrated game scale/orientation remain unresolved for later review. Fine mechanical detail is low-confidence because source pixels do not resolve it. No final artistic acceptance is promoted. Further refining and construction scaffolding remain deferred, the latter separately under #983.

First-version checks passed in Blender 4.5.15 for 26 meshes and five materials. Nine actual views passed framing/export comparison. Both matched-camera alpha channels and threshold-128 silhouettes are identical; foreground mean channel differences remain below 0.005/255. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `30edc8f1`. No existing model was regenerated or refined.
