# Vortex missile reconstruction study

Tracking: #963; relates to #951 and #946. Correctly paletted PM05 management and runtime frames 0, 3, 6 and 9 are bound to archive/palette hashes in `missile-reference-index.json` (#958). Original images and meshes remain reference-only.

## Observations and interpretation

The management view resolves a rounded violet upper casing, oval side forms near its head, silver middle shaft, red side panel, violet lower casing and an exposed gold tail region. The casing edges curve diagonally around the shaft; these are built as actual thick wavy boundaries, not dark masks. Runtime frames preserve the silver/violet regions, red middle feature and gold tail at tiny game scale; they do not establish hidden construction or deployment animation.

Exact rear wave profiles, side-form depths/placement, internal support rings, service fasteners/latch and fluted gold nozzle are independently authored interpretations. The gold tail's function is interpreted as propulsion construction; no source-backed nozzle mechanism is claimed. The unseen rear is left without a duplicate red panel. Two oval head forms are modelled to match the visible pair without asserting a ring of hidden duplicates. Native nose axis is +Z, front is -Y and units are uncalibrated. Final artistic acceptance, gameplay axes/scale/socket transforms and integration remain open.

## Actual render iteration

Revision 1 supplied the thick variable-height casing shells, oval side forms, silver shaft, curved red service surround and gold propulsion cavity. Comparison of six actual views with management and four runtime frames found the silver shaft too thin and the gold lower region too concealed.

Revision 2 widens the shaft, seats its curved service frame/inset/latch, raises the lower cut edge and expands the exposed gold liner. Two internal annular supports connect the shells to the shaft; an open flange connects the nozzle to its mount without obstructing its axis. The liner has authored flutes/ribs instead of a featureless gold disk. Actual front, oblique and nozzle renders were reviewed again. Precise original camera matching and final interpretation of the lower gold region remain pending.

## Deliverables and verification

`build_vortex_missile.py` produces the editable named meshes and asset collection in Blend, standalone GLB, six transparent views and provenance under `docs/assets/reconstruction/missiles/terran/vortex/`. `verify_vortex_missile.py` reopens the source and imports GLB, testing topology/nondegenerate faces/positive volumes, matching materials and bounds, the actual varying-height casing edge, both 0.06-unit walls, support intersections with shaft and shells, curved panel seating, open flange, bell wall thickness and the complete axial path to the recessed throat. No external images or invented articulation are present.

`review_terran_missiles.py --ids vortex` checks all six alpha bounds and creates the authored gallery plus ignored reference comparison `artifacts/missile-reference-study/vortex-comparison.png`. Inventory regeneration/verification, Python compilation and the repository changed-code-quality gate accompany this milestone. Blender generation/reopen/import is the exercised asset runtime; gameplay rendering and bindings are unchanged. Technical success does not mark the model finally accepted.
