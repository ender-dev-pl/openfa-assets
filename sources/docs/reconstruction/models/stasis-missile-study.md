# Stasis missile reconstruction study

Tracking: #967; relates to #951 and #946. PM10 management and correctly paletted runtime frames 0, 3, 6 and 9 are bound to archive/palette hashes in `missile-reference-index.json` (#958). Original pixels and meshes remain reference-only.

## Observed form and interpretation

The management preview resolves a straight green casing, rounded head with short pin/red cap, pale upper band, thin pale joint and broad pale lower collar carrying maroon round marks. A red flared tail is exposed below the collar amid dark/light support details. Runtime frames confirm the long green body, pale bands and red tail region but cannot resolve a mechanism.

The round marks are authored as thin conformal color regions, not asserted to be open ports. Fourfold hidden mark count, the exact tail frame, annular mount/flange and nozzle interior are interpretations of an indistinct tail preview. No deployment or independently moving casing is asserted. Native nose axis is +Z, front is -Y and units are uncalibrated. Final artistic acceptance and gameplay axes/scale/socket integration remain open.

## Actual render refinement

Revision 1 supplied the casing, truly conformal marks and an open tail frame around a hollow red bell. Comparison of actual front/oblique/nozzle renders with the management preview and four runtime frames found the body too slender and the red bell too narrow relative to the collar.

Revision 2 increases world transverse width by eighteen percent and widens the bell's lower profile. The source management crop is 27 by 143 pixels, supporting the need to broaden the first study rather than add decorative surface detail to its plain casing. All six views were regenerated and reviewed again. Exact original camera/projection matching and the detailed original support layout remain pending artistic review.

## Deliverables and verification

`build_stasis_missile.py` produces editable named meshes/asset collection in Blend, standalone GLB, six transparent views and provenance under `docs/assets/reconstruction/missiles/terran/stasis/`. `verify_stasis_missile.py` reopens Blend and imports GLB to check topology/nondegenerate faces/positive volumes, matching materials/evaluated-vertex bounds, seated bands, all four conformal mark face/back offsets, eight actual brace contacts with the bell and mount, measured bell wall and the complete clear nozzle axis to its recessed throat. There are 28 mesh objects and six materials; these counts do not establish artistic acceptance.

`review_terran_missiles.py --ids stasis` checks all six alpha/framing bounds and creates the authored gallery plus ignored reference comparison `artifacts/missile-reference-study/stasis-comparison.png`. Inventory regeneration/verification, Python compilation and changed-code-quality checks accompany the milestone. Blender generation/reopen/import exercises the asset runtime; gameplay rendering/bindings are unchanged. No external images or invented animation are present.
