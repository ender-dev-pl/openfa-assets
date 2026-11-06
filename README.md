# OpenFA assets

This is the sanitized public snapshot. See [publication policy and metadata evidence](docs/publication.md).

Editable artwork, procedural generators and verification tools for the alternative OpenFA visual presentation. This repository owns asset authoring; [ed-openfa-game](https://github.com/ender-dev-pl/ed-openfa-game) owns gameplay, runtime rendering and packaged resources.

**[Browse the model gallery](gallery/README.md)** · **[Interactive catalogue](gallery/index.html)** · **[Construction videos](gallery/construction-animations.html)** · [Workflow](docs/workflow.md) · [Project structure](docs/structure.md) · [Verification](docs/verification.md) · [Provenance](docs/provenance.md)

The imported inventory covers **303 definitions**: 177 buildings, 41 ships/vehicles, 16 hardpoints and 69 missiles across seven cultures. It registers **366 existing study entries**, including available refined studies. The source archive contains **396 Blend files and 405 GLB files**, including earlier variants, reusable rigs and effects. Definition counts, file counts and unique geometry counts are different measures.

The gallery uses existing renders only. It shows each registered iteration with its original stage label, editable source and available GLB. No model or refined variant was generated for this migration. First-source coverage does not mean final artistic acceptance, complete animation, calibrated attachments or game integration.

[New main-menu labels](gallery/menu-labels.md) provide shade-only fields and separate EN/PL lettering aligned with the original menu reference.

## Licensing

Asset-specific recipes, parameters, models, textures and animations use the [OpenFA Asset License 1.0](LICENSE.md) ([Polski](LICENSE.pl.md)). Regenerating protected asset content does not remove these conditions. Audited general-purpose tools use [MIT](LICENSES/MIT.txt); the reusable package is in [tooling/](tooling/README.md). Existing third-party terms and the provenance of recovered legacy data are listed separately. Read the [component licensing guide](docs/licensing/README.md) and [contribution rules](CONTRIBUTING.md); there is no blanket MIT grant over every Python generator.

## Quick start

The [HUD and menu gallery](gallery/ui.html) contains editable interface geometry, button
states and semantic icons alongside the [model gallery](gallery/README.md).

Requires Python 3.10+; install `requirements.txt`. Model operations require Blender 4.5 LTS. Optional legacy evidence checks use `requirements-evidence.txt` and additionally require a local original-game installation in the sibling `legacy` directory and its decoding tools; these files are not bundled here.

```powershell
python -m pip install -r requirements.txt
python tools/asset_workspace.py verify
python tools/asset_workspace.py prepare
```

Open `gallery/index.html` locally for combined search, race and asset-type filters. Its expandable index links to filter combinations; the Markdown gallery provides the same race/type table on GitHub. To rebuild thumbnails and indexes from the preserved renders:

```powershell
python tools/build_gallery.py
```

Animated GLB studies include local WebM previews with play/pause, a timeline and looping; downloads are deferred until playback. Static studies retain their still render. To regenerate previews after changing an animated source, run `sources/tools/blender/render_gallery_animations.py` in Blender before rebuilding the gallery. The index rejects previews whose GLB, native lighting/framing source or renderer hashes are stale.

Preparation works without a game checkout or original installation. Enable `evidence`/`references` only for legacy semantic checks. Run Blender scripts through the assembled workspace; see [the workflow](docs/workflow.md). Sources and finished images are deliberately stored separately. Outputs produced during authoring remain in the ignored `.workspace/` until reviewed and explicitly published to the corresponding source or gallery destination.

## Current scope

Preserve completed reconstructions and existing refinements. The user-requested [RIS2 scaffold refinement](gallery/scaffolds-ris2.md) is available separately from the preserved prototype. The [culture scaffold kits](gallery/scaffolds-cultures.md) extend this construction/reveal approach to all remaining used families, respecting CDB material lore. Other artistic refining remains deferred. Obvious technical defects may be repaired with focused verification. New objects receive function-appropriate wear; existing models are not retrofitted merely because they are regenerated.

The [import baseline](project/import-baseline.json) records original input paths and checksums required by the optional evidence tools. Historical documentation is retained under `sources/docs/reconstruction/models/`; its paths refer to the assembled workspace and its bare issue numbers use the original game-repository numbering.

Current paths and roles live in [project/layout.json](project/layout.json). Material maps belong under `sources/materials/`, original image/animation inputs under `sources/artwork/` or `sources/ui/`, and finished renders under `gallery/`. The import baseline remains in `project/`; archived repair support remains in `archive/repairs/`. Use `audit-import` only to compare with the original revision; normal authoring accepts reviewed source edits.
