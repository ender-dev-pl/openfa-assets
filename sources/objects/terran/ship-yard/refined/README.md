> Historical refinement record. Model payloads in this folder have been replaced by `../model.blend` and `../model.glb` in issue #227. Retained renders and reports describe the earlier mechanism; the current model and transfer contract are documented in `../hangar/README.md`.

# Terran Ship Yard â€” PB25 high-detail refinement

Canonical selected refinement for `terran:ship-yard`, footprint 3Ă—3. The earlier silhouette and generic refined studies remain in their original folders; this source is shared by gameplay, build-menu and information-screen presentations rather than copied into separate model variants.

- `model.blend`: editable, packed PBR textures, named rigid assemblies and presentation lighting.
- `model.glb`: the same opaque geometry/material atlas and one rigid working/stow/close/reopen loop; no skeletal adapter is required.
- `model.json`: source bindings, geometry budget, reference identifiers and limitations.
- `runtime-validation.json`: actual native reopen, independent GLB import and sampled animation/clearance results.
- `../../../../../gallery/media/objects/terran/ship-yard/refined/`: colour views, a closed state, shared-mesh wireframe and imported-GLB previews.

## Geometry and rendering budget

The asset uses 53,616 triangles, 32 mesh primitives/nodes and one opaque material with authored 1024Ă—1024 albedo, metallic/roughness and emission atlases. Static industrial details and the fabrication deck form two batches; the remaining nodes are moving rigid assemblies. There are no alpha-blended surfaces, per-bolt objects, subdivision modifiers or skeletal meshes. Base-pass submissions are bounded by the 32 primitives before any client batching. The static batch requires 32-bit indices, which the current model renderer uses. GPU timing in a populated game scene remains an integration check, not something inferred from these counts.

The atlas contains independently authored paint wear, edge chips, scratches and recessed dirt. No legacy imagery is used as a texture. Procedural Blender-only shaders are unnecessary for the exported appearance. Emissive work lamps are in the model; bloom depends on the renderer.

## Motion and reference limits

The correctly paletted PB25 preview and all 264 frames of PB25.VID establish a circular yard, unequal vessels, crane activity and two opposing closing covers. The legacy English descriptions identify underground pressurised hangars and small-craft construction. Technical ST25 belongs to Shield X40 and is not a shipyard blueprint.

The explicit hidden mechanism in this model is an authored interpretation: a retracting mast, a swivelling boom, trolley/winch and two banks of nested rigid shutter sections. Cover sections slide without scaling their geometry. The timeline is a presentation loop, not recovered gameplay event timing. The mast lowers only until the boom rests on four platform shoes. The hook is reeled in and parked upward, the antenna module folds, and railing openings provide clearance for the resting beam. The partially retracted mast remains inside its base sleeve; the boom does not descend through the platform. No complete underground hangar or calibrated spacecraft sockets are claimed.

Opening/working: frame 1. Crane stowed: frame 100. Closed hold: frames 145â€“185. Fully reopened: frame 260. The scene uses 30 fps and ends at frame 300. Wireframe previews come directly from these same meshes, not an independently detailed technical model.

## Reproduction

From the repository root, generate the surface maps with `python sources/tools/blender/shipyard_surface_maps.py`, then run `sources/tools/blender/refine_terran_shipyard.py` in Blender 4.5 LTS. `--draft` lowers render resolution/sampling; `--no-render` omits previews. The generator strips publication-only path/image metadata while proving that non-path native bytes and image pixels are preserved. Run `sources/tools/blender/verify_terran_shipyard_refinement.py` afterward in a fresh Blender process.

Source issue: https://github.com/ender-dev-pl/openfa-assets/issues/225.

## Configured game-scale comparison

`scale-comparison.json` records the input hashes from the game checkout, selected source hashes and normalization factors. The current surface grid uses 32 world units per cell: this 3×3 yard occupies 96×96 units. The Assault Fighter has a configured longest-axis size of 30 units, or 31.25% of the yard width. The comparison preserves those sizes rather than resizing the fighter to the platform. Views show it beside the yard, above the deck and from above. Its demonstration position is not a calibrated docking socket or a client screenshot.

Run `sources/tools/blender/render_shipyard_scale_comparison.py -- --game-root path/to/openFA-game` in Blender after regenerating the yard. No combined duplicate model is published; the comparison imports the two canonical assets read-only.
