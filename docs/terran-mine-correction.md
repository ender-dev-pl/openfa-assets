# Terran Mine / Deep Bore Mine correction

Asset issue [#271](https://github.com/ender-dev-pl/openfa-assets/issues/271), game integration [ed-openfa-game#1271](https://github.com/ender-dev-pl/ed-openfa-game/issues/1271).

PB08 keeps its existing deck, dome, hatch, trestles and ladder. A low safety fence, two worn coolant/power cabinets and connected conduits extend its horizontal bounds symmetrically by 4/3. Normal bounding-box fitting into the unchanged 2×2 construction footprint therefore displays its retained drilling structure at 75% of PB13's size. The original vertical bounds, horizontal centre and ground anchor are preserved. PB13's overall bounds remain unchanged.

Both mines have a continuous bore pipe connected to a deck chuck and downward cutting crown, with coupling shoulders, worn teeth and joint grime. PB08 previously lacked a central shaft. PB13's previous shaft/coupler proxies were replaced. These are static assets; no pre-existing animation clips were removed and no gameplay mechanics were added.

Legacy surface body frame 1 measures 27×33 pixels for PB08 and 34×42 for PB13. The requested 4/3 envelope is an approximation selected by the user, rather than a claim of exact pixel reconstruction. Legacy reference pixels remain outside this repository.

The primary editable/export pairs remain under `sources/docs/assets/bootstrap-3d/terran-refined/{pb08,pb13}/model.{blend,glb}`. Runtime proof and independent GLB renders are in `gallery/media/docs/assets/bootstrap-3d/terran-mine-correction/`. The paired preview applies the game's bounding-box-fit formula in Blender; it is not an application screenshot. In-game construction, ghosts, picking and shadows must be checked during package integration.

Outgoing source pairs, metadata and previews are preserved in private archive commit `cb59612`, with exact source blobs recorded in `project/terran-mine-correction.json`. Reproduction requires those outgoing inputs, not the already corrected canonical inputs:

```text
blender -b --python sources/tools/blender/correct_terran_mines.py -- --source-root ARCHIVE_ROOT --output artifacts/mine-correction
```

Validate the current canonical delivery without regenerating it:

```text
blender -b --python-exit-code 1 --python sources/tools/blender/verify_terran_mines.py -- --models sources/docs/assets/bootstrap-3d/terran-refined --generation-proofs gallery/media/docs/assets/bootstrap-3d/terran-mine-correction --proof artifacts/mine-verification
```

The verifier opens the actual BLENDs and independent GLB imports, checks unchanged structural meshes, dimensions and drilling parts, and renders both at matching angles. Runtime triangle counts include existing evaluated bevel modifiers: PB08 29,504 and PB13 28,504. The correction does not introduce textures, skinning, morph targets or animation clips.
