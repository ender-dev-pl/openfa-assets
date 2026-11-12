# Contributing

Consult [the licensing map and guide](docs/licensing/README.md) before adding files.

- Contributions must be your own work or have documented permission compatible with the component's terms. Preserve third-party notices; do not claim ownership merely by importing a file.
- Asset-specific recipes, parameter sets, material recipes, templates and mixed recipe/helper modules use the OpenFA Asset License 1.0 together with the corresponding assets. Supply the preferred editable sources for shared modifications. Regeneration does not remove the asset terms from reproduced protected content.
- General-purpose tooling may use MIT only after review and explicit placement in the licensing map or the reusable package. Keep concrete model coordinates, shapes, scene presets and asset templates out of MIT modules. A new `tools/` script is conservatively treated as asset-specific until reviewed.
- Keep canonical source paths and source-bound evidence intact. Extract a general utility with compatibility imports and focused tests; do not move or relicense a complete mixed generator as if it were only a library.
- Imported fixtures with unresolved rights must remain explicitly excluded from new grants. Preserve the Noto font's existing OFL notice. Original game media must not be committed.
- Run `python tools/verify_licensing.py` and `python tools/test_licensing.py`, together with the project checks appropriate to your change.

Submitting a contribution for inclusion means offering your own contribution under the applicable declared component terms. It does not transfer copyright to EnderDEV or authorize you to relicense other contributors' work. EnderDEV administers reserved printing permissions only to the extent it has the necessary authority.
