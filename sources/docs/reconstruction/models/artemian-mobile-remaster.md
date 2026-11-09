# Artemian mobile remasters

Issue #249 is part of programme #248. This is an incremental delivery: two of five mobile ships are currently remastered. The user confirmed that every culture's spacedocks are already complete. Geostationary Construction AR5C and the other fixed orbital stations are excluded from further work in this programme.

| Ship | Legacy | Current milestone | Proposed WorldSize |
|---|---|---|---:|
| Gerla-Kans Explorer | AR0A.256 | Canonical remaster and concept/GLB feedback verified | 40 |
| All-Purpose Assault | AR1A.256 | Canonical remaster and concept/GLB feedback verified | 48 |
| Shielded Multi-Assault | AR2C.256 | Pending | — |
| Ultimate Mk II | AR3C.256 | Pending | — |
| Hardcore | AR4C.256 | Pending | — |

## Evidence and concept workflow

All 32 descriptors per mobile ship were decoded with their original palette and inspected; Hardcore has populated even headings. Original pixels/payloads remain outside the repository. The `_MA` loose-file/archive inventory covers 183 names in PB/ST/PS/PH/PM families; the existing ship-reference index assigns no AR/MN videos. This is an inventory result, not proof that every differently named animation is unrelated.

Gerla-Kans is a scout with two equipment slots. The functional text index maps its name and catalogue role, without a mapped descriptive narrative. Paletted AR0A supports a low pointed green lower body and a raised grey upper surface. Cultural Architecture text favours hard metal/alloy shells and distinct planes; applying that to spacecraft is contextual interpretation, not recovered vehicle engineering.

Two actual ImageGen concepts precede the remaster. The first was rejected as too long/thin and too olive. The second retains a compact grey opaque faceted shell on a green lower wedge. Exact prompts, reference image identities, generated files and discrepancy verdicts are recorded in the canonical `concept-review.json`; the gallery labels the rejected and reviewed attempts. No third generation was needed.

## Gerla-Kans refinement and GLB feedback

The existing independently authored first source is preserved as historical evidence. Its canonical remaster is `sources/objects/artemian/gerla-kans-explorer/model.blend` and `model.glb`; the inventory selects that one payload for gameplay, ship/build menus and SciTek. It has 28,778 triangles, four batches, one material and three embedded PBR maps, reduced from the first source's 78,928 triangles in 38 meshes. Named vertex groups retain all 38 editable part identities.

Actual imported-GLB feedback found a needle-like, overly flat grey prow. The refined shell has a broader truncated forecap and a moderately raised grey mass while retaining the original green planform. A first deformation produced a bulbous front and was rejected after rendering; a linear target half-width fixes it. Profile checks now cover the complete fore section, not only its endpoint. Attached grey covers, slats and fasteners follow the same deformation. Shared worn metal uses sparse scuffs, seam grime and small stains without dense panel grids. Two existing physical dents remain measurable after simplification.

Saved-native and independent-import checks cover the declared refined baseline form per part, 37 seated connections, closed geometry, protected dents, forecap dimensions, matching world positions and actual native/import renders. Technical wireframes derive from that same imported GLB. Coarse side-aspect checks diagnose major projection/shape errors; they do not establish pixel-level or percentage artistic fidelity. Comparison-only camera estimates and a 180-degree azimuth adjustment match visible ends without claiming a recovered client transform.

Service detail, neutral rear interfaces, fine hatch layouts, physical dimensions and hidden engineering remain authored interpretation. No canopy, engine or weapon is inferred. WorldSize 40 is a size-class proposal, not a recovered dimension or gameplay change; equipment socket and client scale/heading calibration remain separate from asset verification. Final user artistic acceptance remains pending.

## All-Purpose Assault refinement and GLB feedback

AR1A supports a broad pointed green body with small central and lateral grey accents. The name and catalogue establish a small combat role and three equipment slots, but no mapped descriptive narrative, calibrated mounts or original engineering explanation. The first source's central and paired lateral opaque alloy cowls remain an interpretation of those accents. They are not labelled cockpits, engines or weapons.

Two actual ImageGen iterations were reviewed against all 32 paletted headings. The first added extra grey rear-corner plates and was rejected. The second retains exactly three low grey cowls on a broad green planform; sparse surface construction and worn finish guide the remaster. Its inset side-cover placement and more boxy central cover do not override clearer original shoulder accents or establish an exact recovered volume. Exact prompts, input identities, generated images and discrepancy reviews accompany the canonical source and gallery.

The canonical `sources/objects/artemian/all-purpose-assault/model.blend` and `model.glb` replace the historical first study in the active inventory selection. They contain 46,320 triangles in four batches with one material and three embedded PBR maps, reduced from 124,424 triangles and 54 meshes. All 54 part identities remain editable vertex groups. No separate gameplay/menu/SciTek model is introduced.

Actual independent-GLB feedback found excessively sharp manufactured hull and service-cover edges. A small three-segment edge radius softens their perimeter without adding a dense panel grid. The first bevel pass exceeded the existing 55,000-triangle limit, so the surface density was reduced before another actual render/check cycle. Protected dents, fitted overlays, sparse fasteners, dark recesses, stains and scratches remain readable. Checks cover 53 seated connections, four physical dents, closed positive native batches, per-part source-form deviations, actual imported positions and native/import renders. The side reference's opaque bounds are 16 by 8 pixels; an estimated camera and coarse aspect check diagnose substantial errors without claiming precise camera recovery or percentage fidelity.

The recipe-specific edge treatment is inactive for Gerla-Kans. That model was regenerated and independently checked after the shared engine changed: its GLB bytes, geometry and rendered appearance are unchanged; its saved native metadata hash is refreshed honestly. WorldSize 48 remains a size-class proposal; three socket positions, client orientation/scale/material validation and final user artistic acceptance are separate from the asset milestone.

## Reproduction

Generate maps with `tools/author_artemian_mobile_maps.py`. In Blender run `sources/tools/blender/remaster_artemian_mobile_ship.py -- --ship gerla-kans-explorer`; the explicit recipe records preserved parts, profile changes, budgets and checks. Sanitize private source metadata with `tools/prepare_artemian_mobile_publication.py --ship gerla-kans-explorer`, then run `sources/tools/blender/verify_artemian_mobile_ship.py` with the same ship argument. Inspect actual imported renders against legacy and the reviewed concept before updating review bindings. Register with `tools/register_artemian_mobile_remasters.py`, run `tools/test_artemian_mobile_remasters.py`, register the delivery report and rebuild the gallery. Refresh source-bound evidence after actual checks; changing hashes alone is insufficient.

The model uses stable Braccatian mesh/material primitives with a separate Artemian palette and explicit recipe. First-study generators and historical variants are preserved; rerunning them is not a substitute for the current remaster recipe. No game build or device performance certification is claimed by Blender verification.
