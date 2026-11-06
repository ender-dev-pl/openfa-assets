# Rigellian gold crown refinement

Part of [#185](https://github.com/ender-dev-pl/openfa-assets/issues/185).
This is the first focused geometry milestone, covering RI01, RI04, RI05, RI06
and RI17. It does not finish the complete buildings, ships or missiles pass.

## Reference decision

Correctly paletted surface bodies and readable catalogue phases show gold
lateral arms which broaden below their tips, with a longer middle stem. The
previous RI01/04/05/06 studies reduced these arms to bent rods of constant
section. RI17 had a single bulb/spike and lacked the lateral arms entirely.
Silver open rod crowns on RI07/08 were deliberately retained: the evidence for
those differs from the gold crown family.

The new studies replace those lateral parts with separate closed tapered arms.
Their widest lower cheeks, narrow tips and open intervals beside the middle
stem remain readable from the normal catalogue camera. RI17 receives the
missing lateral arms and a continuous tapered middle stem. Exact cross-sections,
hidden thickness and absolute dimensions remain independently authored fits.
No movement is inferred from these catalogue reveal/highlight sequences.

Each newly authored arm has a small geometric surface depression, softened
casting edges and original packed colour/roughness maps with restrained joint
dirt, handling scratches and rubbed regions. Original pixels are references
only. Existing body surfaces and their materials were not retrofitted. Existing
sources and all previous studies remain intact.

## Actual verification

`verify_rigellian_crowns.py` reopens the original and new native sources, then
imports the standalone GLB after discarding source mesh/material datablocks.
Every retained body object's world-space geometry, named material bindings and
parent hierarchy are compared. Added arms must have closed positive welded
topology, a measured broad-middle/narrow-tip ratio above 2.6, actual upper fork
clearance, a UV layer and a preserved identity placement root. Export vertex
splits at UV/normal seams are welded for the physical topology check.

| Study | Unchanged body mesh objects | Maximum native/GLB position error | Largest paired RGB mean difference / 255 |
| --- | ---: | ---: | ---: |
| RI01 | 73 | 0.000001565 | 0.077 |
| RI04 | 54 | 0.000001476 | 0.266 |
| RI05 | 39 | 0.000001467 | 0.157 |
| RI06 | 45 | 0.000001565 | 0.291 |
| RI17 | 20 | 0.000001014 | 0.273 |

All retained body vertex errors are zero. Independently reopened native and
imported GLB renders were generated at 768×768 for both the whole model and
crown detail. All ten paired thresholded silhouettes match exactly (IoU 1.0).
The five whole-model renders and crown detail pairs were visually inspected;
the earlier source comparison sheets were used for the shape decision.

RI17's tapered centre exposed a real native/export render discrepancy before
registration. Explicitly triangulating the authored stem before export resolved
it: the detail RGB mean difference fell from 10.19 to 0.009/255 without relaxing
the render threshold. Direct diagnostic comparisons found matching texture
pixels and UVs, so texture colours were not changed to conceal the discrepancy.

The new source folders are `sources/docs/assets/reconstruction/rigellian-refined/ri01`,
`ri04`, `ri05`, `ri06` and `ri17`. Their editable Blend, standalone GLB and metadata
are separate from prior reconstructions. Actual renders and SHA-bound validation
reports are under the matching `gallery/media/` paths. Shared authored maps are
under `sources/materials/reconstruction/rigellian-refined/crowns/`.

The gallery adds five separately selectable refinement studies. These five
models are static; existing RI10/RI18 animations and all gallery video manifests
remain unchanged. Final artistic acceptance and game integration remain open.
