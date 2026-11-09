# Missile Silo: corrected iris and two status lights

This is the current canonical PB14 model for surface gameplay, build menu and SciTek. The earlier silhouette remains historical evidence, excluded from current model selection. No original-game pixels are embedded in the model.

## Mechanism and integration

The original eight curved iris meshes are preserved. Each leaf now lifts by 0.08 native units directly on its fixed rotation axis and turns through 90 degrees. There is no radial travel, external support arm, rack or drive wheel. The compact cylinder barrels sit inside the tube beneath the leaf pivots, attached to an internal mounting ring. Conformal bearing saddles meet the actual underside of each leaf without projecting above it.

The user-selected 90-degree rotation gives a larger opening than the preceding 50-degree study. It does not expose the entire nominal tube radius of 0.87: the guaranteed tested straight passage radius is 0.44. The actual Decoy bundle passes the ascent fixture with the documented WorldSize 48 and closed-footprint fitting. Do not interpret the clip endpoint as a fully bare tube.

`diaphragm-verification.json` checks unchanged original vertex coordinates (error below 1e-6), fixed coaxial alignment, lift,90-degree turn and no radial motion. The internal mounting ring contacts the liner; eight barrels contact that ring. At all33 poses, piston/barrel engagement exceeds0.0649 and all leaf/bearing/spindle connections remain present. The attachment geometry is authored, not recovered hidden engineering or an engineering load analysis.

The single Animation clip runs0..2 seconds: closed at0,90-degree opening at1, closed at2. Native frames1/17/33 at16fps preserve the client's first-half opening convention. The initial short movement lifts the leaves before rotation. Preserve ground origin at native Z=0 / glTF Y=0 for the below-grade shaft, and fit the building from its closed bind pose.

Fixed-obstruction tests exclude original overlapping leaf seams and each leaf's own intentional bearing interface. The verified0.44 passage is ray-tested down to Z=-3.05. Actual Decoy geometry is tested while stored and during ascent. The nominal LaunchPayloadHoldPoint at native(0,0,-2.05) remains an authored proposal, not recovered gameplay calibration.

[Imported GLB detail of the coaxial actuators](../../../../../../gallery/media/docs/assets/bootstrap-3d/terran-refined/pb14/mechanism-detail.png). Final client/Android state and visual acceptance remain separate.

## Two independent light channels

`StatusLampLeft` and `StatusLampRight` each contain three preset lens nodes named with suffixes `Hybrid`, `AttackOnly`, `DefenceOnly`. Select exactly one child with unit scale when lit; zero all three scales when off. The two channels can switch independently. Shared standard PBR emissive materials require no material-animation extension. No lamp animation is exported.

| Mode | sRGB centre | Evidence |
|---|---|---|
| Hybrid/base | 255,210,138 | Composed legacy surface PB14 lamp centres |
| AttackOnly | 194,93,93 | OpenFA Classic Interceptor attack overlay |
| DefenceOnly | 150,170,210 | OpenFA Classic Interceptor defence overlay |

Mode selection belongs to the Interceptor launcher-mode contract; Decoy does not establish a separate mode system. The reviewed 17 surface phases and all 120 PB14.VID frames have constant sampled lamp colours. VID uses its own yellow palette. Independent on/off support implements the requested capability; no recovered blink schedule is claimed. The client must explicitly bind real activity and launcher state to these node presets, and preserve mode overlays when presentation packages override the profile.

## Evidence and verification

PB14.VID is a fixed-camera operational opening/closing sequence, despite the older generic inventory label `rotation-video`. The surface frames, embedded-palette catalogue still and operational VID were reviewed together. The slight lift, coaxial lift assemblies and90-degree rotation are authored additions to the original eight-leaf model, not recovered engineering drawings. Existing exterior materials were retained; new metal parts carry restrained wear.

See `diaphragm-verification.json` for the independent original-shape, coaxial lift and90-degree opening proof; `reference-evidence.json`, `correction-generation.json`, `correction-runtime-verification.json` and `delivery-review.json` for source hashes, measurements and limits. Use `sources/tools/blender/correct_missile_silo.py`, publication preparation, then the independent verifier and registration tools. Final game/Android state, lighting and terrain acceptance remain separate.
