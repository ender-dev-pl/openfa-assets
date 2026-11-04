# Scatter missile reconstruction study

Tracking: #962; relates to #951 and #946. PM04 management and runtime frames 0, 3, 6 and 9 are bound to archive/palette hashes in `missile-reference-index.json` (#958). Original pixels and meshes are reference-only.

## Observations and interpretation

The management preview resolves a slender gray/silver shaft, broad dark band below the head, tapered red nose, silver collar below a red tip and broad swept gold tail forms. Runtime frames preserve the gold tail region, dark band and red head at game scale but do not resolve construction or prove a turntable.

The gold forms are built as thick curved vanes, with upper/lower ends intersecting the shaft and an open middle clearance. Fourfold hidden vane count, exact cross-sections, pale thermal inserts, nozzle and shaft joints are authored interpretations. The original pale marks might instead be surface shading/wear; their conversion to small solid service inserts is not a confirmed legacy mechanism. No fin deployment, spin or independent articulation is asserted. Native nose axis is +Z, front is -Y and dimensions are uncalibrated authored units. Final artistic acceptance and gameplay scale/axes/socket integration remain open.

## Actual render iteration

Revision 1 established the distinct color regions, long shaft and custom varying-angle/radius gold vane lofts. Comparison with the management preview and four runtime frames found the gold surfaces too narrow. Native geometry passed, but imported GLB verification found degenerate triangles at the bevelled narrow vane ends.

Revision 2 broadens the swept gold forms and replaces the problematic bevel stage with explicitly closed curved surface construction at the vane ends. No tolerance or topology contract is relaxed. Actual views are regenerated and compared again, with front/oblique/nozzle views retaining the dark band, red/silver head and broader gold tail silhouette. Exact camera matching and the full lower-petal silhouette still require final artistic review.

## Deliverables and verification

`build_scatter_missile.py` produces editable named meshes/asset collection in Blend, standalone GLB, six transparent views and provenance under `docs/assets/reconstruction/missiles/terran/scatter/`. `verify_scatter_missile.py` reopens the source and imports GLB to examine positive closed volumes/nondegenerate topology, matching materials/bounds, all four actual 0.09-unit vane walls, eight upper/lower root/shaft intersections, embedded thermal inserts, measured bell wall and the entire open nozzle axis to the recessed throat. No external images or invented animation are present.

`review_terran_missiles.py --ids scatter` checks alpha/framing and writes the authored gallery plus the ignored reference sheet `artifacts/missile-reference-study/scatter-comparison.png`. Inventory regeneration/verification, Python compilation and changed-code-quality checks accompany this milestone. Blender generation/reopen/import exercises the asset target runtime; game rendering and bindings are unchanged.
