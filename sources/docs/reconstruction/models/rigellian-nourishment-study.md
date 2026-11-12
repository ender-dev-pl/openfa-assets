# Rigellian Nourishment Bank RI03

Tracked in [#972](https://github.com/ender-dev-pl/ed-openfa-game/issues/972), relates to #948, #946 and reference milestone #970.

The independently authored editable Blend, standalone GLB and authored-only renders are in `docs/assets/reconstruction/buildings/rigellian/nourishment-bank/`. Identity is `openfa:building/legacy/042`, global type 42, definition class 37 and nominal footprint 2x2. The identity `PlacementRoot` sits at ground Z=0. Previous coarse models remain intact. Runtime scale/projection/orientation calibration remains open.

## Observed and inferred construction

The embedded-palette surface body and catalogue phases 0, 10, 20, 30 and 40 were inspected from `rigellian-building-references.json`. RI03 shows three rounded green sections, narrow gold interstage connections, a flared mounting foot, vertical pale equipment beside repeated body fittings, and a low front gold foot fitting. Catalogue phases reveal and highlight the same view; they do not establish hidden camera angles. Original pixels and the comparison sheet stay under ignored `artifacts/rigellian-building-reference-study/RI03/`.

Each process vessel is independently modelled with a shaped radial profile and actual shallow dents. Solid interstage necks overlap adjacent end caps. The repeated visible fittings are interpreted as machined service recesses with retaining returns and cooling louvres; their precise depth and internal equipment are inferred. Hidden rear closures, spine supports, screw/fastener layout, dimensions and material/wear details are authored interpretations, not recovered original engineering.

Revision 1 hid the low foot fitting inside the pedestal. Revision 2 exposes its pressure face while retaining an embedded back. Actual render comparison then identified the continuous spine on the wrong side of the repeated fittings and excessively square retaining edges. Revision 3 moves the spine to the reference-backed side and replaces four straight edge pieces per pocket with one continuous rounded machined return. The overall stack/foot proportions and gold necks are readable against the source. Further artistic review is still required for the pocket interpretation, gold-neck exposure and fine manufactured detailing.

## Surface wear and verification

`author_nourishment_wear.py` creates independent 1024x1024 colour/roughness maps with analytic joint contamination, handling marks, stains and deterministic scratches. It reads no original images. Maps are packed into the Blend and embedded by the GLB export. Explicit cylindrical UVs use V=Z/4.2 after clearing cutter-derived UV layers, avoiding implicit selection of a wrong map. `authored-wear.json` records authoring/image hashes.

`verify_rigellian_nourishment.py` reopens the source and imports GLB in actual Blender 4.5.15 LTS. It checks topology, positive closed-shell volumes, footprint/ground bounds, hierarchy, six material values, actual cut pocket depth, three measured dents, three neck/cap overlaps, the foot fitting's exposed and embedded faces, UV correspondence, packed image provenance and full decoded colour/roughness pixel preservation. A connected vertex/face-centre nearest-surface contact graph is diagnostic evidence, not exhaustive solid-intersection proof. Imported geometry is rendered using the native camera/light setup.

`review_rigellian_nourishment.py` checks six native 900x900 transparent views plus the imported-GLB view, at least 24 pixels of framing margin, native/imported foreground colour differences and exact alpha equality. It creates an authored-only gallery and the ignored reference comparison. Revision 3 contains 47 mesh objects and six materials; the sampled contact graph has one connected component in both formats. All native/imported and seven render checks passed. Top-cap cylindrical mapping still produces subtle radial material streaks in the close top view and is a further material-review item. No gameplay registration or renderer changed; no client runtime integration is claimed.

Final artistic acceptance, comprehensive contact assessment, construction/damage states, runtime placement/orientation and integration remain open. This is a registered reference-refined study, not a completed reconstruction.

## Revision 4: planar end-cap materials

The eight flat end surfaces (both ends of the three vessels and pedestal) now have a separate planar-XY material and independently authored 512x512 colour/roughness maps. Side walls retain cylindrical mapping and the existing 1024x1024 maps. A spatial cap field produces local rim contamination, soft stains, abrasion and fine variation without the angular fan distortion visible in revision 3. All four images are packed into the Blend and embedded in GLB; geometry, dents, pocket cuts, supports and footprint are preserved.

The verifier examines every mapped polygon loop in both formats, distinguishes actual extremal flat caps from side/pocket faces, checks planar coordinates against each end's actual radius, and requires all eight end planes. It verifies the complete colour and roughness pixels for both textured materials after glTF packing. The current source has 47 meshes and seven used materials. Topology, contacts, actual recess/dent/neck/foot-fitting checks and seven render checks pass again in Blender 4.5.15 LTS.

`artifacts/rigellian-building-reference-study/RI03/cap-mapping-comparison.png` compares the authored revision-3 and revision-4 top renders. The close-view radial streak item is resolved; a fine authored scuff and soft surface variation remain intentional. This material repair does not establish final artistic approval or resolve the other construction/state/integration questions above.
