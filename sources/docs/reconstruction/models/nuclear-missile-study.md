# Nuclear missile reconstruction study

Tracking: #964; relates to #951 and #946. PM06 management and correctly paletted runtime frames 0, 3, 6 and 9 are bound to archive/palette hashes in `missile-reference-index.json` (#958). No original pixels, textures or meshes are incorporated into the source.

## Observations and interpretation

The reference resolves a dark tapered casing, long yellow tip, yellow trefoil marking, two visible silver upper side forms and red elongated lower pods with pale feet. Runtime frames preserve the yellow tip/mark, dark body and red lower cluster. The single management perspective does not establish the hidden pod count, fitting function or internal mechanism.

The study uses four lower pods with swept radial offsets and two visible upper silver forms; hidden fourfold tail placement and exact pod depth are authored interpretations. The trefoil is newly constructed geometry conforming to the casing, not sampled artwork. Casing profile, yellow tip and visible color regions guide the model; material response, pale feet and hollow nozzle construction are independently authored. No deployment, independent spinning assembly or internal mechanism is asserted. Native nose axis is +Z, front is -Y and units are uncalibrated. Final artistic acceptance and gameplay axes/scale/socket integration remain open.

## Actual render iteration

Revision 1 established the dark lofted casing, yellow tip, curved tail pod offsets and three solid trefoil sectors. Comparison of actual views with the management preview and four runtime frames exposed partly buried lower trefoil sectors and angular axial transitions on the red shells.

Revision 2 subdivides the trefoil surface in both angular and radial directions so all three marking faces follow the casing while their backs embed inside it. Swept red and silver side forms retain editable lofts with smooth evaluated subdivision skins. The native/imported verification examines actual face-center offsets above/below the casing rather than accepting object names or a successful export. Actual front/oblique/nozzle views were compared again; all three marking sectors are readable and the lower shells are rounded.

The previous bounds helper transforms local bounding-box corners, producing conservative envelopes for rotated subdivided pods that differ after export triangulation. This verifier measures the actual evaluated mesh vertices in world coordinates for both native and imported geometry, retaining the same 0.002-unit matching tolerance. It does not relax the geometry contract. Exact original camera matching and final proportions remain subject to artistic review.

## Deliverables and verification

`build_nuclear_missile.py` produces editable named meshes/asset collection in Blend, standalone GLB, six transparent views and provenance under `docs/assets/reconstruction/missiles/terran/nuclear/`. `verify_nuclear_missile.py` reopens Blend and imports GLB, checking topology, nondegenerate faces, positive closed volumes, matching materials/evaluated-vertex bounds, eight red-pod/casing root intersections, all three trefoil face/back offsets, declared fitting counts, measured bell wall and the complete clear nozzle axis to the recessed throat. No external images or invented animation are present.

`review_terran_missiles.py --ids nuclear` validates alpha/framing and creates the authored gallery and ignored reference sheet `artifacts/missile-reference-study/nuclear-comparison.png`. Inventory regeneration/verification, Python compilation and the repository changed-code-quality gate accompany the milestone. Blender generation/reopen/import exercises the asset target runtime; game rendering and bindings remain unchanged. Technical checks do not imply final artistic acceptance.
