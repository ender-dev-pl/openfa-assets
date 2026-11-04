# Sci-Tek main-screen logo — #208

Separate from the oval HUD badge. Authored from actual `_MS/SCITEK.256` frame 0 with the runtime `_MS/BUTTONS.256` palette: stepped black inlays, blue-grey machined plaque, SCI/TEK lettering and the silver device emblem crossed by a red probe. The reference pixels are private evidence and are not used as model textures.

`logo-native.png` is a transparent 320×160 logical sprite; `logo-4x.png` is 1280×640. Drawn plaque registration remains at (0,0), 234×115 native pixels. Keep the transparent remainder and original placement; do not stretch the drawn rectangle over the canvas. Replace the Sci-Tek main-screen `scitek-logo` binding, not the HUD Sci-Tek button.

Editable `scitek-screen-logo.blend` includes packed font and subtle procedural wear. `scitek-screen-logo.glb` uses explicit PBR colors. The typeface is an authored approximation. Native Blend render/reopen is pixel-identical; independent GLB import silhouette IoU exceeds 0.999. Proof files are in `gallery/media/ui/scitek/screen-logo/`. Game integration must still be checked in the client.

Rebuild in Blender 4.5: `blender -b -t 4 --python-exit-code 1 --python build_logo.py -- OUTPUT_DIRECTORY`. Sources require the adjacent `geometry.py`; render outputs belong outside sources.
