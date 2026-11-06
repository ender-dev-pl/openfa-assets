# Combat Eagle and Scoutship — reference-based studies

Issue #954, within #949 / #946. Both ships have independent editable sources,
standalone GLB exports, six review views and 32 fixed-scale heading samples in
their respective `combat-eagle/` and `scoutship/` directories. The source art is
reference-only: no legacy pixels, textures or geometry are distributed here.
These are incomplete high-detail reconstructions, not accepted final assets.

## Evidence and observed construction

Correctly paletted PS01.VID and PS02.VID frames 0, 15, 30, 45 and 59 were reviewed
with the mapped surface samples recorded in the ship-reference index. The
Combat Eagle has a pointed central hull, a raised dorsal form, broad swept wings
with red segmented identification regions, and small underslung rear drives.
The model uses independently authored longitudinal pressure-hull sections,
separate swept structural wings, enamel segments, exchanger packs, inspection
hardware and hollow drive throats. A second render iteration clips the formerly
square wingtip corners, following the more tapered reference outline.

The user rejected that Combat Eagle study because its silhouette read as an
aircraft, missing the original's Y planform and deep inter-wing notch. Revision 3
replaces that planform: the central hull ends much earlier, both wings become
long swept rear arms, and their inner edges diverge around a deep open bay.
Associated radiator fittings and fasteners were moved onto the shortened spine.
The rejected renders remain in ignored
`artifacts/ship-reference-study/combat-eagle-rejected-aircraft/`.
The verifier ray-tests twelve points through the actual central negative space
to prevent a filled aircraft-like planform returning. This structural invariant
does not replace the remaining visual proportion and detail review.

The user then supplied an annotated top view showing missing body area behind
the swept leading edges. Combat Eagle revision 4 widens both rear arms out to
the trailing edge while retaining the deep central notch; the previous thin
diagonal strips are superseded. The inner outline curves outward gradually,
giving a much broader rear wing body. Wing thickness now tapers from a thicker
root to the tip, and service packs follow the revised upper surface.
Eight positive geometry rays cover the newly required body area in addition to
the twelve negative-space rays. Both invariants apply to native and imported
geometry. The previous thin-Y renders remain in ignored
`artifacts/ship-reference-study/combat-eagle-thin-y/`.

The Scoutship has a fan-shaped broad aft hull, long raised oval crown, curved red
shoulder bands, two rear drives, a recessed neck and separate small forward pod.
Paired antenna fittings beside the neck are visible in its rotation. Its model
uses explicit elliptical section profiles for these separate volumes, rather
than reusing the Eagle's hull. Crown, shoulder and side access panels follow
their underlying pressure-skin cross sections.

## Render-driven corrections

The first Scoutship renders showed flat crown plates intersecting the curved
shell and partly standing clear of it. Its side belts also stood above the hull.
Those details were rebuilt as thin solid patches with sampled longitudinal and
transverse curvature. The nose service cover had the same problem and was
replaced by a conformal patch. An enlarged comparison then exposed a more
important misreading: the original oval crown contains a dark recessed centre
with bright inner-edge fittings, rather than being a solid dome. Scoutship
revision 3 cuts a real oval well, adds a recessed equipment floor, limits covers
to the rim and includes fourteen silver inner-edge elements. Internal cartridges
and cooling slots are authored mechanical interpretation. Ray tests confirm the
well extends below the surrounding shell. Boolean section intersections produced
degenerate slivers; explicit triangulation and small-scale degenerate-edge cleanup
fixed these while preserving strict native/imported face-area checks.
Final side/top renders were inspected after the changes. First-iteration images
remain under ignored artifacts for comparison.

Reference comparison sheets are retained at
`artifacts/ship-reference-study/combat-eagle-comparison.png` and
`artifacts/ship-reference-study/scoutship-comparison.png`. They contain original
pixels and must remain reference-only. The committed galleries contain only the
new authored models. These are qualitative multi-view comparisons; the camera
poses have not been quantitatively registered to the originals.

## Verification and limits

`verify_terran_light_ships.py` opens each Blend and reimports its standalone GLB.
It checks structural features, material assignments, nonempty and nondegenerate
faces, loose edges/non-manifold fans, positive closed-shell volumes, matching
evaluated bounds, and absence of external image dependencies. Hash-bound results
are stored in each model's `technical-review.json`.

`review_terran_light_ships.py` checks all 38 images per model for RGBA transparency,
768×768 dimensions and at least 20 pixels of unclipped margin. Direction metadata
must match the current Blend hash. It writes authored galleries and a hash-bound
render review. Actual modelling, rendering and export/import checks run in
Blender 4.5.15 LTS. No gameplay code or registration changes are included.

Exact physical dimensions, hidden underside structure, nozzle internals, access
panel divisions and fasteners are authored interpretation. The designer's 2D
mount coordinates are not treated as 3D sockets. No weapon socket or firing arc
is invented or registered by this milestone.

Still required before final acceptance: matched-camera silhouette/proportion
review, further close-up surface and mechanical refinement, stronger evidence for
weapon mounts and hidden geometry, calibrated heading/projection/scale in the
actual client, and explicit visual acceptance tied to exact final revisions.
Broad plain surfaces and simple manufactured fittings remain visible; successful
exports and object counts do not establish the requested final detail quality.
The programme review ledger remains unchanged, with final gates open.

## Reproduce

Run `build_terran_light_ships.py` in Blender to author both models. Then run
`verify_terran_light_ships.py` and run the builder with `--directions-only`.
Finally run `review_terran_light_ships.py` in the Pillow-enabled Python runtime.
An optional `--ids combat-eagle` or `--ids scoutship` restricts builder work.
