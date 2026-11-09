# Missile Silo: original iris, corrected launch tube

Current canonical PB14 model for surface gameplay, build menu and SciTek. One editable source and one GLB replace the previous mechanism in place. No original-game pixels are embedded.

## Original leaves and motion

The original eight curved leaf meshes and original motion are restored: drop 0.20 native units, turn 50 degrees around fixed rim pivots, turn back, then rise. No new lift assemblies, radial translation, folding or scaling. The previous coaxial assemblies are removed.

The user explicitly selected this original motion while retaining its existing leaf/rim interference. This is not a collision-free leaf mechanism. Runtime reports record those intersections; the requested correction concerns the payload passage through the tube.

## Tube and black floor

The solid bunker bottom cap is removed. A continuous hollow shaft extends below grade to the floor at -3.2 native Z (upper surface approximately -3.18). Its opaque, non-metallic black material has zero base colour and zero specular response. The floor hides underlying ground in a direct top view and remains below the entire stored Decoy; it is not removed or animated during launch.

Guaranteed tested straight passage radius: 0.33; nominal mouth radius: 0.87. Actual Decoy geometry passes stored-payload and ascent fixtures using the documented WorldSize 48 proposal and closed-footprint fitting. The opening is not a fully bare tube. Scale and payload placement remain proposals, not recovered calibration.

The single Animation clip runs 0..2 seconds: closed at 0, original open pose at 1, closed at 2. Native frames 1/17/33 at 16 fps preserve the client's first-half opening convention. Apply all eight animated leaf-node tracks. Preserve native Z=0 / glTF Y=0 ground origin and fit the building from its closed bind pose. Hold the payload below the closed iris until open, then raise it. LaunchPayloadHoldPoint at native (0,0,-2.05) remains an authored centre proposal.

## Verification

The diaphragm proof checks original vertices and original transforms at all 33 poses in saved source and independently imported GLB. It also checks black floor material, floor depth and 160 top-down rays terminating on that floor. The main runtime report separately records retained leaf/rim intersections, clear payload passage down to -3.05, and actual Decoy geometry during storage and ascent. Zero payload collisions does not imply zero leaf/rim intersections.

Gallery views include original leaf detail and stored Decoy viewed from above. Both galleries include the refreshed animation. Final client/Android placement, activity binding and visual acceptance remain separate.

PB14.VID is a fixed-camera operational opening/closing sequence. Actual surface compositions, catalogue still and all 120 video frames were reviewed. The first model is an authored reconstruction informed by that evidence, not recovered engineering drawings. Its original animation is restored by explicit user choice.

## Two independent light channels

StatusLampLeft and StatusLampRight each contain three preset lens nodes with suffixes Hybrid, AttackOnly and DefenceOnly. Select exactly one child at unit scale when lit; zero all three when off. Channels switch independently. Shared standard PBR emissive materials require no material-animation extension. No lamp animation is exported.

| Mode | sRGB centre | Evidence |
|---|---|---|
| Hybrid/base | 255,210,138 | Legacy surface PB14 lamp centres |
| AttackOnly | 194,93,93 | OpenFA Classic Interceptor attack overlay |
| DefenceOnly | 150,170,210 | OpenFA Classic Interceptor defence overlay |

Mode selection belongs to the Interceptor launcher-mode contract. Reviewed 17 surface phases and all 120 PB14.VID frames have constant sampled lamp colours; VID uses its own yellow palette. No blink schedule is invented. Bind real activity and launcher state in the client and preserve mode overlays with presentation packages.

See diaphragm-verification.json, reference-evidence.json, correction-generation.json, correction-runtime-verification.json and delivery-review.json for hashes, measurements and limits. Run authoring, publication preparation, independent runtime verifiers and registration in that order.
