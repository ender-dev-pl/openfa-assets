# Repository structure

| Path | Purpose |
| --- | --- |
| `sources/tools/blender/` | Procedural modelling, wear, rigging, exporting, reference analysis, native/imported verification and evidence checks |
| `sources/tools/hq-sprite-authoring/` | Existing offline directional sprite and raster upscaling tools |
| `sources/tools/` | Bootstrap UI artwork generation, loading artwork preparation, missile artwork processing and Blender installation |
| `sources/docs/assets/bootstrap-3d/` | Early editable rigs, first building catalogue and existing refined Terran variants; no standalone rendered images |
| `sources/docs/assets/reconstruction/` | Later editable building, ship, hardpoint, missile, scaffold and effect studies, exports and evidence metadata |
| `sources/docs/reconstruction/models/` | Historical research, cultural/function descriptions, inventories, review ledger and source-bound reports |
| `sources/ui/quick-menu/` | Three named PNG inputs used to generate quick-menu UI chrome and icons |
| `sources/content/` | Pinned game-owned input fixtures read by the authoring tools; not a second game implementation |
| `gallery/media/` | Preserved renders, animations, comparisons, reference media and original 2D authoring inputs, retaining their original relative paths |
| `gallery/sheets/` | Newly composed contact sheets of existing renders |
| `gallery/catalogue.json` | Every registered definition/stage and source/export/preview link |
| `tools/` | Current project entry points and gallery generation |
| `migration/` | Exact path/hash manifest and old/new issue crosswalk |
| `.workspace/` | Ignored assembled historical layout used for execution; contains copies, never hardlinks to source files |

The extra historical path levels preserve existing script assumptions and hash-bound evidence. Scripts are not patched just to change a directory spelling. No finished standalone raster, video or rendered HTML file lives under `sources/`. Packed authored textures inside Blend/GLB remain part of the model source.

The original game's decoded pixels are references, not authored replacement textures. Gallery references and independent model output keep their historical separation and provenance. Original game archives, recordings, decompilation and ignored experiments are not relocated by this import.

C# game code and the Ghidra naming script are **not stored in asset sources**. Eleven external evidence inputs are listed in `migration/files.json`. Preparation links `.workspace/src` to the sibling game repository and uses a disposable naming-script fixture only inside the ignored workspace. The durable decompilation remains in the game repository. These dependencies are used by historical semantic audits, not by ordinary modelling, exporting or gallery browsing.

Source PNGs in `sources/ui/quick-menu/` are explicitly registered as `source-input` in the manifest. They are authoring inputs, not finished renders. The workspace maps them back to `content/standard/images/` for the historical generator. Other image/video output remains outside `sources/`.
