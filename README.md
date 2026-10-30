# OpenFA assets

Editable artwork, procedural generators and verification tools for the alternative OpenFA visual presentation. This repository owns asset authoring; [ed-openfa-game](https://github.com/ender-dev-pl/ed-openfa-game) owns gameplay, runtime rendering and packaged resources.

**[Browse the model gallery](gallery/README.md)** · **[Interactive catalogue](gallery/index.html)** · [Workflow](docs/workflow.md) · [Project structure](docs/structure.md) · [Verification](docs/verification.md) · [Provenance](docs/provenance.md)

The imported inventory covers **303 definitions**: 177 buildings, 41 ships/vehicles, 16 hardpoints and 69 missiles across seven cultures. It registers **366 existing study entries**, including available refined studies. The source archive contains **396 Blend files and 405 GLB files**, including earlier variants, reusable rigs and effects. Definition counts, file counts and unique geometry counts are different measures.

The gallery uses existing renders only. It shows each registered iteration with its original stage label, editable source and available GLB. No model or refined variant was generated for this migration. First-source coverage does not mean final artistic acceptance, complete animation, calibrated attachments or game integration.

## Quick start

Requires Python 3.10+; install `requirements.txt`. Model operations require Blender 4.5 LTS. Legacy evidence checks additionally require a local original-game installation in the sibling `legacy` directory and its decoding tools; these files are not bundled here.

```powershell
python -m pip install -r requirements.txt
python tools/asset_workspace.py verify
python tools/asset_workspace.py prepare
python tools/asset_workspace.py references
python tools/asset_workspace.py python -- tools/blender/audit_first_source_coverage.py --check
python tools/asset_workspace.py python -- tools/blender/verify_reconstruction_inventory.py
```

Open `gallery/index.html` locally for search/filtering, or use the Markdown gallery on GitHub. To rebuild thumbnails and indexes from the preserved renders:

```powershell
python tools/build_gallery.py
```

Run Blender scripts through the assembled workspace; see [the workflow](docs/workflow.md). Sources and finished images are deliberately stored separately. Outputs produced during authoring remain in the ignored `.workspace/` until reviewed and explicitly published to the corresponding source or gallery destination.

## Current scope

Preserve completed reconstructions and existing refinements. New artistic refining and scaffolding work remain deferred. Obvious technical defects may be repaired with focused verification. New objects receive function-appropriate wear; existing models are not retrofitted merely because they are regenerated.

The migration preserves exact imported bytes and historical evidence identifiers. [Migration manifests](migration/README.md) map every original path, checksum and transferred issue. Historical documentation is retained under `sources/docs/reconstruction/models/`; its paths refer to the assembled workspace and its bare issue numbers use the original game-repository numbering.
