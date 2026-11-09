# Mauna mobile remasters

Issue #251 is part of programme #248 and follows the completed Artemian asset milestone #249 / PR #250. This is an incremental delivery: all five Mauna mobile ships now have canonical remaster assets; the latest user-concept construction-detail follow-up for MN3C remains open. All cultures' completed spacedocks, including MN5C, are explicitly excluded. Asset verification does not establish final user artistic acceptance or client calibration.

| Ship | Legacy | Current milestone | Proposed WorldSize |
|---|---|---|---:|
| Surveillance Craft Type 5 | MN0A.256 | Canonical remaster and concept/GLB feedback verified | 40 |
| Combat Craft Type 1.5 | MN1A.256 | Canonical remaster and concept/GLB feedback verified | 56 |
| Max Combat Craft Type 6 | MN2C.256 | Canonical model, user-concept and GLB feedback verified | 128 |
| Elite Command Craft | MN3C.256 | Runtime verified; further construction-detail refinement open | 160 |
| Transportation Craft Type 3 | MN4C.256 | Canonical remaster and concept/GLB feedback verified | 180 |

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

## Combat Craft Type 1.5

MN1A has32 populated paletted headings. All were inspected; frames0/4/12/28 retain the clearest low elongated grey beam, stepped upper contour and pale blue-grey end evidence. Four equipment slots are catalogue data without recovered mount coordinates. No catalogue animation or mapped functional narrative establishes extra mechanisms.

Two actual ImageGen attempts were reviewed. Concept1 was too thin/long and put the pale field at the long aft end. Concept2 improves body solidity and moves the field to the short fore end; its top view remains somewhat elongated, so actual legacy and preserved native proportions take precedence. Exact prompts, input/source identities and both generated images are recorded with verdicts. The unequal raised decks, service frames and hidden construction are authored interpretations below sprite resolution. The pale field is opaque metal/service material, not proven glazing, emission or equipment.

The canonical `sources/objects/mauna/combat-craft-type-1-5/model.blend` and `model.glb` contain34,456 triangles in four batches/one material/three embedded PBR maps, reduced from53,512 triangles in49 source meshes. All49 part names remain editable groups.48 surface connections and three physical dents were verified; three whole-assembly rays pass through the shallow deck gap and two hit solid deck sections in both native and independent GLB. Technical wireframe is generated from the actual imported model.

Imported-GLB feedback first rejected the generic comparison camera: end labels12/28 were reversed and the low angle flattened the side silhouette. A second real render uses explicit estimated end directions and elevation0.95; the actual0/4/12/28 collage was inspected again. A higher frame4-only camera was tried and rejected as an unhelpful adjustment. The coarse proportion diagnostic accounts for one-pixel uncertainty in the16x6 source bounds; it is not an artistic acceptance score. This is a comparison aid, not recovered camera calibration or proof of gameplay orientation. The native grey beam, sparse service construction and pale fore end remain recognizable; precise below-pixel engineering remains interpretation. WorldSize56 is a small/medium combat proposal and client calibration/final user artistic acceptance remain separate.

## Transportation Craft Type 3

MN4C supplies16 populated even headings, all inspected; odd frames are empty and the runtime uses the even-heading restriction. Catalogue data establishes ore/missile transport roles and four uncalibrated equipment slots. The three tall notched sections, broad lower housing, pale blue bands and warm lower/end details are visible evidence. Equal manufactured section heights, hidden geometry and exact notch depth are interpretation; apparent oblique height differences alone do not prove unequal towers.

One actual ImageGen concept was generated from paletted0/4/12/28 references and reviewed. The coherent three-section assembly and sparse fitted construction are useful; exact material-band continuation remains authored. Prompt/input/source identities and the generated image are recorded, with no need to spend a second or third attempt.

Actual imported-GLB feedback exposed a geometric defect in the first study: its comb profiles were90degrees across the lower housing, leaving plain columns in a corresponding broadside view. The canonical source rotates each entire fitted section about its own centre, including panels, fasteners and attachments. A declared pre-rotation axial correction broadens the visible comb profile from0.56 to0.64 authored units. Source-form verification applies these explicit transformations instead of pretending the geometry is unchanged. Physical dents and their sampling directions rotate with the sections.

Pale blue-grey material bands now continue across the sections and lower casing. Real face cuts at the band boundaries avoid serrated colour regions; planar UV projection preserves the shared sparse wear atlas. The upper fields were broadened after actual render feedback. These opaque surfaces imply neither glass nor emission. Actual final0/4/12/28 renders were inspected with legacy and concept1; preview lighting is darker/cooler than the original palette, and exact hidden construction remains unresolved.

Canonical `sources/objects/mauna/transportation-craft-type-3/model.blend` / `model.glb` contains39,376 triangles in four batches, one material and three embedded PBR maps, reduced from103,456 triangles in83 source meshes. All83 part identities remain editable. Saved-native and independent GLB checks cover closed positive geometry, declared transformed-source tolerance,82 seated connections and three physical dents.27 notch-entry rays plus two between-section gap rays stay clear;12 adjacent-tooth rays hit structure in both formats. Wireframe derives from the same actual imported geometry.

