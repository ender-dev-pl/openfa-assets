# Missile Silo: corrected iris and two status lights

This is the current canonical PB14 model for surface gameplay, build menu and SciTek. The earlier silhouette remains historical evidence, excluded from current model selection. No original-game pixels are embedded in the model.

## Mechanism and integration

The original eight curved iris leaves are restored, including their original mesh coordinates, curvature, material alternation and 50-degree turn. To clear the rim they first lift by 0.08 native units, then turn and slide outward by 0.60 on telescopic guides. Their original mesh does not shrink or fold. The lift/slide is the user-authorized extension; it is not claimed as recovered hidden legacy engineering.

This keeps the original closed silhouette and opens the full mouth. The separate `diaphragm-verification.json` compares every original surface vertex against the preserved original generator formula in both native source and imported GLB (maximum error below 1e-6). It checks eight rigid curved leaves, the small lift, unchanged turn, radial travel and progressively growing opening.

The single GLB clip `Animation` runs from 0 to 2 seconds: closed at 0, fully open at 1, closed at 2. The initial short movement lifts the leaves; the remainder of the first half spreads them. Native frames are 1/17/33 at 16 fps. Exported modifiers and zero-based timing are checked independently.

Fixed-structure collision checks remain diagnostic evidence, not authority to redesign the leaves. Original overlapping leaf seams and each leaf's own mounting axle are intentional mechanical interfaces excluded from that obstruction test. No other obstruction is excluded. Full-open mouth radius 0.87 and continuous shaft radius 0.82 are ray-tested; the actual Decoy bundle is checked during stored/opening and ascent phases.

**Preserve ground origin at native Z=0 / glTF Y=0.** The launch shaft remains below grade. Fit the building using its closed bind-pose footprint. Open leaves deliberately extend past the fixed bunker, so do not rescale the building from its animated open bounds. The gallery uses fixed framing covering the complete movement.

Keep the loaded payload below the closed iris until opening completes, then lift it. `LaunchPayloadHoldPoint` at native (0,0,-2.05) remains an authored nominal placement for WorldSize 48, not recovered calibration. The Decoy fixture uses the current 2x2 building, 32-unit cells and closed-pose fitting formula, with an explicit native-Y to +Z adapter. It is an asset test, not proof that the client already binds these states or transforms.

## Two independent light channels

`StatusLampLeft` and `StatusLampRight` each contain three preset lens nodes named with suffixes `Hybrid`, `AttackOnly`, `DefenceOnly`. Select exactly one child with unit scale when lit; zero all three scales when off. The two channels can switch independently. Shared standard PBR emissive materials require no material-animation extension. No lamp animation is exported.

| Mode | sRGB centre | Evidence |
|---|---|---|
| Hybrid/base | 255,210,138 | Composed legacy surface PB14 lamp centres |
| AttackOnly | 194,93,93 | OpenFA Classic Interceptor attack overlay |
| DefenceOnly | 150,170,210 | OpenFA Classic Interceptor defence overlay |

Mode selection belongs to the Interceptor launcher-mode contract; Decoy does not establish a separate mode system. The reviewed 17 surface phases and all 120 PB14.VID frames have constant sampled lamp colours. VID uses its own yellow palette. Independent on/off support implements the requested capability; no recovered blink schedule is claimed. The client must explicitly bind real activity and launcher state to these node presets, and preserve mode overlays when presentation packages override the profile.

## Evidence and verification

PB14.VID is a fixed-camera operational opening/closing sequence, despite the older generic inventory label `rotation-video`. The surface frames, embedded-palette catalogue still and operational VID were reviewed together. The slight lift, outward guides and travel are authored additions to the original eight-leaf model, not recovered engineering drawings. Existing exterior materials were retained; new metal parts carry restrained wear.

See `diaphragm-verification.json` for the independent original-shape, lift/slide and growing-opening proof; `reference-evidence.json`, `correction-generation.json`, `correction-runtime-verification.json` and `delivery-review.json` for source hashes, measurements and limits. Use `sources/tools/blender/correct_missile_silo.py`, publication preparation, then the independent verifier and registration tools. Final game/Android state, lighting and terrain acceptance remain separate.
