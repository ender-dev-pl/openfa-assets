# Trading goods — persistent reconstruction objective

Reconstruct the images of **all trading goods**, retaining editable authored model sources and rendered images. This is a persistent objective across sessions, not a one-session batch. Tracking: [issue #214](https://github.com/ender-dev-pl/openfa-assets/issues/214). Branch: `feat/trading-goods-reconstruction`, created from `origin/main`; cinematic work remains on its own branch.

## Coverage and identity

[coverage.json](coverage.json) is the machine-readable work ledger; [ITEMS.md](ITEMS.md) is the initial human-readable checklist. The recovered market catalogue has 101 stable identities, with 202 image targets:

| Market IDs | Category | Items |
|---|---|---:|
| 0–67 | Ordinary inter-culture goods; first authoring batch | 68 |
| 68–72 | Disease treatments | 5 |
| 73–76 | Anti-personnel viruses | 4 |
| 77–86 | Ores | 10 |
| 87–99 | Terran missiles | 13 |
| 100 | Information bundle | 1 |

Every zero-based ID maps to a one-based `_TRADE/TIxxx.256` compact monochrome preview (108×80 canvas) and `_TRADE/TIxxxBIG.256` coloured detail preview (216×160 canvas). Both variants require reconstruction and visual review. The scope ledger includes the entire market archive to avoid silently omitting its non-ordinary categories. Catalogue IDs, names and culture/function descriptions must remain linked to their recovered identities; do not infer identity from a filename's appearance alone.

Evidence: game repository `docs/legacy/trade-information.md` and `content/standard/localization/en.json`. The manifest records localization keys and the inspected file hash; reference images and descriptions must be reviewed locally before modelling. The original game installation/media is optional evidence, never a dependency for rendering published authored models. Do not publish original images or use them as replacement textures.

## Continue in a new session

1. Read repository authoring instructions and this objective; consult issue #214 and the current coverage ledger.
2. Select the earliest uncompleted ordinary good, or continue the recorded in-progress item. Inspect its correctly paletted compact/detail references and description/cultural evidence before deciding geometry, materials and camera.
3. Author separate named objects in Blender, with function-appropriate wear and reusable materials. Keep previous completed work. Render compact monochrome and detailed colour variants from authored sources; higher-resolution masters may accompany the native-size images.
4. Reopen the native source, independently import its static GLB, inspect actual renders of both variants, and retain source-bound validation reports. Geometry checks do not establish visual likeness or game integration. Record failures and unresolved matching honestly.
5. Update the item's source/output paths, evidence-review state and validation links. Mark complete only after both images have been rendered and visually checked. Register actual asset sources/media in `project/layout.json` when they are added; keep renders outside `sources/`.
6. Commit and push each verified major milestone using Conventional Commits with the origin issue number. Continue until all targets are complete; do not stop because one illustrative item exists. Refining finished items remains deferred unless requested.

## Initial checkpoint

All 101 items and both variants are **planned**. This branch-establishment milestone creates no new models, renders or validation claims. Start with ID 0, `TI001`, **Beers**, after reviewing both reference variants and its recovered description.
