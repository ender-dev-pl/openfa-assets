# Native menu button adapters

These generators live beside `../interactive-menu-sphere/`. They were moved from
the game repository (`cba456320`, `23646020b`; game issue #1180, assets issue #204).
They generate package-ready 2D controls; they do not rebuild or alter the sphere.

Run from the asset repository, with Python 3 and Pillow for the label generator:

```powershell
python sources/ui/menu-button-adapters/generate_native_menu_caps.py
python sources/ui/menu-button-adapters/expand_native_menu_labels.py
```

Default output is `gallery/media/ui/menu-button-adapters/native/`; `--output`
can select an isolated verification directory. The label generator accepts
`--source` and defaults to the unchanged refined menu delivery at
`gallery/media/ui/legacy-main-menu-refined/native/` (78cf3723). Always use original
rows as input, never the expanded outputs.

Caps preserve the seven semantic original-menu colors without copying reference
pixels. The label adapter enlarges only the rectangular well; the circular socket
and 211x48 row size remain unchanged. All four themes and five interaction states
are generated. Finished PNGs are explicitly integrated into the game's
`content/openfa3d/images/menu/`; the game does not require this source repository
at build time or runtime to use these controls.
