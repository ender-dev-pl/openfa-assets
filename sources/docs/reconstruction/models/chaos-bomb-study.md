# Chaos Bomb — first authored iteration (#1037)

`openfa:chaos-bomb`, global equipment type 3: SurfaceWeapon, surface damage 12, value 12000. No mapped functional narrative, calibrated 3D gameplay mount or cultural variant is established. This adds a missing first source while preserving prior reconstructions/refinements.

## Evidence and interpretation

PH03.VID supplies 60 correctly paletted 120×80 inventory rotation frames. All frames and enlarged 0/14/29/44 were inspected. They support a larger cylinder bank in three tiers, a smaller triangular three-cylinder bank, red rounded ends, central support, upper rectangular bracket and thin warm lower rails. The full rotation guides a six-cylinder larger bank (two per tier), opposed to a three-cylinder smaller bank. This 6+3 opposed layout is a first-source interpretation, not recovered dimensional/mechanical data. Exact spacing, profiles, orientation, hidden construction and cylinder functions remain unresolved.

The model keeps nine cylinders, nine end caps and nine collars separately editable. The upper bracket is open, and actual gaps separate columns/tiers. Whole-object inventory rotation does not establish a turret, launch/recoil mechanism or mechanical hinge. AlignmentForward is an uncalibrated local -Y helper, not a gameplay mount. Colours are non-emissive. Global equipment identity does not establish seven cultural variants; architectural prose is not used to invent one.

Video/decoded metadata, sampled frame/palette hashes, reference/functional/gameplay indexes and authoring helpers are hash-bound. Original pixels remain reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine actual rendered views, gallery and technical reports. There are 55 closed meshes/five materials; three image materials cover 37 meshes. Components comprise eighteen profiled cylinders/caps, nine collars, central support, two bracket uprights/top, three lower rails, three fitted covers/six slots/twelve fasteners.

Each of the nine grey cylinders has a shallow physical dent. Separate red ends retain overlapping roots. Nine fitted overlays follow actual owner profiles; fasteners align to ray-sampled normals. Applied modifiers and primary triangulation precede authored box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Existing assets and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded pixels, UVs/materials and nine dents. Actual odd/even containment verifies cylinder/cap/collar/support/bracket/rail joins, 81 fitted-surface samples and twelve fasteners. Eight tier-gap witnesses and two bracket voids preserve the three-dimensional arrangement; occupied tube roots verify their support. AlignmentForward is tested under yaw, pitch and roll. Scoped samples do not establish exhaustive mechanical correctness or gameplay mount/animation calibration.

The actual gallery and nine-frame source comparison were inspected. Nine views passed framing. Both matched threshold-128 silhouettes are identical; foreground mean RGB differences are below 0.003/255. Front-quarter alpha differs at one pixel by 4/255, within the existing threshold; detail alpha is identical. Maximum corner-normal error is 0.000575. Nine measured dents range approximately 0.00244�0.00326. Seventy-three assembly contacts, 81 fitted-surface samples, twelve fasteners, eight tier-gap and two bracket-void witnesses passed. Full hardpoint reference verification passed sixteen definitions/144 palette-bound samples. Central support thickness, cap profiles and spacing remain provisional for the deferred refining pass. Original comparison pixels remain ignored in `artifacts/issue-1037-chaos-bomb/`; tracked views contain authored models only. Required changed-code quality base: `d0602f97`. Game-client integration is unchanged.

## Deferred

Final bank layout/proportions, cylinder/end/bracket profiles, lower rail detail, hidden construction, cultural variants, runtime scale/orientation, mounts and launch/damage states remain unresolved. Technical validity does not establish final artistic acceptance. Refining and construction scaffolding remain deferred.
