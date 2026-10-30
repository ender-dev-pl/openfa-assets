# Legacy-inspired basic colony buildings

Tracked in [#942](https://github.com/ender-dev-pl/ed-openfa-game/issues/942).
All geometry and materials are newly authored in Blender. Original images are
visual references only; no legacy textures, meshes or pixel crops are included.
Earlier generic CPU/solar models remain available in `../models/`.

## Selected references

The building IDs and preview profiles are confirmed by
`content/standard/presentation/legacy-domain.json` and
`content/standard/catalogues/legacy-buildings.json`.

| Model | Preview | Selected frames (zero-based) | Visible features retained |
| --- | --- | --- | --- |
| CPU | `PB20.VID` | 0, 16, 38 | Low gold dome, radial side pods, aerials and small service gantry |
| Solar | `PB04.VID` | 0, 5, 11 | Tall tapered mast, gold collar and four broad radial collector petals |
| Air processor | `PB19.VID` | 5, 21, 48 | Unequal joined towers, bronze caps and paired curved blue pipes |
| Hydroponics | `PB37.VID` | 5, 27, 54 | Ribbed glazed hemisphere, front annex and two small side tanks |
| Hydration | `PB38.VID` | 0, 21, 43 | Raised bell-shaped head, gold cap, exposed columns and lower reservoir |

Preview contact sheets sample the 60-frame rotations at twelve orientations.
The existing CPU export and freshly decoded PB04/PB19/PB37/PB38 videos retain
their embedded VGA palettes; decoding uses the original executable's video codec
through the existing offline Unicorn exporter, without launching the game.
Source-video and selected-frame hashes are recorded in `reference-frames.json`.

Also inspected the matching `_B/_B` entries `PB04.256`, `PB19.256`, `PB20.256`,
`PB37.256` and `PB38.256`. Frame 0 is the shadow and frame 1 is the body; these
are not construction stages. The preview videos provide rotating views rather
than a demonstrated functional animation cycle. No operational or construction
animation is claimed for these static studies. AC-prefixed files belong to a
different culture and are not used as Terran building references.

Exact hidden internals, detailed piping, rib layout, support counts and mesh
cross-sections are authoring choices. The models reconstruct recognizable visible
features rather than claiming an exact recovery of the original 3D sources.
Reference-only images and decoding outputs are in `artifacts/issue-942-buildings/`.

## Deliverables and regeneration

Each of `cpu/`, `solar/`, `air/`, `hydroponics/` and `hydration/` contains:

- `model.blend`: editable named components, native materials, orthographic camera,
  lighting and a collection marked as a Blender asset.
- `model.glb`: self-contained geometry/material export.
- `front-quarter.png`, `rear-quarter.png`, `top.png`: transparent 768x768 Cycles CPU
  renders with 48 samples.

`manifest.json` records render settings, references and mesh counts.
`preview.jpg` is a contact sheet of the five front-quarter renders.

```powershell
& C:/tools/blender/openfa-blender.ps1 -Background `
  -PythonScript tools/blender/build_legacy_buildings.py
& C:/tools/blender/openfa-blender.ps1 -Background `
  -PythonScript tools/blender/verify_legacy_buildings.py
```

The generator overwrites this study's known model/render filenames. Save manual
edits under another name before regenerating. It reads no legacy images at runtime.
The verifier reopens all five Blend sources, checks camera, materials, major part
counts and evaluated geometry bounds, then imports each GLB independently.

These are model-source deliverables. The currently packaged bootstrap sprites
are not automatically replaced: footprint calibration, sprite scaling, palette
mapping and runtime review are separate integration work.
