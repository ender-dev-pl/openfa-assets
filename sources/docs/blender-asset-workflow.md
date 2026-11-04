# Original OpenFA Blender workflow

Tracked in [#940](https://github.com/ender-dev-pl/ed-openfa-game/issues/940).
This creates independent artwork, with no legacy models, textures or game pixels
as inputs. These are editable starter models for the alternative visual style;
they do not replace the bootstrap's currently packaged sprites automatically.

## Portable installation

```powershell
./tools/Install-OpenFaBlender.ps1
```

The default is official Blender 4.5.15 LTS, Windows x64, installed under
`[local]/blender-4.5.15-windows-x64`. The installer verifies the ZIP
against the release's official SHA-256 list and records source/version/hash in
`openfa-installation.json` beside the executable. Downloads are cached under
the ignored `artifacts/blender-downloads/`. Existing complete installations are
reused, while incomplete directories and checksum mismatches stop installation.

Launch through `[local]/openfa-blender.ps1`. This uses the installation's
`4.5/config/` for preferences and startup, without changing global PATH or other
Blender profiles. It forwards Blender arguments and offers explicit script
arguments to preserve the `--` separator through PowerShell.

## Generate, configure and verify

Run from the repository root:

```powershell
& [local]/openfa-blender.ps1 -Background `
  -PythonScript tools/blender/build_openfa_assets.py `
  -ScriptArguments @('--configure')

& [local]/openfa-blender.ps1 -Background `
  -PythonScript tools/blender/verify_openfa_assets.py
```

`--configure` explicitly saves the sprite rig as the portable startup scene and
adds **OpenFA original models** to the Asset Browser library. Omit it to regenerate
only the project files. The generator writes known output filenames in
`docs/assets/bootstrap-3d/`; keep manual model edits in sibling files before
regenerating. The installer is x64-specific; another platform requires its own
official archive/checksum selection.

The shared rig uses a 30-degree elevated orthographic camera, a 6.4-unit frame,
three soft area lights, Cycles CPU with 32 samples and denoising, AgX colour
management, and transparent RGBA PNG output at 512x512. No GPU setup or plugins
are required. This is an authored alternative view, not a claim of exact legacy
camera reconstruction. `--resolution` and `--samples` can override render quality.

## Deliverables

`docs/assets/bootstrap-3d/` contains the empty `openfa-sprite-template.blend` and:

| Asset | Editable source | Interchange | Preview |
| --- | --- | --- | --- |
| CPU command hub | `models/cpu.blend` | `exports/cpu.glb` | `renders/cpu.png` |
| Tracking solar array | `models/solar.blend` | `exports/solar.glb` | `renders/solar.png` |
| Cargo transporter | `models/transporter.blend` | `exports/transporter.glb` | `renders/transporter.png` |

Each source keeps named mesh parts, bevels, native materials, camera and lights;
the model collection is marked as a reusable Blender asset. GLB files contain
geometry/materials only. The manifest records Blender version, render parameters,
mesh counts and relative deliverable paths. The verifier starts a fresh Blender
process, checks saved startup/preferences, reopens all blends, and imports every
GLB to catch broken sources, missing geometry or external texture dependencies.

Runtime graphics must be deliberately cropped/scaled, palette-mapped and
registered before replacing packaged sprites. Animations, directional frames,
construction stages and exact model footprints remain future art work.

The reference-based successor studies are documented in
[`transporter-inspired/README.md`](assets/bootstrap-3d/transporter-inspired/README.md)
and [`buildings-inspired/README.md`](assets/bootstrap-3d/buildings-inspired/README.md).
They retain independent generators, reference evidence and editable model variants.

The [complete building catalogue](assets/bootstrap-3d/full-catalogue/README.md)
extends this workflow to all 177 definitions across seven cultures, with a
filterable local gallery, editable sources and three review views per entry.

The [refined Terran variants](assets/bootstrap-3d/terran-refined/README.md)
preserve that catalogue as a comparison baseline while adding building-specific
manufactured geometry and equipment to PB00–PB39. Their separate gallery shows
before/after pairs, and directional variants retain their independent head rigs.
