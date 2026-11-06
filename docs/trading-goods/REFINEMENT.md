# Trading-good material refinement

The second pass preserves all 101 first-pass natives, GLBs and gallery PNGs. New editable files live in `sources/docs/assets/reconstruction/trading-goods-refined/TIxxx/`. Tracking: [#214](https://github.com/ender-dev-pl/openfa-assets/issues/214), branch `feat/trading-goods-reconstruction`.

## Materials and geometry

Material roles follow the existing named parts and recovered item descriptions. Metals use conductive reflection, anisotropy and fine machining variation. Glass and gems use transmission, refractive indices and volume absorption. Fabrics use crossed weave relief, tinted sheen and different roughness for velvet, raw silk, satin and cotton. Leather has pore relief; wood has stretched grain; organic materials have restrained subsurface scattering. Paint, ceramic, carbon, paper, horn and pearls retain their own responses.

Low-amplitude colour and roughness variation avoid uniform plastic shading. Organic, horn, stone and fabric meshes receive deterministic small normal displacement. Manufactured edges receive small radii where appropriate. Cask stickers are moved outside the shell; the cheese's cut-face proxy dots are replaced by actual Boolean cavities. These are refinements of the existing reconstruction, not new historical evidence for unseen details.

The **native Blender files contain the complete procedural materials**. GLBs deliberately carry scalar physical parameters and base colours; procedural colour/normal/roughness graphs are not baked to texture maps. GLB viewing therefore does not reproduce the native render exactly. Texture baking and engine integration are separate work.

## Reproduce and validate

Requires Blender 4.5 LTS, Python 3 and Pillow for gallery publication. Original game media is not required to open these authored sources. From the repository root, in an environment with `blender` on PATH:

```sh
python sources/tools/trading-goods/refining/batch.py --repo . --jobs 4
```

The batch builds missing models, independently reopens each native and imports each GLB, compares evaluated world bounds and base colours, and renders 1024×768 transparent PNGs. It checks source/tool hashes before reusing output. Logs and raw PNGs remain under ignored `artifacts/trading-goods-refining/production/`. Each source folder has `refinement.json` lineage/material evidence and `runtime-validation.json` import evidence.

The studio renderer uses Cycles, adaptive sampling up to 32 samples for opaque goods and 64 for glass/gems, denoising, three rectangular softboxes, a neutral world and a transient shadow catcher. Render staging is not saved into the model or exported as goods geometry. Each render journal records the actual native and renderer hashes, resolution, settings and output hash. It also verifies that rendering did not modify the source.

Inspect all rendered items, including glass, gems, fabrics, metal, organic objects and the inherited missiles. Record `reviewed_items` (TI identifiers), observations and a `reviewed_images` map in a local review JSON. For each actually inspected item, copy `native_sha256` and `image_sha256` from its render journal into that map. These hashes bind visual review to the exact source and raw PNG, so replacing a render requires a new review. Publication refuses an incomplete review set or stale source/render evidence:

```sh
python tools/publish_trade_refinement.py --renders artifacts/trading-goods-refining/production --review artifacts/trading-goods-refining/visual-review.json --consume
python tools/build_gallery.py --from-catalogue
python tools/verify_trading_gallery.py
python tools/verify_trade_refinement.py
node tools/test_gallery_filters.cjs --filters-only
```

Publication removes ancillary PNG metadata and losslessly recompresses the identical filtered scanline stream when smaller, without altering decoded pixels. Optional `--consume` removes raw PNG duplicates only after comparing decoded pixels against the installed file, keeping source/render journals and hash-bound publication receipts. Interrupted publication can resume from verified installed images. `docs/trading-goods/refinement-validation.json` binds published PNGs to the independently verified native and GLB files. The gallery retains both iterations under each of the existing 101 goods cards. Existing building, ship, scaffold, missile and cinematic gallery records remain preserved.

This pass does not replace the separate legacy-size compact/detail UI image targets or claim game integration. Artistic review remains iterative; the original low-resolution evidence still limits inferred small details.

## TI041 geometry correction

The user rejected the first-pass coat and boots as too angular. `TI041/remodelled/` is a separate reconstruction with a continuous fitted open-front shell, turned lapels, actual leather thickness and dark lining, bent closed-shoulder sleeves, hanging folds, shaped boot lasts and calves, ankle creases, layered soles and a flat belt. Raised decorative trim and saddle seams follow the curved surfaces. Ornament is an authored approximation of the low-resolution evidence. The original model and material-only checkpoint remain preserved.

`refinement-selections.json` selects this geometry revision for publication and batch rendering. The remodel's lineage records both the original model and the preserved material-only native. Its own geometry-builder hash supplements the original shader-builder evidence. `remodel_leather.py` rebuilds the selected variant from the material-only checkpoint; `batch.py` handles the selection when rendering or rebuilding missing outputs.

## Gem absorption correction

Actual studio review showed that the first transparent shader washed out ruby/astramarine hues. Selected `optical/` variants increase volume absorption, with lower density for diamonds/metachrome and intermediate density for opal/moonstone. `tint_gems.py` changes only the native volume shading. Meshes and scalar GLBs remain unchanged, with preserved preceding sources and independent native/GLB validation. The selection ledger records the revised deliveries.

## TI048 cut-face topology repair

Full-resolution review exposed a dark slit between cheese cavities. The separate `TI048/repaired/` variant welds near-coincident displaced Boolean bridge vertices, triangulates holed cut-face polygons and recalculates normals. The raw wheel mesh changes from 17 nonmanifold edges to zero, while preserving the earlier source checkpoint and actual cavities. This variant has its own native/GLB runtime validation and source-bound studio render.

## TI067 bowl correction

The red lining accidentally included a rim-height cap, hiding the intended hollow bowl once flat caps were shaded correctly. `TI067/repaired/` removes that cap, orients the enamel towards the interior with actual coating thickness, restores reflective enamel and moves handles outside the bowl wall. This follows the existing documented hollow red-lined construction; the reference is ambiguous about lining versus contents, so no new historical detail is claimed. Earlier checkpoints remain preserved.

## Missile studio exposure

The inherited missile family uses the same softboxes and neutral world with exposure −1.0 instead of −0.2, retaining dark coated-metal colours. `renderer_overrides` selects the frozen `render_missiles.py` preset for TI088–TI100. Both studio scripts are source-bound by per-image hashes; all other goods retain the original renderer. This changes presentation, not model geometry or source materials.

## TI064 geometry refinement and cup clearance check

The user rejected TI064’s primitive blade geometry. `TI064/remodelled/` replaces the flat outline with thick stepped crescent blades, convex cutting arcs, tapered burnished bevels, a forged head socket with peened pins and a smoothly turned hardwood haft with longitudinal grain. The silhouette follows the local reference; restrained lunar inlays interpret the Cyreni description and are not recovered glyphs. Earlier versions remain preserved.

The current TI067 handles are independently checked by `verify_cup_clearance.py`: evaluated vertices stay outside the radial cavity profile and BVH triangles do not intersect the inner enamel lining. Source-bound results are in its `clearance-validation.json`. The batch runner also uses Blender’s Python error exit code so script failures cannot be mistaken for successful subprocesses.
