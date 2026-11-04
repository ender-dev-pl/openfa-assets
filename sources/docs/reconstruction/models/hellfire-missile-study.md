# Hellfire missile reconstruction study

Tracking: #961; relates to #951 and #946. Correctly paletted PM03 management preview and runtime frames 0, 3, 6 and 9 are indexed with archive/palette hashes in `missile-reference-index.json` (#958). Original imagery is reference-only; the source imports no pixels or meshes.

## Observations and interpretation

The management preview resolves a silver fusiform casing, long tapered nose, small red tip, red side patch, large oval lower side form and dark vertical fitting with a wider upper end. The runtime frames confirm a long silver body and red tip at game scale. They do not prove the side fitting's function, hidden symmetry, a rear-facing duplicate or independently moving assemblies.

The oval form is interpreted as raised casing relief rather than a colored decal. Its exact depth and perimeter are authored. The unseen side is left plain; no mirrored fitting or invented weapon barrel is asserted. Nose/tail seam construction, hidden nozzle, material response and dimensions are authored interpretations. Native nose axis is +Z, front is -Y and units are uncalibrated. Final artistic acceptance, gameplay scale/axes, mounting transforms and integration remain open.

## Render comparison and refinement

Revision 1 produced a recessed port, separate oval form, long nose and hollow nozzle. Actual render comparison with the management preview and four runtime frames showed an overly narrow body, too-small oval relief and an overly regular capsule-shaped port.

Revision 2 widens the casing by 14 percent in world transverse axes, enlarges and lengthens the oval form, follows casing curvature with a smooth elliptical relief and gives the actual cut port a wider upper bulb. Render review caught an incorrect local-axis width transform displacing rotated rings; scaling now operates on world-space mesh coordinates and the nose seam's seating is checked by intersections. A smoothed Boolean cutter produced invalid edge fans; it was replaced with explicit controlled loft geometry instead of relaxing topology checks. Both changes were rerendered and reverified. Side-view review also exposed a raised identification disk; it was replaced with a thin conformal marking with a back surface embedded in the nose skin, checked against actual nose intersections.

The clean authored metal response remains an interpretation of the original's irregular shading; surface detail is concentrated on observed forms rather than adding decorative greebles to the plain silver casing. Exact camera matching and final per-asset acceptance are still pending.

## Sources and verification

`build_hellfire_missile.py` writes the editable asset collection, standalone GLB, six transparent views and provenance under `docs/assets/reconstruction/missiles/terran/hellfire/`. `verify_hellfire_missile.py` reopens the native file and imports GLB, checking actual topology/materials/bounds, recessed keyhole depth and upper/lower widths, substantial oval relief, nose seam seating, bell wall thickness and the full unobstructed nozzle axis to the throat. No external image dependencies or invented animation are allowed.

`review_terran_missiles.py --ids hellfire` checks all six render alpha bounds and creates the authored gallery plus ignored reference comparison at `artifacts/missile-reference-study/hellfire-comparison.png`. Catalogue inventory is regenerated/verified, Python sources compiled, and the repository quality gate run against the preceding milestone. This change does not modify the game renderer or bindings; Blender generation/reopen/import is the exercised target runtime.