The generic Mauna author gained rigid per-part rotations and the verifier rotates protected dent directions. Both earlier Mauna models were genuinely regenerated, sanitized and independently verified afterward; their GLB bytes and every render hash were checked unchanged before updating native-source review bindings. No earlier cultural generator was modified.

Estimated comparison azimuth-minus90degrees/elevation0.18 is a visual aid, not recovered client calibration. WorldSize180 is a transporter proposal; four mounts, scale/heading/material validation in the client and final user artistic acceptance remain separate. One canonical payload serves gameplay, build/menu and SciTek; the original study is historical and outside current packaging selection.

## Reproduction and selection

Generate the independently authored atlas with `tools/author_mauna_mobile_maps.py`. Run Blender with `sources/tools/blender/remaster_mauna_mobile_ship.py -- --ship surveillance-craft-type-5`, sanitize metadata with `tools/prepare_mauna_mobile_publication.py --ship surveillance-craft-type-5`, then run `sources/tools/blender/verify_mauna_mobile_ship.py` with the same ship argument. Inspect actual imported renders against legacy and the reviewed concept before recording review bindings. Register with `tools/register_mauna_mobile_remasters.py`, run `tools/test_mauna_mobile_remasters.py`, register the delivery report and rebuild the gallery.

The Mauna author uses stable shared mesh/recipe helpers with its own palette, grouping, planar projection and generator. The verifier reuses geometry/raster helpers while adding native/import void/solid witnesses. Both entrypoints and imported helper files are hash-bound; none of the earlier cultural generators or models is rewritten. Source-bound evidence must follow actual validation, not hash replacement alone.

Inventory selects one canonical payload for gameplay, ship/build menus and SciTek. Historical first studies remain outside current packaging selection. Blender is the asset authoring target runtime; no game build, device performance certification or completed client integration is claimed here.

## Elite Command Craft

MN3C retains two grey chamfered blocks in tandem, a short narrow connector and opposed red-tipped axial rods. All32 populated headings were inspected. Two built-in ImageGen requests returned no pixels; the explicitly authorized third attempt returned the sole inspectable concept. All three requests count against the limit. The concept guides sparse worn alloy, fitted maintenance surfaces and opaque pale-blue bands; exact joints, hidden surfaces and rod function remain interpretations.

The canonical `sources/objects/mauna/elite-command-craft/model.blend` and `model.glb` contain38,594 triangles in four batches, one material and three embedded maps, versus103,696 triangles in59 original meshes. All59 source part identities remain editable. Actual saved-native and independent GLB verification covers source-surface tolerance,58 seated connections, two physical dents, matching exported positions and rendered parity. Two side-void rays preserve the narrow connector; three occupied rays check adjacent structure.

The first GLB feedback found blue-grey rod terminals: the recipe now uses the muted-red atlas tile. End comparison elevation was reduced from0.95 to0.25 after inspecting corresponding legacy12/28, and the saved source/import were actually verified again. End blue-field extent and lighting still differ; no numerical fidelity score or complete client acceptance is inferred. WorldSize160 and six equipment mounts require calibration. The gallery selects the same canonical source for gameplay and all menus, with the first study retained as historical.

## Max Combat Craft Type 6

MN2C keeps the low layered grey hull, bronze side strips, sloped aft housing and two separate red covers at one transverse deck station. All32 populated paletted headings were inspected. Two built-in ImageGen requests returned no inspectable output; the third returned a primitive/material study, whose plan view incorrectly placed the red pair longitudinally. The user-supplied ImageGen concept is the preferred construction-detail reference. It does not authorize tandem bridges, a taller silhouette or invented lights. Both inspectable concepts are available in the gallery; no fourth generation was made.

Canonical `sources/objects/mauna/max-combat-craft-type-6/model.blend` and `model.glb` contain61,322 triangles in four batches, one material and three embedded PBR maps. The58 original part identities remain alongside139 new fitted details: six framed side maintenance banks, four conformal shoulder plates with service insets, roof/foredeck louvers, supported conduits and red-cover bands. Broad surfaces remain quiet. Equipment function and hidden engineering are interpretations; WorldSize128 and six mounts require client calibration.

Actual saved-native and independent GLB verification covers declared source-surface tolerance, closed positive geometry,197 named parts,196 seated contacts, three physical dents, two open-space rays and three occupied rays in both formats. Feedback corrected planar side-wall shading, added the missing shoulder depth, reduced excessive tessellation on added planar fittings, and adjusted estimated comparison cameras. The exported red surfaces are tested as a transverse pair at the same longitudinal station, using actual GLB positions and UV material tiles. No numerical artistic fidelity score is inferred.

MN2C uses dedicated `remaster_mauna_type6.py`, `mauna_type6_detail_parts.py` and `verify_mauna_type6.py` so the four preceding source authors/exports are unchanged. Sanitize with `prepare_mauna_mobile_publication.py --ship max-combat-craft-type-6`, then run the dedicated verifier with that ship argument. Existing primitive/loft helpers and the shared geometry verifier are hash-bound. Report I/O regression tests ensure reports remain in the model folder and validation cannot silently rewrite source inputs.

The user's new MN3C reference exposes remaining detail work despite its existing technical pass. Its high-detail acceptance gate is therefore withdrawn until that follow-up is actually rendered and reviewed. This is not completion of the whole remaster programme or final user/client acceptance.
