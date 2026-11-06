# Coloured model phase completed

The authorized model-only phase delivers **101 coloured model sets**, TI001–TI101, each with an editable `.blend`, coloured static `.glb`, source/reference observations and a source-bound Blender runtime report. **All 202 production images remain deferred by the user.** Technical inspection renders and original references stay local; no image-delivery completion is claimed.

## Verification

All 101 natives were reopened in Blender 4.5 LTS and rendered for model inspection. All 101 GLBs were imported independently, compared for evaluated mesh coverage and world-space bounds, and checked for preservation of used Principled base colours. The final catalogue audit verifies contiguous identities, registered source paths, actual binary hashes, GLB structure/material factors, per-item evidence linkage, inherited-source proofs and deferred image states. See [catalogue-validation.json](catalogue-validation.json).

Run the standalone audit without Blender or original game media:

```sh
python sources/tools/trading-goods/audit_catalogue.py --repo .
```

This is the first reconstruction pass, not final artistic/game-integration acceptance. Hidden structure, small ornaments, unreadable symbols and some arrangements are inferred. Native shader graphs retain procedural wear; procedural-material baking to GLB is not claimed.

## Reuse and preservation

Related bottles, cloth rolls, jewellery, gems, cases and containers share construction functions with separate saved outputs. TI078–TI081 copy the completed TI001 casks, matching the reused original reference packaging. TI088–TI100 reuse the existing Terran missile natives: local mesh data and shader graphs are preserved, the assembly is reoriented, and inspection cameras/lights are replaced. Each missile folder records source SHA256, geometry-preservation proof and lineage. Original completed sources remain unchanged.

## Pushed model milestones

| Items | Commit |
|---|---|
| TI001–TI008 | `5ae2728` |
| TI009–TI015 | `9c25eb4` |
| TI016–TI024 | `5a3feb7` |
| TI025–TI037 | `fb93c16` |
| TI038–TI048 | `02e0fef` |
| TI049–TI052 | `7c08434` |
| TI053–TI060 | `6dbb644` |
| TI061–TI068 | `3901d81` |
| TI069–TI077 | `b631956` |
| TI078–TI087 | `269421d` |
| TI088–TI100 | `b5fe2c6` |
| TI101 | `6b48e30` |

Branch: `feat/trading-goods-reconstruction`. Umbrella: [issue #214](https://github.com/ender-dev-pl/openfa-assets/issues/214). The subsequently authorized gallery/material phase is complete below; do not restart the first model phase because legacy UI targets are deferred.

## Material and gallery refinement complete

101 selected native-material variants and 101 new 1024×768 RGBA gallery PNGs are complete, reviewed and source-bound. All original 101 natives, GLBs and 768×576 PNGs remain preserved. The shared gallery keeps 101 trading cards with both iterations; its existing 303 primary non-trading records and 137 supplemental cards remain preserved.

The pass adds role-specific procedural colour/roughness/normal detail, glass/gem transmission and absorption, reflective metals, fabric weave/sheens, leather pores, organic subsurface response and restrained geometry irregularity. TI041 and TI064 are separately remodelled; TI048 and TI067 receive focused geometry repairs. This is another reconstruction iteration, not final artistic/game-integration acceptance.

| Source milestone | Commit |
|---|---|
| 101 physical material/surface natives and runtime checks | `4277cdd` |
| TI041 tailored coat, rounded boots and belt | `2b2cb3c` |
| Gem absorption/hue correction | `702b8d8` |
| TI048 Boolean seam repair | `440ae88` |
| TI067 open bowl and handle repair | `f160567` |
| Family-specific studio exposure | `e1418d3` |
| TI064 crescent axe and independent cup-clearance check | `46b5da7` |

Validation covers actual Blender 4.5.15 LTS native reopen/independent GLB import, geometry bounds and base-colour round trip; all 101 rendered outputs visually inspected with source/image hashes; lossless PNG metadata removal/recompression and pixel equality; RGBA framing; preserved first-pass files and baseline gallery records; gallery filter/search behavior and actual desktop/mobile Chromium inspection. Final per-item evidence is in `refinement-validation.json`.

Full procedural shaders remain in Blend. GLBs are unbaked scalar/base-colour fallbacks. The separate 202 legacy-size compact/detail UI outputs and engine integration remain deferred. See `REFINEMENT.md` for reproduction and publication commands.
