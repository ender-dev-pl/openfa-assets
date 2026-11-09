# Mauna mobile remasters

Issue #251 is part of programme #248 and follows the completed Artemian asset milestone #249 / PR #250. This is an incremental delivery: one of five Mauna mobile ships is currently remastered. All cultures' completed spacedocks, including MN5C, are explicitly excluded. Asset verification does not establish final user artistic acceptance or client calibration.

| Ship | Legacy | Current milestone | Proposed WorldSize |
|---|---|---|---:|
| Surveillance Craft Type 5 | MN0A.256 | Canonical remaster and concept/GLB feedback verified | 40 |
| Combat Craft Type 1.5 | MN1A.256 | Pending | — |
| Max Combat Craft Type 6 | MN2C.256 | Pending | — |
| Elite Command Craft | MN3C.256 | Pending | — |
| Transportation Craft Type 3 | MN4C.256 | Pending | — |

## Evidence and material direction

Actual paletted heading sheets and selected enlargements remain private. The ship-reference index assigns no MN video; the existing `_MA` archive/loose-file inventory is an inventory finding, not proof that differently named animation material is unrelated. Original pixels are not published or used as model textures.

The broad Mauna material direction follows the individual references: neutral/oxidized grey alloy, subdued blue-grey fields, small warm oxide/brown details and red parts only where observed. Architecture text (ENGLISH.CDB Mauna record 137 at 0x7bea) supports utilitarian/angular context, not concrete spacecraft, architectural decoration or exact vehicle geometry. Bright and pale marks do not by themselves establish glazing, emission or equipment function.

## Surveillance Craft Type 5

MN0A's 32 populated paletted headings support an upright thick grey slab, an interrupted upper edge, blue-grey surface fields and warm lower details. The catalogue establishes a small scout and two equipment slots without recovered mount coordinates. The first source's four crown tabs, two lower tabs, service fields and hidden construction are authored interpretations below source resolution.

Two actual ImageGen attempts precede this remaster. The first retained the broad form and worn finish but introduced a numeral-like blue marking, which was rejected. The second replaces it with plain opaque material/service fields. Exact prompts, input/source identities, generated images and verdicts accompany the canonical `concept-review.json`; the gallery distinguishes rejected and reviewed attempts. No third generation was needed.

The canonical `sources/objects/mauna/surveillance-craft-type-5/model.blend` and `model.glb` reduce the first source's 41,332 triangles in 47 meshes/five materials to 26,160 triangles in four batches, one material and three embedded PBR maps. All 47 part identities remain editable vertex groups. The grey slab, interpreted crown, warm lower tabs, fitted panels and fasteners retain their original assembly relationships. Sparse grime, scuffs, stains and physical dents keep broad surfaces readable without dense panel grids. Small service-frame radii soften manufactured edges.

Actual imported-GLB feedback rejected a fan of stretched texture and a wavy seam on the flat ends: the reused body-name heuristic selected cylindrical UVs for a rectangular hull. Mauna now uses dominant-axis planar projection while preserving explicit atlas material tiles. Actual hero, end, broadside and corresponding 0/4/12/28 views were inspected again with legacy and concept2. A direct GLB positions/indices/UV test requires non-collapsed texture area on those broad planar ends, preventing a metadata-only UV-mode claim.

Saved-native and independent GLB checks verify closed positive geometry, declared source-form tolerance, 46 seated connections, two physical side dents, matching world positions and actual renders. Three whole-assembly ray columns through crown gaps and four occupied-tab rays run against both native and imported geometry. These scoped witnesses do not prove exhaustive mechanical correctness. Technical wireframes derive from the same actual GLB geometry.

The blue-grey fields are opaque service surfaces, not a numeral, window, engine or weapon. Warm lower tabs may be occluded in high views and are darker under preview lighting; lower/underside views retain their geometry without invented emission. Heading4 alpha bounds are 20 by 17 pixels. Estimated comparison azimuth zero and elevation 0.12 are not recovered client orientation or projection. WorldSize 40 is a small-scout proposal; two mount positions, client scale/heading/material validation and final user artistic acceptance remain separate.

## Reproduction and selection

Generate the independently authored atlas with `tools/author_mauna_mobile_maps.py`. Run Blender with `sources/tools/blender/remaster_mauna_mobile_ship.py -- --ship surveillance-craft-type-5`, sanitize metadata with `tools/prepare_mauna_mobile_publication.py --ship surveillance-craft-type-5`, then run `sources/tools/blender/verify_mauna_mobile_ship.py` with the same ship argument. Inspect actual imported renders against legacy and the reviewed concept before recording review bindings. Register with `tools/register_mauna_mobile_remasters.py`, run `tools/test_mauna_mobile_remasters.py`, register the delivery report and rebuild the gallery.

The Mauna author uses stable shared mesh/recipe helpers with its own palette, grouping, planar projection and generator. The verifier reuses geometry/raster helpers while adding native/import void/solid witnesses. Both entrypoints and imported helper files are hash-bound; none of the earlier cultural generators or models is rewritten. Source-bound evidence must follow actual validation, not hash replacement alone.

Inventory selects one canonical payload for gameplay, ship/build menus and SciTek. Historical first studies remain outside current packaging selection. Blender is the asset authoring target runtime; no game build, device performance certification or completed client integration is claimed here.
