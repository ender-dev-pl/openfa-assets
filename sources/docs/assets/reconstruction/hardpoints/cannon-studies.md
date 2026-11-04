# Photon and Plasma Cannon reconstruction studies

Issue #957 within #950 / #946; paletted reference evidence is indexed under #955.
These are independent editable equipment sources, not finally accepted models.
Each folder contains Blend, standalone GLB, seven transparent review views and an
authored gallery. Legacy frames appear only in ignored comparison sheets at
`artifacts/hardpoint-reference-study/<name>-comparison.png`.

## Observed structure and iterations

PH06 shows a low broad cover, central circular cap, paired long thin forward
projections and a rectangular rear equipment unit with red-ended connectors.
Photon Cannon preserves that construction. First-render comparison showed overly
thick barrels; they were narrowed and lengthened. Bore interiors, collars, captive
fasteners, cooling passages and conductor routing are authored interpretation.

PH07 shows a thicker rounded wedge-like housing, red ribbed flanks, single front
assembly, raised top fitting and a large dark rear aperture. The first authored
body was too cylindrical and tall. Actual render review prompted a lower,
clipped wedge casing with a corresponding cover/perimeter, instead of a generic
round can. Further comparison shortened the oversized front assembly and added
the visibly metallic rear service face and corner guards. The rear aperture is
cut through both casing and rear plate and has a connected hollow
sleeve and recessed dark stop. It is not a dark circle painted on a solid wall.
The service hatch and internal bore dimensions are authored fine construction,
not established by the source pixel resolution. Initial Plasma views remain in
`artifacts/hardpoint-reference-study/cannon-revision-1/`.

## Verification

Blender 4.5.15 LTS builds and renders both actual sources. Native and reimported
GLB checks verify nonempty/nondegenerate materialled geometry, closed-shell
positive volumes, loose/non-manifold-edge checks, matching bounds and six
materials, open barrel axes and actual rear-port penetration. Technical reports
bind these results to exact source/export hashes. Render review checks all
fourteen images for 768×768 RGBA, transparent background and at least 20 pixels
of unclipped margin. Original image/mesh dependencies are absent.

No independent turret head, elevation joint or recoil animation is invented.
Inventory rotation alone does not prove such mechanics. Cultural variations,
3D ship sockets, aiming semantics and mounted projection/scale remain unresolved.
Matched-camera silhouette/proportion review and further high-detail surface and
mechanical refinement remain open; native export success is not final artistic
acceptance. The programme review ledger and all final gates remain unchanged.

Run `build_cannon_equipment.py` and `verify_cannon_equipment.py` in Blender, then
`review_cannon_equipment.py` with Pillow. No gameplay registration/code changes
are included in this milestone.
