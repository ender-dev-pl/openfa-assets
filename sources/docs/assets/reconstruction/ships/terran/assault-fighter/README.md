# Terran Assault Fighter — reconstruction study, revision 3

Issue #953, within #949 / #946. This is an independently authored editable model,
not a finished or accepted high-detail reconstruction. No legacy pixels, textures,
or meshes are included. The available source views are indexed in
`docs/reconstruction/models/ship-reference-index.json`.

`model.blend` contains an asset collection and orthographic transparent render rig.
`model.glb` is a standalone material/geometry export. `gallery.png` contains six
authored views; `directions/` contains 32 fixed-scale camera orbit samples.
These orbit images are review exports: gameplay heading/projection alignment is
not calibrated, so they must not silently replace runtime sprites.

## Observed features and iterations

The PS00 inventory rotation shows the pointed delta footprint, vermilion swept
bands, raised dorsal form, dark dorsal wells, rear hump, and bronze drive ends.
The tiny PS0A surface images are secondary silhouette checks. Hidden underside
structure, nozzle internals, panel divisions and fasteners are authored inferences.
Physical dimensions and three-dimensional weapon sockets are not established.

Revision 1 had an overly long, flat shell and raised louvre disks. Actual Blender
renders exposed these discrepancies. Revision 2 shortens the planform in Y,
rebuilds the dorsal shell with shaped cross sections, cuts four actual elliptical
pockets, recesses their louvres, and adds the observed aft pressure fairing.
Revision 3 adds silver outer-drive fairings observed in frames 5, 20, 40 and 50.
It replaces overlapping wing panels with twelve separate ruled-surface plates
and narrow seam gaps. Their subdivision and captive fasteners are authored
manufacturing detail, not a claim of exact legacy panel topology.
Side-view review exposed unsupported space below the sloping plates; continuous
load-bearing wing webs now connect their undersides to the pressure hull.
Closed-shell signed-volume checks exposed inward-oriented wing panels;
generation now explicitly orients closed shells outwards after normal recovery.
Native and reimported meshes pass positive-volume, non-manifold-fan and loose-edge
checks. Directional metadata binds the render set to the exact Blend hash.

The original iteration images remain in ignored artifacts. A comparison sheet
with correctly paletted legacy frames is retained at
`artifacts/ship-reference-study/fighter-comparison.png`; it is reference material,
not distributed art. Views are a qualitative comparison, not camera registration.

GLB reimport initially exposed degenerate triangulation on thin bevelled disks.
Chamfers now scale to the smallest local dimension. Native and imported geometry
checks pass, including four ray-tested recessed wells, four open exhaust axes,
seven materials, matching evaluated bounds and no external image dependencies.
All 38 single-view/directional images have transparent backgrounds and at least
20 pixels of unclipped margin at 768×768. Tests ran in Blender 4.5.15 LTS.

## Remaining refinement and acceptance

- Match camera orientation to representative rotation frames for quantitative
  silhouette/proportion checks; current views are not matched cameras.
- Refine dorsal curvature, engine housings, wing surface segmentation and the
  aft transition. Several surfaces still read as broad simple slabs; successful
  export and 150 mesh objects do not satisfy the high-detail art requirement.
- Resolve the appearance of dorsal openings against additional frames before
  freezing their exact profile and arrangement.
- Establish weapon socket transforms from stronger evidence and validate mount
  clearance. No invented socket is registered by this study.
- Calibrate directional renders and scale in the actual client before integration.
- Verify normals/topology and material treatment in close-up after further
  geometric refinement, and explicitly review the exact final model revision.

The programme review ledger remains unchanged; every final acceptance gate is
still open. No gameplay rendering or registration changed in this milestone.

## Reproduce

Run `tools/blender/build_assault_fighter.py` in Blender, then
`verify_assault_fighter.py` and `render_assault_fighter_directions.py`.
Run `review_assault_fighter.py` with Pillow after rendering. The latter uses
ignored source reference exports and the preserved first-iteration images.
Technical reports are retained under `artifacts/ship-reference-study/`.
