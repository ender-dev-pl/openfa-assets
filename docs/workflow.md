# Authoring workflow

## Prepare

Run `python tools/asset_workspace.py prepare` once. It verifies all imported bytes, copies sources and gallery media into `.workspace/`, and creates a local `legacy` directory link to the installed sibling legacy tree. `--legacy-root` and `--game-root` override those sibling locations. If the game repository contains the protected decompilation directory, the workspace links to it without moving it.

Preparation refuses to overwrite an edited workspace file. Preserve your work before preparing again. All canonical source and gallery files remain untouched by executing historical scripts. Opening a `.blend` under `sources/` directly in Blender is supported; render outputs must be directed outside `sources/`.

```powershell
python tools/asset_workspace.py blender --blender C:/tools/blender/blender-4.5.15-windows-x64/blender.exe -- tools/blender/verify_assault_fighter.py
```

The launcher uses a fresh background Blender session and nonzero Python-error exit status. To install the recorded portable Blender version, use the archived `sources/tools/Install-OpenFaBlender.ps1`. The original [installation/rig notes](../sources/docs/blender-asset-workflow.md) remain available; their direct generation commands are historical and must now run in `.workspace/`.

Before legacy semantic checks, run `python tools/asset_workspace.py references`. This decodes a local reference cache from original archives and checks it against existing reference metadata; it does not generate scaffold models or change canonical metadata. C# evidence is read through a directory link to `../openFA-game/src`, without copying C# into this repository. The game Ghidra naming script is only an ignored runtime fixture for the historical functional-text audit.

## Model and review

1. Locate the definition and available studies in `gallery/catalogue.json` and the inventory. Do not rebuild a completed first iteration or create a missing refined version during the current pass.
2. Read the original functional description and cultural architecture evidence before interpreting ambiguous pixels. Inspect correctly paletted legacy views and animation/state frames. Do not run DOSBox.
3. Edit the appropriate script/model in the workspace. Preserve named moving parts, pivots, hardpoints and independent materials. Give newly authored objects wear appropriate to their function; do not retrofit existing models without a separate instruction.
4. Execute the existing source-specific native and GLB verifiers. Inspect actual renders, including mechanisms and all important silhouettes. Technical validity does not establish artistic or runtime-integration acceptance.
5. Explicitly copy reviewed Blend/GLB/scripts/metadata into `sources/` and finished media into `gallery/media/`. Rebind evidence when a hash-bound source changes; never simply replace report hashes to claim a test was run. Regenerate gallery indexes after publishing media.
6. Update the migration import baseline only as deliberate provenance maintenance: `migration/files.json` records the original import, not a moving claim that future modified models still have their imported hashes. Future authoring changes need their own current verification records.
7. Commit each verified milestone and post technical English results to the relevant asset issue with the commit link.

Historical one-time migrations and historical baseline probes are not normal rebuild commands. Some require commits from the original game repository's history. Their retained scripts are evidence; do not rerun them over already migrated/repaired models. Scripts requiring original archives or decompilation remain dependent on those local inputs.

## Game integration

Package-ready sprites remain generated deliverables. Export them into the game repository only through an explicit package-integration task. This migration changes ownership of authoring material; it does not switch the game client to 3D models or replace packaged resources. Catalogue JSON files under `sources/` are pinned fixtures; synchronize them deliberately when the game contract changes and rerun affected evidence.

Quick-menu UI inputs live in `sources/ui/quick-menu/`. Preparation maps them to the historical `content/standard/images/` workspace paths used by `tools/Generate-QuickMenuChrome.py`; the generator produces its outputs only in the ignored workspace until reviewed.
