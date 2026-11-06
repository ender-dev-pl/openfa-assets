# Legacy-aligned main-menu labels (#206)

Replaces the rejected dark metal label wells with a quiet shade-only field and
small grey serif lettering. Earlier menu kits and the #204 adapter remain unchanged.
This is a Python/Pillow 2D asset delivery; no 3D model or gameplay behavior changes.

## Evidence and interpretation

The supplied legacy main-menu frame was inspected, along with game
`docs/legacy/fe-tag-menu-usage.md` and `frontend-callbacks-and-composition.md`.
The main menu uses BOX shading at `(456,28+64n)`, size `184x46`, style
`0xFFFF240D`, shade row 13: approximately `208/256` destination brightness.
It does **not** draw FE_TAG or a framed black nameplate. The substrate remains visible.
The observed FONT.256 labels have small grey serif forms and a black edge.

The new RGBA shade uses black alpha 48 to approximate that brightness on truecolor
artwork; legacy palette quantization is not claimed. Hover/pressed/selected/off
feedback is an authored extension. Noto Serif Bold 14 px is an openly licensed
stylistic interpretation, **not** an exact reconstruction or copy of FONT.256.
Font source and OFL 1.1 license are bundled; provenance is recorded by hash.
Source: [Noto Serif Bold](https://github.com/notofonts/noto-fonts/blob/main/hinted/ttf/NotoSerif/NotoSerif-Bold.ttf),
[license](https://github.com/notofonts/noto-fonts/blob/main/LICENSE).
No original-game pixels or reference screenshots are distributed in this kit.

## Integration

Finished files: `gallery/media/ui/legacy-menu-labels/`; `catalog.json` supplies
hashes, composition coordinates and integration warnings.

- Prefer separate `label-shade-STATE.png` (184x46), `socket-STATE.png` (44x46),
  existing semantic colored caps, and localized live text using the font atlas.
- Alternatively use `rows/row-THEME-STATE.png` (211x48), which already includes
  shade and socket. The four theme aliases are deliberately identical.
- **Remove the old framed row and its extra shade rectangle** before composing
  these assets. Do not draw both the row PNG and separate shade/socket.
- Native canvas is 640x480, row anchor `(429,27)`, pitch 64. Shade anchor is
  `(456,28)`, socket center `(450,50)`, cap bounds `(434,34,32,32)`;
  text center is `(554,51)`. Increment vertical positions by `64*n`.
  These are legacy-aligned anchors, not the rejected adapter's shifted socket.
- Text remains separate. Optional EN/PL string PNGs have a transparent 184x46
  canvas at the shade anchor, including a two-line multiplayer/no-network label.
  `font-atlas.png` plus `font.json` provides 319 Unicode glyphs covering ASCII,
  Latin-1 and Latin Extended-A, including Polish letters and mixed-case titles.
  Atlas RGBA already contains the grey ink and black edge; do not flat-tint it.
  `offset` is relative to the text baseline pen and `advance` moves that pen.
- Do not globally replace unrelated UI fonts or bake English-only text into the
  button background. Integration/localization remains with the game presenter.
- Match canvas scaling for panel, buttons and lettering. Native 14 px is deliberate;
  prefer nearest-neighbor scaling for the retro lettering when enlarging it.

The preview is an asset composition on an existing authored OpenFA right panel,
not a game-runtime capture. The left field is deliberately neutral. The sphere,
panel, overall neon and semantic cap assignments are outside this replacement.
The metal socket has restrained surface marks; the shade/ink contain no fake
scratches that would obscure text or change the observed visual hierarchy.

## Reproduction

```powershell
python sources/ui/legacy-menu-labels/build_labels.py
python tools/verify_menu_labels.py
```

Requires Python 3 and Pillow. The generator reads only the bundled open font,
its license and the existing authored preview panel. Generation is deterministic.
The verifier repeats generation in an isolated directory, checks every output
hash, text clipping, 319 glyphs/Polish coverage, anchors, theme invariance,
absence of rails/frames and destination brightness across multiple test colors.
