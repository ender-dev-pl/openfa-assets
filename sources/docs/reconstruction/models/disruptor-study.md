# Disruptor — first authored iteration (#1034)

`openfa:disruptor`, global equipment type 1: SurfaceWeapon, surface damage 6, value 6000. No mapped functional narrative, calibrated gameplay mount or culture-specific geometry is established. This adds a missing first source while preserving earlier reconstructions/refinements.

## Evidence and interpretation

PH01.VID supplies 60 correctly paletted 120×80 inventory rotation frames. All frames and enlarged 0/14/29/44 were inspected. They support a tapered frontal body/aperture, large offset spherical mass, smaller rounded fitting, blue rear surfaces, angular side shields and copper connecting pipes. The presentation rotates the whole assembly; it does not prove independent aiming, recoil or an internal mechanism.

The first source interprets these as a tapered main housing with separate blue rear cap, full grey sphere with an offset blue rear cap, upper rounded fitting, spherical support, two angular shields, side red boss, front annular rim/blind backing, two curved copper pipes and fitted surface details. Profiles, counts, dimensions, hidden surfaces, blue material identity and functions remain interpretations. No visible component is assigned a proven internal subsystem. Coloured surfaces are rough and non-emissive. AlignmentForward is an authored local -Y helper, not a gameplay mount.

Equipment definitions are global; cultural architecture does not establish a race-specific Disruptor. Original images remain reference-only and absent from geometry/texture generation. Reference, functional and gameplay indexes, video/decoded metadata, frame/palette hashes and authoring helpers are hash-bound.

## Independent assembly

The asset directory contains editable Blend/GLB, six independent 1024-square colour/roughness maps, metadata, nine rendered views, gallery and technical reports. There are 38 closed meshes/six materials; three image materials cover seventeen meshes. Components comprise five profiled body/sphere/fitting/cap shells, spherical support, two shields, red boss, front annular rim/backing, two copper pipes, four fitted red fields and three service covers/six slots/twelve fasteners.

Three nonzero physical dents reside in the body, large grey sphere and upper fitting. The blue sphere cap sits 0.004 units outside the full grey sphere profile to avoid coincident surfaces; the overlap is an authored assembly detail. Copper pipes use directly authored circular ring sections and triangle-fan caps, avoiding conversion seams. Dense primary shells and pipe surfaces are triangulated before corner-normal capture. Thirteen fitted overlays follow owner profiles and fasteners align to actual ray-sampled normals. Applied modifiers precede authored box UVs. Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Existing models and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded pixels, UVs/materials and three dents. Actual odd/even containment checks body/cap/sphere/support/shield/rim/pipe joins, 117 fitted-surface samples and twelve fasteners. Ten pipe-interior witnesses check continuity; two empty front-axis samples and occupied backing preserve a blind recess. AlignmentForward is tested under yaw, pitch and roll. Scoped samples do not establish exhaustive mechanical correctness or aiming/mount calibration.

The actual gallery and nine-frame original comparison were inspected. Nine views passed framing. Matched native/imported alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.002/255. Maximum corner-normal error is 0.000595. Measured dents are approximately 0.00571/0.00388/0.00300. Thirty-five attachment contacts, 117 fitted-surface samples, twelve fasteners, ten pipe interior witnesses and the blind recess checks passed. Full hardpoint reference verification passed sixteen definitions/144 palette-bound samples. Original comparison pixels remain ignored in `artifacts/issue-1034-disruptor/`; tracked views contain authored models only. Required changed-code quality base: `21812675`. Game-client integration is unchanged.

## Deferred

Final profiles/proportions, sphere placement, shield and pipe layout, aperture depth, hidden construction, cultural variants, runtime scale/orientation, mounts, aiming/recoil and damage variants remain unresolved. Technical validity does not establish final art acceptance. Refining and construction scaffolding remain deferred.
