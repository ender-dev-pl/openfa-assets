# Rigellian Construction Unit RI09

Tracked in [#979](https://github.com/ender-dev-pl/ed-openfa-game/issues/979), relates to #948/#946 and reference milestone #970.

Independent editable Blend and standalone embedded-texture GLB: `docs/assets/reconstruction/buildings/rigellian/construction-unit/`. Preserve ID `openfa:building/legacy/048`, global type 48, definition class 25, nominal 4x4 footprint and identity ground-level `PlacementRoot`.

## Observed and inferred

Correctly paletted surface and catalogue phases show twin open annular platforms, a raised circular machinery hood, a depressed top panel, small brass fittings, a central red inset, paired rear uprights and green internal equipment posts. Hologram phases reveal/highlight one presentation, not independent views or proven mechanical movement. Source provenance is in `rigellian-building-references.json`; original pixels and comparison sheets remain reference-only under `artifacts/rigellian-building-reference-study/RI09/`.

Hidden mounting runners, exact platform spacing and thickness, recess depths, post counts/depths and hidden connections are authored interpretation. No reference mesh or texture is distributed. Further independent views are unavailable; hidden geometry is not claimed as observed.

## Modelling and comparison

Revision 1 established closed annular solids, ten actual recessed outer-wall channels/backings, a supporting spine/column, internal green posts and supported inspection covers. Revision 2 adds sufficiently dense ring rows for actual shallow dents, plus independently authored dirt, stains, abrasion and colour/roughness maps. Side surfaces use cylindrical coordinates about each casting centre; planar extreme caps use each casting XY bounds. Bevels are applied before UV assignment.

Comparing actual renders with surface/hologram references led to revision 3: the hood inspection depression becomes circular and rear portal supports become paired. The initial rectangular depression and single supports did not represent these visible source features adequately.

## Verification and outstanding work

Blender 4.5.15 LTS reopens native Blend and imports GLB. Checks cover 46 closed mesh objects, eight used materials, identity placement, 4x4 bounds, open axes through the entire assembly, ten channel depths/embedded backings, geometric ring dents, hood recess/floor contact and column support overlaps. A connected nearest-surface sample graph supplements checks; it is not exhaustive intersection proof. Packed image bytes match authored PNGs, full colour/roughness pixels and effective material values survive export, and every mapped corner satisfies planar or cylindrical UV coordinates.

Six native 900x900 RGBA renders and an actual imported GLB render pass framing/alpha review and native/imported comparison. The scoped Blender runtime gate binds exact model, export, source, reports and render hashes. This does not establish final artistic acceptance or game-client integration.

Precise proportions, source-facing projection, low-resolution front rib interpretation, richer manufactured detail, wear visibility at gameplay scale, construction/damage states, calibrated placement and game integration remain open. All final visual gates remain false; no gameplay renderer or asset registration changed.
