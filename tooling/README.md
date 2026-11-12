# General-purpose tooling — MIT

The reusable Python package is in `openfa_tools/`:

- `publication.py`: byte-preserving native path and bitmap metadata cleanup, hashing and compression helpers. It contains no model coordinates, material presets, asset templates or scene recipes.
- `licensing.py`: ordered, explicit path-scope resolution and coverage checks.

These modules are under [MIT](../LICENSES/MIT.txt). Existing callers can continue to import `tools/publication_support.py`, which forwards to this package. The previous implementation is preserved in `publication.py`, with only a license identifier added and line endings normalized.

The audited additional MIT tools are enumerated individually by `reviewed-tools` in [the licensing map](../project/licensing.json). This includes workspace preparation, catalogue rendering, publication checks and their general regression tests. A new file in `tools/` is not automatically MIT. Existing mixed recipe/helper modules remain asset-specific source as a whole.

Using an MIT utility does not give an MIT license to an input asset, a loaded recipe or an output reproducing protected asset content. Importing a separately licensed recipe does not change either component's license. Read [the license scope guide](../docs/licensing/README.md) before copying a complete tool plus its dependencies.

To use the reusable package directly, add the repository's `tooling/` directory to the Python import path and import `openfa_tools.publication` or `openfa_tools.licensing`. These modules have no Blender scene side effects. Their optional runtime dependencies remain subject to their own licenses.
