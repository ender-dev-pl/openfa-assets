> New user authorization: render all 101 coloured PNGs and integrate them into the shared asset gallery. Gallery PNGs are separate from the earlier legacy-size compact/detail image targets. Model sources remain preserved.

# Trading goods — persistent coloured-model reconstruction

User objective: reconstruct **all coloured editable trading-good models**, one after another, reusing related finished models/construction families where useful. **Final image generation is deferred.** This supersedes the initial image-first plan. Tracking: [issue #214](https://github.com/ender-dev-pl/openfa-assets/issues/214). Branch: `feat/trading-goods-reconstruction`, based on `origin/main`; cinematic work is separate.

[coverage.json](coverage.json) is the machine-readable ledger; [ITEMS.md](ITEMS.md) lists model progress. Track model completion independently from compact/detail image targets. The catalogue has 101 identities: 68 ordinary goods, five treatments, four anti-personnel-virus containers, ten ores, thirteen Terran missiles and one information bundle. Identities 0–100 map to `_TRADE/TI001`–`TI101`.

## Gallery PNG checkpoint

All 101 colour PNGs are now rendered at 768×576 with transparency and linked in the shared asset gallery. [Browse trading goods](../../gallery/trading-goods-shared.md), or open the [interactive filter](../../gallery/index.html#type=trading-goods). Model sources remain unchanged; render journals bind image hashes to native/renderer hashes. PNG metadata is removed without changing decoded pixels. The newly requested material-refinement pass will preserve this first image set as an earlier iteration.

`python tools/build_gallery.py --from-catalogue` rebuilds the shared index using preserved baseline catalogues, without requiring unrelated media to be materialized in a sparse checkout. Full checkouts retain the existing default builder behavior. `tools/verify_trading_gallery.py` checks PNG content, source hashes and gallery links.

## Current state

**101/101 coloured models are complete for the first reconstruction pass.** All 202 final images remain deferred. See [COMPLETION.md](COMPLETION.md) and [catalogue-validation.json](catalogue-validation.json). No models should be regenerated merely because image targets are deferred.

## Evidence and workflow

Read the game repository's `docs/legacy/trade-information.md` and the item's recovered localization description/cultural evidence. Inspect its correctly paletted `TIxxxBIG.256` colour reference locally before authoring. The compact monochrome 108×80 and colour 216×160 image variants remain future output targets; technical preview renders are solely model inspection aids. Do not publish or project original pixels as textures.

Continue from the earliest item whose `model_status` is not `coloured_model_verified`. Sources live in `sources/docs/assets/reconstruction/trading-goods/TIxxx/`, with authored tools in `sources/tools/trading-goods/`. Preserve named editable parts and material assignments. Add function-appropriate wear. Reuse construction functions and existing sources as appropriate; `derived_from` records a related construction family or native-source lineage, not necessarily a byte-level clone.

Run `build_model.py --item N --out /path/to/ignored/work/TIxxx` in Blender 4.5 LTS. The generator saves a native and static GLB. `verify_model.py --native NATIVE --glb GLB --report REPORT --preview INSPECTION_PNG` reopens the native, renders a technical inspection, independently imports GLB, compares evaluated geometry bounds and object coverage, and verifies used Principled base colours survive the round trip. Procedural wear remains in native shader graphs; GLB material baking and game integration are not claimed.

Inspect actual model previews against source evidence. Only then mark the coloured model verified, record source/reference hashes, update coverage and register authored assets/tools in `project/layout.json`. Production images stay deferred; native/GLB checks alone do not establish final visual likeness. Commit and push each verified major milestone with issue #214. Continue through the entire catalogue, retaining finished versions and deferring refining unless requested.

No original installation or decoded reference cache is required to open/render published model sources. Original media, decoded references and technical inspection sheets stay local under ignored `artifacts/`.
