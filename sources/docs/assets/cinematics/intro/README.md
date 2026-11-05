# Editable intro reconstruction

The complete film now has a [basic editable assembly](remaining-basic/README.md), covering original frames **0–1873**: 24 scene strips, **3748 frames at 24 fps** (156.1667 seconds). [Open the full project](remaining-basic/full-intro-basic.blend). The remaining twenty shots establish geometry, framing and coarse motion; refining is deferred.

Preserved first-sequence checkpoint through original zero-based frame **412**, inclusive: **826 frames at 24 fps**, **34.4167 seconds**, **640×480 letterbox**.

Open [the current Blender project](stages/first-sequence-v8-to-frame-412/first-sequence-to-412.blend). Its MASTER scene contains four independent scene strips and three native CROSS dissolves. Choose a source scene in Blender to edit its 3D objects.

- A: existing ship, eclipse, nebula and galaxy; corrected vertical presentation and damped ship rocking.
- B: separate asteroid-field shot with a distant ship. A/B dissolve: original frames 144–164.
- C: terrain flight, mechanical feet and embossed sole-shaped logo. B/C dissolve: 198–214.
- D: editable, extruded Tetra Corp outline traced from the observed end-card. C/D dissolve: 368–388; frame 412 ends on black.

The asteroid placement, terrain relief and mechanical feet are reference-guided approximations, not recovered original models or a force/torque simulation. Earlier procedural background approximations remain. Native tests do not establish final artistic or game-integration acceptance. No GLB/runtime-game export is claimed.

## Restore on another host

Install Blender 4.5 LTS, Python 3.10+ and ffmpeg/ffprobe. Preserve the stage directories together. Copy into an isolated authoring workspace before running generators:

```sh
python sources/docs/assets/cinematics/intro/restore_workspace.py --output artifacts/intro-authoring
cd artifacts/intro-authoring/stages/first-sequence-v8-to-frame-412
python render_master.py --workers 4
python ../../encode_video.py --frames rendered-frames --output first-sequence.mp4
```

The parallel helper uses Linux/macOS `fcntl`, four independent one-thread Blender processes, disjoint output frames and hash-checked journals. A full new render is independent of the game checkout, original installation and reference-frame caches. No preview PNGs or authoring caches are required.

For other systems, render MASTER directly in Blender or use its animation-render command. With one-based `frame-######` filenames, pass `--start-number 1` to the encoder.

## Original soundtrack and evidence stay local

The repository copy intentionally contains **no original-game audio, GDV, ISO, reference screenshots or reference composites**. Packed authored cloud textures remain inside the native projects. The logo is editable vector geometry, not a screenshot texture. The local, audio-complete project is retained separately.

If you own the original installation, prepare the soundtrack locally:

```sh
python ../../restore_audio.py --legacy-root /path/to/owned-installation --output opening-audio.m4a
python ../../encode_video.py --frames rendered-frames --audio opening-audio.m4a --output first-sequence.mp4
```

Add the resulting soundtrack to MASTER at frame 1 if desired. Original evidence is required only to retrace/reference-check, not to render the preserved models.

## Preserved stages and validation

All eight completed source checkpoints are retained under `stages/`: initial modelling, 24 fps retiming, nebula revision, ship framing fit, continuation to 150, letterbox correction, calmer flight and the multi-scene sequence to 412. Their Python generators and authoring JSON inputs are preserved. Historical finishers/reference comparisons require optional local evidence; `encode_video.py` is the portable delivery encoder.

`SOURCES.sha256` verifies the published source bytes. `publication-runtime.json` records native reopen checks, unchanged mesh/curve/animation fingerprints and representative renders after original audio and local path metadata were removed. The local full MASTER delivery has completed all 826 frames, with PNG decode, stream and final-black checks recorded in `delivery-verification.json`. Public source checks and artistic/game acceptance remain separate.

[Work tracking: issue #209](https://github.com/ender-dev-pl/openfa-assets/issues/209). [Authored preview](../../../../../gallery/media/cinematics/intro/new-shots-preview.jpg).

Publication copies preserve unused authoring datablocks, rewrite local paths and omit original sound. Authored EXR fields are losslessly encoded as PIZ; identical float32 RGBA values are recorded in `packed-field-verification.json`.

[Silent authored preview](../../../../../gallery/media/cinematics/intro/intro-v8-preview.mp4). Recovery-workspace copying and the portable silent encoder were exercised successfully. Optional procedural re-authoring uses NumPy, SciPy and Pillow; fresh rendering uses Blender and standard-library Python.
