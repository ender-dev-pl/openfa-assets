# Complete building model catalogue

177 independently authored Blender studies cover every building definition in
the installed catalogue: Terran 40, Rigellian 23, Braccatian 23, Mikotaj 21,
Artemian 23, Mauna 21 and Achaean 26. Open `index.html` to filter the catalogue
and switch between front-quarter, rear-quarter and top views.

Each resource directory contains an editable `model.blend`, standalone geometry
and materials in `model.glb`, three transparent 512px renders and `model.json`.
The five detailed basic building studies are reused in their catalogue slots.
Named parts and asset collections preserve building IDs and footprint metadata.

These are original silhouette studies informed by legacy reference frames;
hidden surfaces and details are inferred. They are not exact recovered legacy
models. No original image pixels or meshes are included in the generated files.
See `REFERENCE_EVIDENCE.md` for source mapping and uncertainty.

## Reproduction

From the repository root, use the configured Blender launcher:

```powershell
python tools/blender/author_catalogue_recipes.py
& [local]/openfa-blender.ps1 -Background -PythonScript tools/blender/build_full_catalogue.py -ScriptArguments @('--resume')
& [local]/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_full_catalogue.py
python tools/blender/review_full_catalogue.py
```

The authoring script expands explicit per-building recipes; unknown families
fail rather than silently substituting a generic object. Resume checks recipe,
generator and render-setting hashes. The verifier reopens all Blend files and
independently imports each GLB. The review script checks complete ID coverage,
transparent render bounds and hashes, then rebuilds the gallery and sheets.

These source models are not yet registered as gameplay sprites. Construction
stages, palette mapping and runtime integration require a separate export pass;
the directional model exports below provide source frames for that work.

## Directional assemblies

Weapon heads have an editable `DirectionalHead` empty with a local Z pivot;
`StaticBase` owns the fixed foundation/housing. Protected solar and storage
towers include an authored defensive cap; Ex-Fang has a separate rotor, and
MK21 uses a rotating crystal emitter body. This is source-model capability,
not a change to the runtime's directional-building allowlist.

After generating or rebuilding base models, run:

```powershell
& [local]/openfa-blender.ps1 -Background -PythonScript tools/blender/build_directional_catalogue.py -ScriptArguments @('--resume')
& [local]/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_directional_catalogue.py
python tools/blender/review_directional_catalogue.py
python tools/blender/review_full_catalogue.py
```

The Blend timeline and exported GLB contain `HeadingPreview_360`, a linear
one-turn demonstration on frames 1–17. Frames 1–16 correspond to model-local
angles 0–337.5 degrees in 22.5 degree increments. Direction zero faces -Y and
positive rotation is counterclockwise around +Z. This local convention must be
mapped deliberately to gameplay headings during sprite registration.

`directions/00.png` through `15.png` use a single camera fitted to the union of
all headings: the building anchor and scale stay fixed. `directions.jpg` and
`rotation.gif` provide review previews. They show the full composite building;
separate base/body sprite layers and runtime registration remain future exports.
The rig verifier checks every sampled base pose stays fixed, moving geometry
actually rotates, the loop closes, and GLB hierarchy/animation survives import.
