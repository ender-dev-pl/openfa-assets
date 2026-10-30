# XS01 airborne / ship-explosion reference

Follow-up evidence for [#1035](https://github.com/ender-dev-pl/ed-openfa-game/issues/1035).
The installed files are named **XS00–XS02**, rather than SX.

Inspect the [animated preview](legacy-preview.gif) or
[all 26 phases](legacy-contact.png). Original unscaled canvas PNGs and
`reference.json` retain registration, palette provenance and coverage data.

## Confirmed observations

- `_P/XS01.256` contains 26 frames on 320×200 canvases with its own embedded
  palette. Its original file SHA-256 is
  `686491be8eba9ed2d38568c310194ac08836725ea524baa3a5022bec91f958a0`.
- The recovered ship-explosion resource descriptor uses 26 frames, 50 ms per
  frame, a nominal 40×40 reference size and 13 retained-hull frames. See
  [fleet combat evidence](../../../../../../legacy/fleet-combat-phases.md)
  and `LegacyShipExplosionProjection`. The preview plays the 26 phases over
  1.3 seconds and adds a 350 ms blank interval between loops.
- Frames 0–8 show a bright, predominantly white/yellow expanding flash with
  irregular edges and small outward points.
- Frames 9–13 show pale cyan/blue regions within the bright mass, with warm
  edges and sideways extensions. These are observed palette colours; they do
  not independently establish a physical temperature or material.
- Frames 14–17 break into separate bright lobes and holes. A thin ring-like
  outline becomes visible around the fragments.
- Frames 18–24 retain increasingly sparse internal fragments and an expanding,
  darkening perimeter; frame 25 has only small residual fragments.
- The extracted indexed sprite uses alpha 0 or 255. Its apparent disappearance
  comes from changing coverage and colours, rather than a smooth fractional
  alpha channel. Fractional volumetric opacity remains an authored 3D feature.
- No substantial upward smoke column is visible in this sequence.

## Implications for a future spatial variant

The current compact/rising/asymmetric models were authored using XB references
and an explicit smoke requirement. XS01 suggests a separate airborne treatment:
an initially intense flash, more nearly radial expansion, short-lived hot lobes,
outward sparks and a thin dissipating spherical shell. Interpreting the observed
outline as a shock shell is an authoring choice, not a confirmed physical model
from the sprite alone. A heavy buoyant plume should not dominate that variant.

This follow-up adds reference evidence and analysis; it does not modify or
rerender the existing Blender variants.

## Reproduce

```powershell
python tools/blender/extract_explosion_reference.py '<licensed installation>' `
  docs/assets/reconstruction/effects/pyro/reference/xs01 --name XS01 --frame-ms 50
```

Extraction uses the existing RLE decoder, requires the embedded palette, keeps
every frame and dynamically sizes the contact sheet so sequences longer than
20 phases are not truncated.
