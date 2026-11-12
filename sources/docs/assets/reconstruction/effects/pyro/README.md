# Reusable 3D explosion effects

Tracked in [#1035](https://github.com/ender-dev-pl/ed-openfa-game/issues/1035).

Three editable Blender effects provide fire, turbulent smoke, incandescent sparks
and gradual dissipation. These are authored spatial effects inspired by the
original explosion family, rather than reconstructions of individual sprite
silhouettes. They do not replace game resources automatically.

| Variant | Seed | Character | Source |
| --- | --- | --- | --- |
| Compact | 17 | Short radial burst, clustered billows | [Blender](compact/explosion.blend) |
| Rising | 53 | Taller plume with a spreading upper cloud | [Blender](rising/explosion.blend) |
| Asymmetric | 91 | Uneven lateral expansion | [Blender](asymmetric/explosion.blend) |

Watch [all variants](variants.mp4), including their alpha composited over a
checkerboard, or inspect the [phase contact sheet](contact.png). Each variant
also has `explosion.mp4` and 96 transparent **300×300** RGBA PNGs in `frames/`.
MP4 previews have an opaque review background; the PNG sequence preserves alpha.
Working previews are excluded from Git. The procedural 3D sources can also
render at larger resolutions without changing their geometry or shaders.

## Use in Blender

Open a source project and play frames **1–96 at 24 fps** (four seconds).
Alternatively, use **File → Append → explosion.blend → Collection →
Pyro | append this collection**. Append this effect collection only; review
cameras and lights are outside it.

Select **ExplosionRoot** to move, rotate and scale the complete effect. Its
custom properties **fire_intensity** and **density** control flame emission and
volume density through native drivers. Changing `seed` in the root is metadata;
regenerate with the command-line `--seed` option to create a new random layout.

Transforms, volume evolution, density and emission use native keyframes and
shader nodes. No Python auto-run, external textures, VDB files or simulation
cache are needed. The shader uses actual volumetric absorption, scattering and
emission in EEVEE. Cycles can also evaluate the volume nodes, but the delivered
renders and transparency verification use EEVEE in Blender 4.5.15 LTS.

To retime an effect, scale/offset **both object and material node-tree keyframes**;
changing only the root's transform keys does not retime the fire or dissipation.
For repeated independent events, use independent object/material copies with
their own keyframe timing. Seed variants can be regenerated with the authoring
script. GLB export does not preserve Blender's procedural volumetric shaders;
the RGBA sequence is the portable presentation output.

## Regenerate

Run from the repository root with the installed Blender executable:

```powershell
& [local]/blender.exe `
  --background --factory-startup --python-exit-code 1 `
  --python tools/blender/build_pyro_explosions.py -- --variant compact --seed 17
```

Use `rising` or `asymmetric` for the other layouts. To create additional seeds,
pass `--seed <integer> --output <new-directory>`. `--preview` renders six review
phases; `--generate-only` writes the editable project without
rendering. These commands regenerate the selected variant's known filenames;
save manual edits separately before rerunning them.

Run `tools/blender/verify_pyro_explosions.py` in a fresh Blender process, then
`tools/blender/package_pyro_explosions.py --ffmpeg <ffmpeg executable>` with Python,
Pillow and NumPy to verify PNG coverage and create review videos.

## Legacy evidence and interpretation

Local-only `reference/xb00`, `reference/xb01` and `reference/xb02` can contain the original
16-, 20- and 19-phase sequences decoded by `tools/fragile256.py`. Their manifests
record original file hashes and embedded palette hashes. Reference extraction
requires an existing licensed installation and fails if the expected embedded
palette is unavailable; it does not silently substitute a palette.

Observed in those frames: white/yellow hot areas, orange/red edges, expansion,
fragmentation and disappearance; the three resources have different shapes.
The original resource table and its use are documented in
[missile mechanics](../../../../legacy/missile-mechanics.md).

Authored here: hidden depth, motion in all three axes, four-second duration,
continuous noise evolution, soot, sparks and the three seeded layouts. The
effect uses animated procedural volumes, not a fluid simulation. Smoke was
explicitly requested as part of this new effect; it is not a claim about an
unobserved original smoke pass. No colony or runtime game-state imagery is used.

`side-review.png` in each variant shows the volume from a second camera angle.
`blender-verification.json` records reopening, control checks and fresh renders;
`rgba-verification.json` records fractional alpha, blank endpoints and coverage
across all frames. `manifest.json` identifies the delivered sources and videos.
The discarded silhouette study remains in
`artifacts/issue-1035/initial-silhouette-study/` for diagnostics.

The subsequent [XS01 airborne explosion study](reference/xs01/README.md) records
a different visual family: bright flash, fragmenting hot lobes and a thin
expanding perimeter, with no substantial rising smoke column. It supplies
additional evidence for an airborne variant without changing these XB-inspired
models. The separate [airborne 3D effect](airborne/README.md) implements that
family with a white/cyan flash, radial fragments and a dissolving spatial shell
at 300×300, 30 fps and approximately 1.33 seconds.

Original reference PNGs, GIFs and mixed legacy/authored comparison videos are not distributed. Extract references locally before running comparison packaging tools.
