# MN15 Pulse Tower

Canonical Mauna Pulse Tower, `openfa:building/legacy/144`, openfa-assets #261. Indexed identity: 2x2 footprint, class 17, 32 construction updates, durability 40. Function record 1005 identifies the Mauna anti-ship installation; culture record 137 describes practical concrete architecture. Metric dimensions, rail angle and calibrated weapon sockets are not recovered.

## Evidence and concept

All 20 nonempty own images were reviewed: shadow 0, fixed base 1 and directional heads 2..17 from `_B/MN15.256`, plus overview/detail from `_ZOOM/MN15.256`. The sixteen heads were composited over the fixed base using actual offsets. All 41 catalogue updates were inspected. These establish heading states, not autonomous scanning, recoil, firing or light timing.

Full `_MA` loose/archive indexes and all 36 semantic research subjects were surveyed. Class 17 and research 19 explicitly bind generic Terran PB17: all 60 colour updates and its archive preview were reviewed. Research 19 information binds SCITEK/ST19, whose 195 technical updates/423 timeline frames were inspected. Photon Turret research 18 has separate PB18/ST18 bindings. Generic Terran round-head/single-barrel anatomy does not replace the Mauna fork. Original-game pixels stay private.

One real built-in ImageGen concept was selected against the own source. The model retains a broad asymmetric wedge/spade head narrowing into TWO parallel rectangular prongs, with a real gap and a narrow rotating support pierced by a triangular opening. The fixed sloping grey-blue base has exactly two side brass reservoirs/dark caps, two opaque round ochre front fittings, a narrow blind horizontal slot and one low red mark. The historical silhouette study's three circular emitters are superseded by own-source anatomy. Bearings, caps, hidden walls, recess depths, dimensions and precise rail inclination remain authored. Used cast stains, grime, scratched metal, worn paint and two shallow physical chips preserve quiet surfaces.

## Geometry, motion and review

The original `DirectionalHead` and `StaticBase`, native `HeadingPreview_360` action, pivot and exact rotation keys are retained. Native frames 1..17 at 16 FPS represent a complete heading preview. The exported clip is `Animation`; 64 FPS baking preserves intermediate rotation. The gallery plays this preview at quarter speed for inspection, not gameplay timing. Current whole/detail renders use heading frame 5 for a more source-like presentation; this is not calibrated legacy heading-index recovery.

Actual saved-native and independent GLB checks sample 65 poses. They verify closed positive geometry, finite UVs, stationary base, fourteen physical support contacts at every sample, no unintended moving/fixed surface intersections, real triangular opening/solid support rays, two distinct rail hits and an empty fork gap, source reservoir/front-fitting placement, actual blind service slot/backing, cast slope, physical chips, decoded texture pixels and motion/render parity. This is sampled verification, not continuous-sweep certification. Budgets and exact hashes/errors are in `model.json` and `runtime-review.json`.

Visual feedback darkened the too-pale head/support to used grey-blue steel and softened their edges. The source counts and controller were retained. A more representative heading avoids confusing foreshortening with different geometry. Final whole/detail renders and technical edges use the same canonical model; agent review does not imply final user artistic approval.

## Integration

One current editable Blend/portable GLB serves gameplay, construction/build menus and SciTek. The prior pair remains unchanged and historical. Preserve `PlacementRoot`, ground 0, +Z up/-Y forward, 2x2 placement and the heading controller. Bind it to authoritative simulation heading; do not run the preview as an autonomous scan. Actual source-index registration, world scale, weapon socket, state/shader and Android performance require separate client verification. Both galleries include the current model, details, wireframe and playable heading preview. See `integration-contract.json`.
