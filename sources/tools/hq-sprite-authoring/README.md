# HQ 2x directional sprite authoring

`render_directional_sprite.py` converts a project-generated, vertex-coloured
directional model into an RGBA8 sprite sequence for issue #161 authoring review.
It is an offline content tool, not a runtime asset lookup path.

The generated sequence preserves the legacy logical canvas and frame count. Its
physical canvas and reference bounds are exactly twice as large. Model colours
are interpolated in linear light, encoded as sRGB, and stored with straight
per-pixel alpha. The output manifest declares the density, pixel contract,
sampling intent, logical geometry, directional mapping, source hashes, and every
generated artifact hash.

The source frame manifest is used only for canvas and opaque-bound geometry.
Original frames are not copied into the output. Generated samples belong under
the ignored `.asset-lab` directory until their legal and artistic review is
complete.

## Environment

The current proof-of-concept renderer uses an NVIDIA CUDA device and the same
isolated Python environment as the model-reconstruction experiment. It requires
Python 3.10+, Pillow, NumPy, trimesh, PyTorch, nvdiffrast, and utils3d.

## Example

```powershell
& '.asset-lab/venv/Scripts/python.exe' `
  './tools/hq-sprite-authoring/render_directional_sprite.py' `
  --asset-id 'openfa:presentation/ships/federal-transporter' `
  --display-name 'Federal transporter' `
  --model '.asset-lab/runs/PS05-transporter-12view-seed195/gaussian-colors/model-gaussian-calibrated-colors.glb' `
  --frame-manifest '.asset-lab/vid-directional/PS05/frames-manifest.json' `
  --appearance-manifest '.asset-lab/runs/PS05-transporter-12view-seed195/gaussian-colors/gaussian-color-manifest.json' `
  --output '.asset-lab/exports/issue-161-hq-x2/transporter'
```

The stable resource IDs in this first authoring sample are provisional. They
must be reconciled with the package presentation-resource contract before an
`hq.ofapkg` fixture is created.

## Raster-only alternative

`upscale_raster_sprite.py` creates the same 2x RGBA sequence directly from the
decoded source sprites. It does not load or reconstruct a 3D model. The pipeline
reconstructs colours outside the opaque edge, converts sRGB to linear light,
reduces palette dithering with a conservative bilateral filter, resamples colour
at 2x, reconstructs smooth coverage from a signed-distance contour, applies a
bounded unsharp mask, and writes straight-alpha RGBA8+sRGB PNG files. Colour and
coverage remain separate, so stronger surface sharpening cannot create alpha
halos or reintroduce a stair-stepped silhouette.

For a perceptual-sharpening experiment, pass the official
`RealESRGAN_x2plus.pth` through `--realesrgan-model`. The model processes only
nearest-edge-filled RGB; the deterministic signed-distance alpha remains
authoritative. `--realesrgan-blend` controls how much neural RGB is blended with
the classical linear-light result. Model weights are never committed and their
SHA-256 is recorded in the generated manifest.

The expected official x2 weights are published in the Real-ESRGAN v0.2.1
release and have SHA-256
`49fafd45f8fd7aa8d31ab2a22d14d91b536c34494a5cfe31eb5d89c2fa266abb`.
The minimal inference architecture in `rrdbnet_x2.py` follows XPixelGroup's
Apache-2.0 BasicSR RRDBNet definition. The default 0.55 neural blend was selected
to improve edge continuity and surface sharpness while retaining more source
texture than the fully neural result.

```powershell
& '.asset-lab/venv/Scripts/python.exe' `
  './tools/hq-sprite-authoring/upscale_raster_sprite.py' `
  --asset-id 'openfa:presentation/ships/federal-transporter' `
  --display-name 'Federal transporter' `
  --frame-manifest '.asset-lab/vid-directional/PS05/frames-manifest.json' `
  --output '.asset-lab/exports/issue-161-hq-x2-raster/transporter'
```

The output includes an HQ-only contact sheet and a private source-nearest versus
HQ comparison sheet. Neither the generated sequences nor comparison sheets are
committed while redistribution rights are under review. Unlike the 3D-authored
variant, these images are direct derivatives of the legacy rasters; the manifest
marks that provenance explicitly and must not be interpreted as a redistribution
license.
