# Laser — first authored iteration (#1039)

`openfa:laser`, global equipment type 5: OrbitalWeapon, orbital damage 2, surface damage 1, value 1000. No mapped functional narrative, calibrated gameplay mount or cultural variant is established. This adds a missing first source while preserving previous reconstructions/refinements.

## Evidence and interpretation

PH05.VID supplies 60 correctly paletted 120×80 inventory rotation frames. All frames and enlarged 0/14/29/44 were inspected. They support a broad tapered front with thin terminal, elongated rear body, long red dorsal tube/copper lead, exposed dark side bay with three blue fittings and rear red details. Whole-object rotation does not establish independent aiming, recoil, launch or internal mechanisms.

The first source interprets the rear as a partial cylindrical shell with a real open angular sector, recessed lining/end walls and three separate fittings. Bay depth, insert sections/counts, wall thickness, front proportions, rear port construction and hidden surfaces remain interpretations. Coloured surfaces are rough/non-emissive; the name is not used to infer an optical pathway or moving barrel. AlignmentForward is an uncalibrated local -Y helper, not a registered gameplay mount. Equipment identity is global and does not establish cultural variants.

Video/decoded metadata, frame/palette hashes, reference/functional/gameplay indexes and authoring helpers are hash-bound. Original pixels remain reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine actual rendered views, gallery and technical reports. There are 35 closed meshes/six materials; three image materials cover fourteen meshes. Components comprise tapered nose/open rear shell/red dorsal tube, front stem/terminal, recessed lining/two end walls, three fitting bases/three blue fittings, two red rear ports/two dark inlays, two dorsal supports/copper lead and two service covers/four slots/eight fasteners.

The open rear shell is a finite-thickness closed casting with inner/outer walls and an actual missing side sector. The lining and inserts are separately editable behind that opening. Three primary profiles have physical dents. Six fitted overlays follow owner profiles; fasteners align to actual ray-sampled normals. Applied modifiers and primary triangulation precede box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and issue-seeded scratches provide new-object wear. Earlier sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded pixels, UVs/materials and three dents. Actual odd/even containment checks shell/endwall/lining/fitting/port/dorsal joins, 54 fitted-surface samples and eight fasteners. Four empty bay witnesses plus occupied recessed lining distinguish real depth from a dark overlay. AlignmentForward is tested under yaw, pitch and roll. Scoped samples do not establish exhaustive mechanical correctness or aiming/mount calibration.

The actual gallery and nine-frame source comparison were inspected. Nine views passed framing. Both matched alpha channels and threshold-128 silhouettes are identical; foreground mean RGB difference is below 0.001/255. Maximum corner-normal error is 0.000662. Measured dents are approximately 0.00476/0.00600/0.00197. Twenty-seven attachment contacts, 54 fitted-surface samples, eight fasteners and four bay-void witnesses passed. Full hardpoint reference verification passed sixteen definitions/144 palette-bound samples. Front/rear proportions, bay outline and surface layout remain provisional for deferred refining. Original comparisons remain ignored in `artifacts/issue-1039-laser/`; tracked views contain authored models only. Required changed-code quality base: `f5f60ed5`. Game-client integration is unchanged.

## Deferred

Final proportions, bay depth/sections, rear port/fitting layout/functions, hidden construction, cultural variants, runtime scale/orientation, mounts, aiming/recoil and damage states remain unresolved. Technical validity does not establish final artistic acceptance. Refining and construction scaffolding remain deferred.
