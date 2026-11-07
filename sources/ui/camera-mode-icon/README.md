# Camera orbit and pitch mode HUD icon

Asset issue [#230](https://github.com/ender-dev-pl/openfa-assets/issues/230).
An authored OpenFA3D extension for the Android bottom-right quick-menu control.
It toggles camera interaction mode: horizontal orbit/yaw and vertical pitch.
The silver camera, blue horizontal orbit and gold vertical pitch axis distinguish
this control from the existing wire-globe/return camera-reset icon. Keep reset as
a separate action and asset.

## Canonical delivery

- `camera-mode-icon.blend`: editable geometry, procedural surface wear, original HUD lighting.
- `camera-mode-icon.glb`: matching rigid geometry, explicit portable silver/blue/gold PBR colours.
- `catalog.json`: dimensions, state paths, hashes, semantics and Blender runtime evidence.
- `../../../gallery/media/ui/camera-mode-icon/icons/native/camera-mode-icon.png`:
  normal 48x40 RGBA PNG, transparent background, no button frame or text.
- `../../../gallery/media/ui/camera-mode-icon/icons/hires/camera-mode-icon.png`:
  normal 384x320 RGBA PNG for high-density rendering.

The five states are `normal`, `hover`, `selected`, `pressed` and `disabled`.
Normal omits the suffix; other filenames end in `-<state>.png`. All have identical
canvas size and registration. Pressed artwork is offset by one native pixel;
state colour/brightness follows the existing HUD packaging recipe.
The labelled `preview.png` is a review board, not an in-game texture.

Suggested game asset id: `openfa:asset/gameplay/camera-mode-icon`. Copy the normal
PNG into the game's image package and bind it to the 48x40 camera-mode control at
the bottom of the right quick menu. Reuse existing button chrome behind this
standalone glyph. Do not bake the review board or a button background into it.
Use the selected variant for active mode and disabled when the action is unavailable.
Renderer and real Android screenshot acceptance remain game integration work.

## Evidence and reproduction

The actual correctly paletted legacy `ICONS.256` frames 006, 019 and 059 were
inspected for raised-sign, orbit-arrow and palette language. The current authored
111-record HUD set supplies shared geometry, materials, lighting and interaction
processing. This camera motif is new; it is not claimed to be a recovered legacy
camera command. Original pixels are local reference only and are not published or
used as textures/contours.

```text
blender --background --python-exit-code 1 --python sources/ui/camera-mode-icon/build_camera_mode_icon.py
python sources/ui/camera-mode-icon/assemble_camera_mode_icon.py
python sources/ui/camera-mode-icon/verify_camera_mode_icon.py
```

Blender uses only its bundled Python; packaging uses the normal Pillow dependency.
Cycles renders the native scene, independent GLB import and reopened saved Blend.
Both alpha silhouette IoUs are 1.0. GLB has constant PBR colours; procedural fine
wear remains in Blend and PNGs. Checks cover source and payload hashes, all ten
RGBA outputs, clear borders, native blue/gold legibility and rejection of opaque,
wrong-size and missing-axis-colour negative controls.
