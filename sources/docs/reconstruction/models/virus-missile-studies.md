# Virus and Anti-Virus missile reconstruction studies

Tracking: #965; relates to #951 and #946. PM07/PM08 management previews and correctly paletted runtime frames 0, 3, 6 and 9 are bound to raw archive/palette hashes in `missile-reference-index.json` (#958). Original pixels and meshes remain reference-only.

## Evidence and distinct variants

Virus resolves two vertically aligned rows of bronze oval side forms, an olive casing, yellow band below the red tip, long thin antenna and a flared olive/violet skirt above a red tail cluster. Anti-Virus resolves one larger violet side-equipment row, a different long-neck casing, pale nose band, shorter antenna and similar lower skirt/tail color regions.

The decoded runtime geometry/pixels are identical for these two definitions. Their management previews differ and do not justify reducing them to one mesh with a material swap. Both independently generated sources have separate body profiles, equipment counts/placement, bands and antenna lengths. The verifier asserts the shared runtime shape hash, distinct management source hashes and distinct native model hashes/antenna heights.

Fourfold hidden side repeats, skirt scallops around the unseen side and four hollow red tail nozzles are authored interpretations. The original tail's function and nozzle count are not proven by the preview. Exact dimensions, material response, equipment depth/function and internal propulsion are unresolved. Native nose axis is +Z, front is -Y and units are uncalibrated. No independently animated pod, antenna or deployment mechanism is invented. Final artistic acceptance and gameplay scale/axes/socket integration remain open.

## Actual render iteration

Revision 1 supplied body-following oval relief, olive/violet scalloped skirts, distinct collars/antennas and four hollow red tail tubes. Comparison of actual views with both management previews and runtime frames found the bodies too slender and Virus bronze forms too small.

Revision 2 widens both models by ten percent in world transverse coordinates, enlarges/lengthens both Virus equipment rows, deepens violet skirt openings and darkens the olive material. Actual front, oblique and nozzle renders were regenerated and compared again. Both models retain their observed one-row versus two-row distinction and differing nose bands. Precise original camera matching and final proportions remain for artistic acceptance.

## Deliverables and checks

`build_virus_missiles.py` produces editable named meshes/asset collections, standalone GLB, six transparent views each and provenance under `docs/assets/reconstruction/missiles/terran/virus/` and `anti-virus/`. `verify_virus_missiles.py` reopens native sources and imports both GLBs, checking nondegenerate topology/positive closed volumes, material/evaluated-vertex bounds, actual side-equipment/casing contacts, true scallop height variation, 0.066-unit skirt walls and four full open nozzle axes to recessed throats with measured tube walls. It also checks distinct source/model identities and antenna lengths.

`review_terran_missiles.py --ids virus,anti-virus` checks all twelve alpha/framing bounds, writes authored galleries and `virus-family.png`, and generates ignored reference sheets under `artifacts/missile-reference-study/`. Inventory regeneration/verification, Python compilation and changed-code-quality checks accompany the milestone. Blender generation/reopen/import exercises the asset runtime; gameplay rendering and bindings are unchanged. Passing checks does not assert final artistic acceptance.
