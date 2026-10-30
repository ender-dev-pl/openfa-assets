# Blender UI kit

Tracking: [#176](https://github.com/ender-dev-pl/openfa-assets/issues/176),
integrated by [game #1124](https://github.com/ender-dev-pl/ed-openfa-game/issues/1124).

64 semantic, extruded metal pictograms and 28 panel/button renders. The three
button sizes each have normal, selected, pressed, disabled and hover states.
The other thirteen renders provide reusable panel, header and quick-menu chrome.
New materials have restrained noise-based grime and abrasions; existing model
assets were not modified. Silver bevels, dark recesses and cobalt/amber accents
use the correctly paletted Legacy FA side of the game's
`docs/assets/issue-627/menu-comparison.png` as shape/layout evidence.

![Authored Blender symbol contact sheet](media/ui/blender-kit/source-contact.png)

![Independent GLB geometry and base-material import](media/ui/blender-kit/imported-contact.png)

The frontend console includes a machined navigation globe and raised OPENFA plate.

![Blender frontend console](media/ui/blender-kit/frontend-edge.png)

The GLB proof preserves evaluated geometry and constant base material parameters.
Procedural wear remains in the editable Blend and the delivered Cycles PNGs;
the GLB is a geometry/base-material verification export, not the game UI payload.

| Normal | Selected | Pressed | Disabled | Hover |
| --- | --- | --- | --- | --- |
| ![Normal](media/ui/blender-kit/gameplay-normal.png) | ![Selected](media/ui/blender-kit/gameplay-selected.png) | ![Pressed](media/ui/blender-kit/gameplay-pressed.png) | ![Disabled](media/ui/blender-kit/gameplay-disabled.png) | ![Hover](media/ui/blender-kit/gameplay-hover.png) |

[Editable Blend](../sources/ui/blender-kit/ui-kit.blend),
[GLB proof](../sources/ui/blender-kit/ui-kit.glb),
[generator](../sources/ui/blender-kit/build_ui.py),
[metadata](../sources/ui/blender-kit/ui-kit.json).

Reproduce with Blender 4.5 LTS (Cycles CPU, 24 samples, AgX/None, transparent RGBA):

```powershell
blender --background --factory-startup --python-exit-code 1 `
  --python sources/ui/blender-kit/build_ui.py -- `
  --output gallery/media/ui/blender-kit
```

The generator creates only this kit's sources and renders. `--proof-only` refreshes
the source/contact/import checks without rerendering all deliverable PNGs.
Run `python sources/ui/blender-kit/verify_ui.py --renders gallery/media/ui/blender-kit`
to verify rendered silhouettes, occupied symbols and state coverage. The verified
native/imported silhouette IoU is 1.0 (125,550 occupied pixels on each side);
`verification.json` records the current source and rendered proof hashes.
The game publishes reviewed renders through `tools/Import-BlenderUi.py`, preserving
its resource IDs, dimensions, states and native/tiled view contracts. Runtime
requires no Blender installation or sibling asset checkout.
