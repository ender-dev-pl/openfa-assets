# Missile Silo: corrected iris and two status lights

This is the current canonical PB14 model for surface gameplay, build menu and SciTek. The earlier silhouette remains historical evidence, excluded from current model selection. No original-game pixels are embedded in the model.

## Mechanism and integration

Sixteen thin rigid iris blades rotate about fixed pivots in the plane of the lid, overlapping like a camera diaphragm. The blade count and hidden rim construction are authored; the reviewed VID establishes the planar star-shaped opening, not an exact engineering drawing. There is no lowering carrier or out-of-plane folding. Independent native and imported GLB checks sample all 33 frames against fixed structures; projected iris-sheet laps are excluded from that fixed-structure test. A separate planar proof checks disjoint height bands for every sheet at every pose, with at least 0.00049 native units between layers. The full-open bore is checked by 768 rays, including a continuous radius 0.82 shaft down to Z=-3.05.

The single GLB clip `Animation` runs from 0 to 2 seconds: closed at 0, fully open at 1, closed at 2. This preserves the existing runtime convention that the first half opens the iris. Native frames are 1/17/33 at 16 fps. Exported modifiers and zero-based clip timing are verified independently.

**Preserve ground origin at native Z=0 / glTF Y=0.** The underground launch shaft must remain buried; never fit its lowest vertex onto the terrain. `SiloPlacementRoot` carries `preserve_ground_origin=true`. Gallery terrain is a render-only mask, absent from the delivered model.

Keep the loaded payload below the closed iris until the opening completes, then lift it. No carrier-retraction clearance is required. `LaunchPayloadHoldPoint` is an authored nominal centre at native (0,0,-2.05), not a recovered legacy launch transform. The Decoy clearance fixture uses the current 2x2 building, 32-unit cell and proposed missile WorldSize 48 fit, with an explicit native-Y to +Z adapter. It tests the stored payload throughout all 33 poses and its ascent through the fully open aperture. This is an asset test, not proof that the game client already implements those transforms or sequencing.

## Two independent light channels

`StatusLampLeft` and `StatusLampRight` each contain three preset lens nodes named with suffixes `Hybrid`, `AttackOnly`, `DefenceOnly`. Select exactly one child with unit scale when lit; zero all three scales when off. The two channels can switch independently. Shared standard PBR emissive materials require no material-animation extension. No lamp animation is exported.

| Mode | sRGB centre | Evidence |
|---|---|---|
| Hybrid/base | 255,210,138 | Composed legacy surface PB14 lamp centres |
| AttackOnly | 194,93,93 | OpenFA Classic Interceptor attack overlay |
| DefenceOnly | 150,170,210 | OpenFA Classic Interceptor defence overlay |

Mode selection belongs to the Interceptor launcher-mode contract; Decoy does not establish a separate mode system. The reviewed 17 surface phases and all 120 PB14.VID frames have constant sampled lamp colours. VID uses its own yellow palette. Independent on/off support implements the requested capability; no recovered blink schedule is claimed. The client must explicitly bind real activity and launcher state to these node presets, and preserve mode overlays when presentation packages override the profile.

## Evidence and verification

PB14.VID is a fixed-camera operational opening/closing sequence, despite the older generic inventory label `rotation-video`. The surface frames, embedded-palette catalogue still and operational VID were reviewed together. Rim storage geometry, blade count and pivot placement are authored solutions, not recovered engineering drawings. Existing exterior materials were retained; new metal parts carry restrained wear.

See `diaphragm-verification.json` for the independent fixed-pivot/planarity and growing-opening proof; `reference-evidence.json`, `correction-generation.json`, `correction-runtime-verification.json` and `delivery-review.json` for source hashes, measurements and limits. Use `sources/tools/blender/correct_missile_silo.py`, publication preparation, then the independent verifier and registration tools. Final game/Android state, lighting and terrain acceptance remain separate.
