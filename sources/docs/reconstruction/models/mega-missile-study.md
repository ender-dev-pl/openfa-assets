# Mega missile reconstruction study

Tracking: #966; relates to #951 and #946. PM09 management and correctly paletted runtime frames 0, 3, 6 and 9 are bound to archive/palette hashes in `missile-reference-index.json` (#958). Original pixels and meshes remain reference-only.

## Observed form and authored interpretation

The management preview resolves a long gray cylindrical body, ivory nose cone, silver collar over a copper band, copper tip with short pin, long diamond-like side vanes and broad copper lower forms. Transverse marks are visible on the side vane. Runtime frames preserve the overall elongated body and pale regions but cannot resolve the vanes' hidden layout or their mechanism.

The study uses three radial vanes, three curved copper lower panels and authored transverse ribs/edge rails. Threefold hidden repetition, precise vane cross-section, rib count, copper relief and interior nozzle/mount are interpretations. No independent vane articulation or deployment is asserted. Native nose axis is +Z, front is -Y and dimensions are uncalibrated. Final artistic acceptance and gameplay scale/axes/socket integration remain open.

## Actual render refinement

Revision 1 supplied solid diamond vanes, transverse ribs/edge rails, pointed ivory nose and hollow copper nozzle. Comparison of actual front/oblique/nozzle renders with management and four runtime references found the overall width too narrow, the lower copper forms too small/capsule-like and the upper collar incorrectly copper.

Revision 2 widens the world transverse silhouette by fifteen percent, replaces the lower capsules with substantial curved double-wall copper panels that meet the casing, and makes the upper collar silver over the retained lower copper band. Six views were regenerated and compared again. The lower panels now wrap the base rather than appearing as isolated pods. Exact original camera matching, hidden vane count and final proportions remain pending artistic review.

## Deliverables and checks

`build_mega_missile.py` produces editable named meshes/asset collection in Blend, standalone GLB, six transparent views and provenance under `docs/assets/reconstruction/missiles/terran/mega/`. `verify_mega_missile.py` reopens Blend and imports GLB, checking nondegenerate topology/positive closed volumes, matching materials/evaluated-vertex bounds, three actual 0.0805-unit vanes, six vane/casing root contacts, three seated copper panels, silver collar contact, measured bell wall and full open nozzle path to the recessed throat. There are 64 mesh objects and five materials; these counts are structural evidence rather than artistic acceptance.

`review_terran_missiles.py --ids mega` validates all six alpha/framing bounds, writes the authored gallery and creates the ignored reference sheet `artifacts/missile-reference-study/mega-comparison.png`. Inventory regeneration/verification, Python compilation and the repository changed-code-quality gate accompany this milestone. Blender generation/reopen/import exercises the asset runtime; gameplay rendering and bindings are unchanged. No external images or invented animation are present.
