# MN13 Defence Pods

Canonical Mauna Defence Pods, `openfa:building/legacy/142`, openfa-assets #261. Indexed identity: 2x2 footprint, class 3, 34 construction updates, durability 40. Function record 1003 identifies this as the Mauna anti-missile pod. Culture record 137 describes purely practical concrete architecture. Metric dimensions and calibrated 3D muzzle sockets are not recovered.

## Evidence and concept

All 20 nonempty own images were inspected: shadow 0, fixed base 1, sixteen directional heads 2..17 from `_B/MN13.256`, and two `_ZOOM/MN13.256` overview/detail images. Directional heads were composited over the fixed base using actual offsets. All 41 catalogue updates were reviewed. These establish heading states, not an automatic idle scan, firing or recoil cycle.

The full `_MA` loose/archive indexes and all 36 research subjects were surveyed. Class 3 and research 02 explicitly bind generic Terran PB03; research 02 information binds `_SCITEK/ST02.VID`. All 60 PB03 colour updates, its archive preview and all 195 ST02 technical updates/423 timeline frames were reviewed. Their round Terran anatomy and additional fittings do not override the Mauna source. Original-game pixels stay in private evidence.

One actual built-in ImageGen concept was selected against the own source. The canonical model retains a squat truncated-square grey-blue concrete pedestal, broad red strip, framed two-column/four-row vent, compact rotating head and ONE long slim inclined barrel. The prior silhouette study's twin gold muzzles were unsupported and are replaced. Hidden walls, bearing engineering, head service plate, muzzle bore, material depths, barrel elevation and cell-relative dimensions are authored interpretation. Used concrete, joint grime, paint scuffs, metal scratches and two actual shallow cast chips preserve broad readable surfaces.

## Motion and verification

The prior editable model's `DirectionalHead` and `StaticBase` controllers, native `HeadingPreview_360` action, pivot and exact rotation curves are retained. Native frames 1..17 at 16 FPS represent a 360-degree heading preview; the GLB clip is named `Animation`, matching the prior GLB. Export baking uses 64 FPS to preserve intermediate rotation. Gallery playback is slowed to one quarter of this preview speed for inspection. None of these timings establish simulation timing or autonomous motion.

Actual saved-native and independent GLB checks sample 65 poses across the full rotation. They verify positive closed meshes, finite UVs, a stationary base, supported bearings/head/collar/barrel/backing/service plate, absence of unintended moving/fixed surface intersections, eight actual blind vent cells with seated backings, a true recessed muzzle bore, cast wall slope, two physical chips, decoded texture pixels, root and animation parity. This is sampled verification, not a proof of every continuous pose. Budgets and exact measured errors are in `model.json` and `runtime-review.json`.

Visual feedback lowered the moving assembly by 0.10 local units, shortened the fixed bearing by 0.10 and rounded the head edges after inspecting the first native render against the selected concept and own source. The original controller is unchanged. Final native/imported whole/detail renders and technical edges use the same canonical geometry.

## Integration

One current Blend/GLB serves gameplay, building/construction and SciTek; the prior pair remains unchanged and historical. Preserve `PlacementRoot`, ground 0, +Z up, -Y forward and 2x2 placement. Bind the heading controller to authoritative simulation heading. Runtime index registration, world scale, muzzle socket calibration, shader/performance and final user artistic approval remain separate. Do not run the gallery heading preview as an autonomous gameplay scan. No muzzle flash, recoil, projectile or timed light phase is inferred. Both galleries include the current model, details, wireframe and playable heading preview.
