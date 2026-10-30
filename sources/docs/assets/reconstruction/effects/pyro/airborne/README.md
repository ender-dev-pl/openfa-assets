# Spatial airborne explosion

Authored for [#1035](https://github.com/ender-dev-pl/ed-openfa-game/issues/1035)
using the [XS01 reference study](../reference/xs01/README.md).

[Animation](explosion.mp4) · Legacy comparison (local evidence only; not distributed) ·
[Phase contact sheet](contact.png) · [Editable Blender source](explosion.blend)

The effect starts with a white/cyan incandescent flash, separates into warm
porous lobes and outward sparks, and leaves a thin, irregular expanding shell
before disappearing. Expansion is spatial and radial, without a prescribed
upward smoke column or falling particle trajectories.

The source contains nine procedural gas volumes, forty incandescent particles
and a genuinely spherical transparent shell with procedural displacement and
fragmentation. The shell is an authored interpretation of the thin perimeter
visible in XS01, rather than a physically verified shock-wave simulation.
All geometry and shaders remain editable; no external texture or simulation
cache is required.

## Playback and reuse

- **300×300 RGBA**, 40 frames at **30 fps** (approximately 1.33 seconds).
- `frames/001.png` and `frames/040.png` are fully transparent. MP4 has an opaque
  review background; PNGs preserve fractional alpha. The GIF shows alpha over
  a checkerboard and adds a short pause between loops.
- Append **Pyro | append this collection** from `explosion.blend`. Review
  cameras and lights are outside that collection.
- Transform **AirburstRoot** to position, rotate or scale the whole effect.
  Its **density**, **fire_intensity** and **shell_opacity** properties drive
  the corresponding shaders. For scripted property changes, call
  `root.update_tag(refresh={'OBJECT'})` and update the view layer.
- To retime, change both object and material-node keyframes. The original XS01
  has 26 phases at 20 fps; this model has independently authored continuous
  animation at 30 fps with a similar duration.
- EEVEE in Blender 4.5.15 LTS is the verified rendering target. Procedural
  volumes and the transparent shell are not preserved by ordinary GLB export.

## Regenerate and verify

```powershell
& C:/tools/blender/blender-4.5.15-windows-x64/blender.exe `
  --background --factory-startup --python-exit-code 1 `
  --python tools/blender/build_airburst.py

& C:/tools/blender/blender-4.5.15-windows-x64/blender.exe `
  --background --factory-startup --python-exit-code 1 `
  --python tools/blender/verify_airburst.py

python tools/blender/package_airburst.py --ffmpeg '<ffmpeg executable>'
```

`--preview` renders six phases only. `--seed <integer> --output <new directory>`
creates an additional seeded layout without overwriting the delivered variant.
Default regeneration overwrites known output filenames; save manual edits
separately. Root seed metadata alone does not regenerate a layout.

`blender-verification.json` records fresh reopening, root-control checks and an
alternate-angle runtime render. `render-verification.json` records frame size,
fractional alpha, blank endpoints, unclipped edges, dissipation and output hashes.
