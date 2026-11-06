# Repository structure

| Path | Purpose |
| --- | --- |
| `sources/tools/blender/` | Reusable modelling, material, rigging, export, reference and verification tools |
| `sources/tools/hq-sprite-authoring/` | Offline directional sprite and raster upscaling tools |
| `sources/tools/` | UI, loading-artwork and missile image generators, local decoder fixtures, Blender installer |
| `sources/materials/` | 698 independently authored colour/roughness PNG inputs, grouped by object |
| `sources/artwork/` | Original 2D authoring images/animations, bootstrap prompts and palette |
| `sources/ui/quick-menu/` | Three source PNG inputs for menu chrome and icons |
| `sources/docs/assets/` | Native models, GLB exports and source-bound metadata in their retained historical hierarchy |
| `sources/docs/reconstruction/models/` | Functional/cultural research, inventories, review ledger and technical evidence |
| `sources/content/` | Only the three catalogue/presentation JSON snapshots actually consumed by asset tools |
| `gallery/media/` | Existing finished renders, animations, comparisons and reference imagery |
| `gallery/sheets/` | Contact sheets assembled from existing previews |
| `gallery/catalogue.json` | Current registered study/source/export/preview links |
| `project/layout.json` | Current canonical destinations, input roles and logical workspace paths; no frozen content hashes |
| `archive/repairs/` | Five immutable one-time repair/proposal scripts, retained as evidence |
| `migration/` | Frozen import hashes, one-time import recipe and original/new issue crosswalk |
| `tools/` | Current preparation, validation and gallery entry points |
| `.workspace/` | Ignored disposable execution layout, synchronized without overwriting edited files |

Native Blend/GLB files retain packed authored textures. Source textures and 2D image inputs are explicitly registered with `material-texture` or `source-input` roles. Finished raster/video/HTML output is rejected under `sources/`; a bitmap extension alone does not make an authoring input a render.

The original logical paths are recreated in the workspace. Relocation changes neither model bytes nor archived script/report hashes. Four unused game snapshots (factions, personnel, research and Terran construction) were retired; their original hashes remain in the import record and their authoritative copies stay game-owned.

C# and Ghidra code are not versioned here. Ordinary preparation does not inspect or link the game checkout or a legacy installation. The explicit `evidence`/`references` commands enable old semantic-audit inputs. Existing local links/caches are not deleted when switching back to ordinary preparation; use a fresh custom workspace to demonstrate independence.
