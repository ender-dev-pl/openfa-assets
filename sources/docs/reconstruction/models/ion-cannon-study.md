# Ion Cannon — first authored iteration (#1033)

`openfa:ion-cannon`, global equipment type 0: SurfaceWeapon, surface damage 2, value 1000. The catalogue does not establish a 3D gameplay mount, aiming axis or cultural geometry variants. No mapped functional narrative is located. This adds a missing first source while preserving existing shield/Photon/Plasma reconstructions and refinements.

## Source and interpretation

PH00.VID supplies 60 inventory rotation frames at 120×80, decoded with original per-frame palettes. All frames and enlarged 0/22/36/51 were inspected; nine canonical frame/palette hashes and source/metadata hashes are verified. They support an elongated rounded pale housing, red/copper front, broad rear collar/prongs, a transverse cylindrical assembly on a stem, recessed side end and raised rectangular bracket.

The full rotation supports one visible transverse assembly. This supersedes the earlier provisional two-side-cylinder wording in the reference review; it does not establish a hidden symmetric pair. Exact rear-prong count, profiles, bracket section, hidden surfaces and mount orientation remain uncertain. Three rear prongs, an open bracket and a blind side recess are first-source interpretations. Dark front marks are shallow fitted inlays, not an unproven through-bore. The inventory rotates the whole presentation and does not prove an independently rotating turret, recoil, hinge or deployment. AlignmentForward is an authored local -Y helper only; no gameplay mount is registered.

This equipment entry is global. None of the cultural architecture sections establishes a race-specific Ion Cannon form. Original pixels remain reference-only and absent from geometry/texture inputs. Reference, functional and gameplay indexes, source video, decoded metadata and authoring helpers are hash-bound.

## Independent assembly

The asset directory contains editable Blend/GLB, four independent 1024-square colour/roughness maps, metadata, nine actual rendered views, gallery and technical reports. There are 40 closed meshes/four materials; two image materials cover nineteen meshes. Components comprise three profiled shells, front neck, transverse stem, dark backing, side annular rim/rear annular collar, three prongs/three red tips, three bracket members, two fitted front marks and three service covers/six slots/twelve fasteners.

Dense radial profiles retain three physical dents. Proper axis rotations preserve owner-local surface definitions. Annuli have actual inner walls; the side end has a separate recessed backing. Eleven fitted overlays follow dented profiles and fasteners align to actual ray-sampled normals. Modifiers and primary triangulation precede local box UVs and explicit corner-normal capture. Independent analytic grime/stains, grain and issue-seeded scratches provide new-object wear. Existing assets and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 native reopen and independent GLB import/render passed positive closed topology, exact geometric vertex counts after diagnostic-only 1e-6 seam welding, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded pixels, UVs/materials and dents. Maximum corner-normal error is approximately 0.000575. Measured dents are approximately 0.00600/0.00382/0.00381. Actual odd/even containment verifies 33 attachment contacts, 99 fitted-overlay samples and twelve fasteners. Two bracket voids, three empty recess-axis witnesses and an occupied blind backing distinguish real openings from solid faces. AlignmentForward is checked under yaw, pitch and roll. These samples do not establish exhaustive mechanical correctness or mount/animation calibration.

Actual gallery and nine-frame source comparison were inspected. Nine views passed framing. Both matched threshold-128 silhouettes are identical; foreground mean RGB differences are below 0.003/255. Alpha differs at one front-quarter pixel and four detail pixels, with maximum difference 4/255, within the existing export threshold. Full reference verification passed sixteen definitions/144 sampled palette-bound frames. Standalone Blender runtime verified; game-client integration unchanged. Source comparisons remain ignored in `artifacts/issue-1033-ion-cannon/`; tracked views contain authored models only. Required changed-code quality base: `19ddac49`.

## Deferred

Final shell proportions, side-assembly details, rear-prong count, bracket/hidden construction, cultural variants, runtime scale/orientation, mounts, aiming/recoil and damage states remain unresolved. Technical validity does not establish final artistic acceptance. Refining and construction scaffolding remain deferred.
