# Warp Generator â€” first authored iteration (#1041)

`openfa:warp-generator`, global equipment type 9: Special, value 9000, orbitalEvasionPercent 50. These are gameplay catalogue facts; they do not establish a physical mechanism. The functional-text index locates the name only, with no mapped narrative. Relates to hardpoints #950 and overall programme #946. This fills a missing first source and preserves previous models/refinements.

## Source evidence and interpretation

All 60 correctly paletted PH09.VID inventory frames and enlarged 0/14/29/44 were inspected. They show a flared domed end with circular terminal and visible surface divisions, a cylindrical middle, copper-coloured connectors and an opposite rounded module with two yellow bands and a circular terminal. Whole-object rotation does not establish independent motion, aiming, recoil or operating mechanisms. Shared equipment has no established race-specific geometry; cultural architectural descriptions cannot override this reference.

The model interprets these as three profiled closed bodies, four axial copper connectors and sleeves, four fitted dome sectors, two conforming yellow annuli and separately editable terminal bezels/inlays/studs. Connector count, hidden structure, dome segmentation, band widths, terminal construction and exact profiles are authored interpretations. Two fitted service covers/four slots/eight fasteners are authored manufacturing detail. No discharge, propulsion or operating animation is invented. AlignmentForward is an uncalibrated local -Y helper, not a recovered gameplay mount.

Reference video, decoded metadata and canonical PNG/palette hashes are checked against the authoritative hardpoint index. Model metadata binds the functional/catalogue indexes, wear and authoring helpers. Legacy pixels remain reference-only, absent from geometry and texture generation inputs.

## Editable first assembly

Deliverables comprise editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine actual renders, gallery and scoped technical reports. The assembly has 41 closed meshes, five materials, three image materials and 17 mapped meshes. Three primary bodies have geometric dents. Two yellow annuli overlap the actual rear profile. Dome sectors are finite fitted castings with smooth curved skins and sharp edge walls; a first-render faceting defect was corrected before milestone verification. Primary/annular/sector triangulation and applied modifiers precede UVs and explicit corner-normal capture. Analytic grime/stains/grain and issue-seeded scratches provide independent wear.

## Verification and review

The standalone modelling runtime uses Blender 4.5.15 native reopen and independent GLB import/render. Verification covers closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6 imported seam welding, explicit corner normals, source/helper hashes, packed bytes/decoded map pixels, box UVs/materials, hierarchy/transforms/bounds and three measured dents. Actual odd/even containment checks body/connector/sleeve/band/terminal joins, fitted sectors/covers/slots and fasteners; four empty connector-interval witnesses prevent a filled replacement body. AlignmentForward is exercised under yaw/pitch/roll. Meshes have no animation; operating motion remains unestablished. Scoped probes are not exhaustive mechanical or calibrated-mount acceptance.

Native reopen and independent GLB import/render passed. Measured dents are approximately 0.00600 / 0.00396 / 0.00500; maximum corner-normal export error is 0.000628. Forty-five assembly contacts, 90 fitted-surface samples, eight fasteners and four connector-gap witnesses passed. Both matched alpha channels and threshold-128 silhouettes are identical; maximum mean foreground RGB difference is below 0.001/255. Nine views passed framing. Full hardpoint reference verification passed 16 definitions / 144 palette-bound samples.

The actual gallery and source comparison were inspected. The opposite rounded module is more elongated and less spherical than the source; dome curvature/segmentation, connector proportions and terminal detail are simplified. These explicit artistic gaps remain for the deferred refining pass. Comparison pixels stay ignored in `artifacts/issue-1041-warp-generator/`; tracked images contain authored models only. Required changed-code quality base: `bfb7da92`. Game-client integration is unchanged.

## Deferred acceptance

Final profile curvature/proportions, dome segmentation, connector count and sleeve placement, band widths, terminal detail/functions, hidden construction, runtime scale/orientation, calibrated mounts, cultural variants, operating/damage states and final artistic acceptance remain unresolved. Technical validity does not accept final art. Further artistic refining and construction scaffolding remain deferred by user direction.
