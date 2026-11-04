# Authoring workflow

## Independent preparation

```powershell
python tools/asset_workspace.py verify
python tools/asset_workspace.py prepare
```

These commands use current files from `project/layout.json`. They require neither the game repository, original installation, decompilation nor old Git commits. Ordinary preparation excludes standalone historical repair tools. Two archived modules imported by current fighter verifiers are materialized only as support; preparation does not execute them. A separate clean workspace can be selected with `--workspace artifacts/my-workspace`; custom workspaces must be under this project's ignored `artifacts/` directory.

The workspace records the last synchronized hash of each file. A changed canonical source updates a clean workspace copy automatically. Edited or unrecognized workspace files cause a conflict before any inputs are overwritten. If workspace and canonical edits are already identical, preparation accepts them. Resolve a conflict by explicitly publishing the reviewed edit or keeping it in a separate working file; preparation never discards it automatically.

```powershell
python tools/asset_workspace.py blender --blender C:/tools/blender/blender-4.5.15-windows-x64/blender.exe -- tools/blender/verify_assault_fighter.py
python tools/asset_workspace.py python -- tools/Generate-QuickMenuChrome.py
```

The Blender launcher starts a fresh background session and returns a nonzero exit code on Python errors. Model operations run on copies, not hardlinks to canonical sources. Open a canonical Blend directly only when intentionally editing it, and render outside `sources/`.

## Optional original-game evidence

Only semantic/reference audits need this step. Install their optional dependencies with `python -m pip install -r requirements-evidence.txt`:

```powershell
python tools/asset_workspace.py evidence --legacy-root ../legacy --game-root ../openFA-game
python tools/asset_workspace.py references --legacy-root ../legacy --game-root ../openFA-game
```

`evidence` opts into matching C#/naming/decompilation inputs and materializes archived support scripts so historical exact-file checks can read them. `references` also decodes local paletted reference caches and compares them with existing metadata; it does not build scaffold geometry. C# is linked from the game checkout. Naming-code copies and decompilation links exist only in the ignored workspace. Optional semantic checks still reject mismatching historical inputs rather than fabricating verification.

## Edit, review and publish locally

1. Locate the definition and available studies in the gallery/inventory. Preserve completed reconstructions, existing refinements and deferred scaffold work.
2. Read original functional/cultural evidence and inspect correctly paletted reference states. Do not run DOSBox.
3. Edit a workspace source, or deliberately edit the canonical source and prepare again. Keep named moving parts, pivots, hardpoints and authored materials. Add appropriate wear only to newly authored objects.
4. Run relevant source-specific native/imported GLB checks and inspect real renders. Technical validity does not establish artistic or gameplay integration acceptance.
5. Publish reviewed model/code/metadata into their canonical source locations, textures into `sources/materials/`, original 2D inputs into `sources/artwork/` or `sources/ui/`, and finished previews into `gallery/media/`. Update current layout entries for new/relocated inputs; existing entries contain no immutable content hashes.
6. Revalidate affected source-bound inventories/reports after actual source changes. Keep their meaningful acceptance contracts. Do not replace hashes alone to claim a test ran. The optional import audit may now correctly report intentional divergence; do not rewrite historical import evidence to hide it.
7. Rebuild the gallery, run project checks, commit the milestone and record technical English issue results with the commit reference.

## Historical repairs

See `archive/repairs/README.md`. `prepare --include-history` restores archived support files without requiring a game checkout. Reading those files for evidence is different from rerunning them. Direct execution through the launcher requires `--allow-history`, a matching historical workspace and the original game repository's Git history. Already-applied migrations must not be run on current corrected models.

## Game integration

Game workflows can call `ender-dev-pl/openfa-assets/.github/actions/provide-models@<commit-sha>`
to use the organization Actions access grant. GitHub downloads the action repository;
the action exports its root as `OpenFaAssetSourceRoot` through `GITHUB_ENV` for later
MSBuild steps. It validates the catalogue/layout paths and does not perform another
checkout, persist credentials or copy authoring files into the game's workspace.
Pin the action to a published commit containing both the action and intended model
inputs. No cross-repository PAT secret is required. The runner needs PowerShell 7.
Run `pwsh -File tools/Test-ProvideModels.ps1` for the export contract checks.

Package-ready sprites are deliberate generated deliverables. Publish them to the game repository in an explicit integration change. The client does not load this sibling source repository at startup. The three remaining catalogue/presentation snapshots are pinned input contracts; synchronize them deliberately when the game contract changes and rerun affected semantic evidence.
