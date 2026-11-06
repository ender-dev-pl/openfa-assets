# Asset authoring instructions

- Use this repository's `origin` for asset issues. Keep issue documentation technical and in English; link committed milestones. Use Conventional Commits with the issue number and commit each verified milestone.
- Use branches prefixed by `feat/`, `fix/`, `docs/` or `chore/`, not `codex/`.
- Do not start another feature before committing the current milestone. Preserve user files and existing models.
- Keep finished renders, reference media and contact sheets outside `sources/`. Run historical generators in the isolated workspace described in `docs/workflow.md`.
- Preserve completed first iterations/refinements. Refining and scaffolding remain deferred unless requested. Obvious technical defects may be corrected with focused evidence.
- New objects need material/function-appropriate grime, scratches, stains and minor dents while keeping their silhouettes readable. Do not retrofit existing models, including RI01, without explicit scope.
- Read original function and culture evidence and inspect correctly paletted legacy frames before modelling. Treat reference pixels as evidence, not replacement textures. Do not use DOSBox.
- Verify editable sources and independent GLB imports in actual Blender runtime; inspect rendered output. Never infer final visual, state, attachment or integration acceptance from file existence or polygon counts.
- Keep source-bound evidence honest. Update evidence after actual validation, never by replacing hashes alone. Consult migration issue mappings before using historical bare issue numbers.
- New tools need focused verification. Asset-only work uses Blender as its target runtime. For game integration, follow the game repository's quality/build/runtime requirements.

## Persistent objective: trading goods

- Branch `feat/trading-goods-reconstruction` tracks reconstruction of all trading-good assets; see origin issue #214 and `docs/trading-goods/README.md`.
- The user-authorized coloured-model phase is complete: TI001–TI101 have editable natives, coloured static GLBs, inspected technical previews and runtime reports. Read `coverage.json` and `COMPLETION.md` before new work; do not restart completed items.
- Latest user scope authorizes a material-refinement pass for all 101 goods, including transparency, reflections and surface irregularities, followed by high-quality PNGs and a gallery update. Preserve all first-pass sources and PNGs; see docs/trading-goods/REFINEMENT.md. Exact legacy-size monochrome/detail UI outputs are separate from these gallery renders.
- Related native models and construction families may be reused, preserving each completed source and recording lineage. Artistic refining and game integration require their own scope; retain original reference and cultural/description evidence locally.

- The material-refinement/gallery pass is complete: all 101 items have selected refined natives and reviewed 1024×768 PNGs alongside the first pass. Read each coverage item’s `refined_variant`, `refinement-selections.json` and `refinement-validation.json` before continuing. TI041/TI064 are remodelled; TI048/TI067 have geometry repairs. Preserve all completed variants and first-pass PNGs. Full shaders are in Blend; GLB textures remain unbaked. Legacy UI targets remain separate.

- Read docs/trading-goods/LORE-AUDIT.md and lore-audit.json before further refinement. All 101 descriptions were reviewed. Do not equate technical PNG/GLB validation with semantic accuracy; the seven explicit material/cut/product-state/count conflicts have separate verified lore/ corrections. Current review: 71 core_match, 28 partial, 2 ambiguous; follow the remaining per-item priorities. Keep ambiguous icon/text cases (TI007/TI063) explicit. Current TI064 uses the separate ceremonial craft revision.
