# Vortex Mine — first authored iteration (#1038)

`openfa:vortex-mine`, global equipment type 4: SurfaceWeapon, surface damage 5, value 5000. No mapped functional narrative, calibrated gameplay mount or cultural variant is established. This adds a missing first source; existing reconstructions/refinements remain unchanged.

## Evidence and interpretation

PH04.VID provides 60 correctly paletted 120×80 inventory rotation frames. All frames and enlarged 0/14/29/44 were inspected. They support an elongated segmented cylinder, tapered front with a blue end field, small lateral red/grey fittings, clipped rear collar and red rear terminations. Source form is cylindrical rather than a flat disk. Whole-object inventory rotation does not establish aiming, deployment, recoil or a mine-launch mechanism.

The first source uses central casing, separate tapered nose/red rear ends, three annular sleeves, front rim/blue backing, fitted side bezels/red inserts, lower side bosses/tips and a bevelled octagonal rear collar. Segment counts, exact clipping, profiles, small rear detail, blind-front depth and hidden surfaces remain interpretations. Colours are rough and non-emissive; no visible part is assigned proven engine, sensor or internal subsystem function. AlignmentForward is an uncalibrated local -Y helper, not a gameplay mount. Global equipment identity does not establish cultural variants.

Video/decoded metadata, frame/palette hashes, functional/reference/gameplay indexes and authoring helpers are hash-bound. Original pixels remain reference-only and absent from geometry/texture inputs.

## Independent assembly

The asset directory contains editable Blend/GLB, four independent 1024-square colour/roughness maps, metadata, nine actual rendered views, gallery and technical reports. There are 40 closed meshes/five materials; two image materials cover twenty meshes. Components comprise four profiled shells/ends, three annular sleeves, nose rim/blue backing, rear collar/small dark face, two cast bezels/two red inserts, two lower bosses/two tips and three fitted covers/six slots/twelve fasteners.

Three shells retain physical dents. Sleeves have actual inner walls and intersect the central casing at their roots. Nose bezels use ray-sampled embedded casting roots with planar insert faces. Nine fitted overlays follow owner profiles; fasteners align to actual sampled normals. Applied modifiers and primary/casting triangulation precede box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Existing sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render exercise the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, corner normals within 0.001, hierarchy/transforms/bounds, hashes, packed bytes/decoded pixels, UVs/materials and three dents. Actual odd/even containment checks casing/nose/end/collar/sleeve/fitting roots, 81 fitted-overlay samples and twelve fasteners. Nine sleeve-axis witnesses verify hollow castings; three empty front-axis witnesses and occupied blue backing preserve a blind recess. The expected collar bounds account for its vertex chamfers. AlignmentForward is checked under yaw, pitch and roll. Scoped samples do not establish exhaustive mechanical correctness or mount/animation calibration.

The actual gallery and nine-frame source comparison were inspected. Nine views passed framing. Both matched alpha channels and threshold-128 silhouettes are identical; foreground mean RGB differences are below 0.002/255. Maximum corner-normal error is 0.000334. Measured dents are approximately 0.00578/0.00388/0.00290. Fifty assembly contacts, 81 fitted-surface samples, twelve fasteners, nine sleeve voids and the blue-front recess checks passed. Full hardpoint reference verification passed sixteen definitions/144 palette-bound samples. Exact sleeve profile/seams and clipped collar remain provisional for the deferred refining pass. Original comparisons remain ignored in `artifacts/issue-1038-vortex-mine/`; tracked views contain authored models only. Required changed-code quality base: `1c61e3c6`. Game-client integration is unchanged.

## Deferred

Final silhouette/proportions, sleeve/collar details, fitting layout/functions, front recess construction, hidden surfaces, cultural variants, runtime scale/orientation, mounts and deployment/damage states remain unresolved. Technical validity does not establish final artistic acceptance. Refining and construction scaffolding remain deferred.
