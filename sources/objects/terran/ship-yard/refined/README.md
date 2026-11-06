# Terran Ship Yard — PB25 high-detail refinement

Canonical selected refinement for `terran:ship-yard`, footprint 3×3. The earlier silhouette and generic refined studies remain in their original folders; this source is shared by gameplay, build-menu and information-screen presentations rather than copied into separate model variants.

- `model.blend`: editable, packed PBR textures, named rigid assemblies and presentation lighting.
- `model.glb`: the same opaque geometry/material atlas and one rigid working/stow/close/reopen loop; no skeletal adapter is required.
- `model.json`: source bindings, geometry budget, reference identifiers and limitations.
- `runtime-validation.json`: actual native reopen, independent GLB import and sampled animation/clearance results.
- `../../../../../gallery/media/objects/terran/ship-yard/refined/`: colour views, a closed state, shared-mesh wireframe and imported-GLB previews.

## Geometry and rendering budget

The asset uses 53,392 triangles, 30 mesh primitives/nodes and one opaque material with authored 1024×1024 albedo, metallic/roughness and emission atlases. Static industrial details are batched into one mesh; the remaining nodes are moving rigid assemblies. There are no alpha-blended surfaces, per-bolt objects, subdivision modifiers or skeletal meshes. Base-pass submissions are bounded by the 30 primitives before any client batching. The static batch requires 32-bit indices, which the current model renderer uses. GPU timing in a populated game scene remains an integration check, not something inferred from these counts.

The atlas contains independently authored paint wear, edge chips, scratches and recessed dirt. No legacy imagery is used as a texture. Procedural Blender-only shaders are unnecessary for the exported appearance. Emissive work lamps are in the model; bloom depends on the renderer.

## Motion and reference limits

The correctly paletted PB25 preview and all 264 frames of PB25.VID establish a circular yard, unequal vessels, crane activity and two opposing closing covers. The legacy English descriptions identify underground pressurised hangars and small-craft construction. Technical ST25 belongs to Shield X40 and is not a shipyard blueprint.

The explicit hidden mechanism in this model is an authored interpretation: a retracting mast, a swivelling boom, trolley/winch and two banks of nested rigid shutter sections. Cover sections slide without scaling their geometry. The timeline is a presentation loop, not recovered gameplay event timing. The mast retracts below the deck; the exterior base occludes the underground stowage volume. No complete underground hangar or calibrated spacecraft sockets are claimed.

Opening/working: frame 1. Crane stowed: frame 100. Closed hold: frames 145–185. Fully reopened: frame 260. The scene uses 30 fps and ends at frame 300. Wireframe previews come directly from these same meshes, not an independently detailed technical model.

## Reproduction

From the repository root, generate the surface maps with `python sources/tools/blender/shipyard_surface_maps.py`, then run `sources/tools/blender/refine_terran_shipyard.py` in Blender 4.5 LTS. `--draft` lowers render resolution/sampling; `--no-render` omits previews. The generator strips publication-only path/image metadata while proving that non-path native bytes and image pixels are preserved. Run `sources/tools/blender/verify_terran_shipyard_refinement.py` afterward in a fresh Blender process.

Source issue: https://github.com/ender-dev-pl/openfa-assets/issues/225.
