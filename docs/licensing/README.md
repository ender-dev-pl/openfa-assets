# Licensing boundaries / Podział licencji

This repository uses different licenses for different components. The executable map is [project/licensing.json](../../project/licensing.json); rules apply in their listed order. The identifiers and notices describe licenses only to the extent the corresponding rights holders can grant them. The map is not proof of ownership, and it does not sanitize private Git history.

| Component | Terms | Scope |
| --- | --- | --- |
| Asset-specific source, recipes, parameters, templates and mixed recipe/helper modules | [OpenFA Asset License 1.0, English](../../LICENSE.md) / [Polski](../../LICENSE.pl.md) | Creative source and its protected asset outputs, including regeneration and format conversion |
| Audited general tools and the reusable `tooling/` package | [MIT](../../LICENSES/MIT.txt) | The named code and tool documentation, without relicensing its asset inputs or outputs |
| Models, textures, animations, renders and asset-specific evidence | OpenFA Asset License 1.0 | Original OpenFA contributions only; unrelated code/works do not inherit it merely through tool execution |
| Generated gallery HTML | Component-specific terms | Presentation code is MIT; covered embedded asset content/data keeps the asset license |
| Noto font and its notice | Existing SIL OFL 1.1 | Original font terms and copyright notice preserved |
| Nine imported reference fixtures with no established redistribution license in this repository | No new license grant | See [THIRD-PARTY.md](THIRD-PARTY.md); neither MIT nor the asset license is silently assigned |

## Finding and checking a file

```text
python tools/verify_licensing.py
python tools/verify_licensing.py --explain sources/tools/blender/build_federal_transporter.py
python tools/verify_licensing.py --explain tooling/openfa_tools/publication.py
python tools/test_licensing.py
```

CI checks every tracked publication file and rejects unclassified paths, stale explicit exceptions and unsafe broad MIT assignment to creative sources/payloads. The source list and exceptions can be inspected with `--report artifacts/licensing-report.json`. This checks declarations, not whether a particular work is legally copyrightable. New asset-specific Python placed inside `tooling/` would still require human review; a path checker cannot infer creative content from arbitrary code.

## Recipe sources stay with the assets

Recipes currently live in `sources/tools/`, beside subjects in `sources/ui/`, within historical `sources/docs/` source trees, and in `archive/repairs/`. Asset-specific orchestration, rendering and registration scripts also remain in `tools/` unless explicitly reviewed for MIT. The executable map assigns those files to the asset license. In particular, `sources/tools/blender/build_federal_transporter.py`, `refine_ps7c_details.py` and `sources/tools/trading-goods/recipes.py` are recipes, not permissively licensed generic libraries.

A mixed module such as `build_federal_transporter.py` contains both a concrete ship recipe and geometry helpers. Its entire file retains the asset license; the presence of a `box()` function does not make the complete ship recipe MIT. Generic algorithms and independently written implementations are not claimed as exclusive creative assets. Further reusable portions can be extracted and reviewed separately later.

Canonical recipe paths and bytes remain unchanged. Relocating these source-bound files would disrupt import paths, model manifests and historical verification hashes. The legal boundary is explicit in this map and the license, with the genuinely reusable metadata module physically extracted to `tooling/`. There are no additional model copies or asset regenerations in this separation.

## Generated results and Editable Source

Regenerating a protected OpenFA asset from its recipe does not remove its license. Exporting the same covered creative content using Blender, an MIT utility or a modified pipeline does not grant an alternative license to that content. Conversely, unrelated output is not automatically covered merely because a tool was run.

When sharing a modified asset, provide its preferred editable source, including the relevant recipe and parameters when these are the actual working source. A rendered image or exported mesh alone does not replace a more editable source used to make the modification. Do not assume changing to GPL, MIT or another software license by itself controls all generated artwork; the asset-specific source and protected output need their own explicit scope.

## Zasady w skrócie

- Modele oraz ich konkretne receptury i dane konstrukcyjne podlegają licencji assetów OpenFA. Dotyczy to również receptur zapisanych w Pythonie oraz plików mieszających recepturę z funkcjami pomocniczymi.
- MIT obejmuje wyłącznie wskazane narzędzia ogólne. Nie przenosi się przez ich uruchomienie na cudze dane wejściowe ani na odtworzone chronione assety.
- Udostępniane przeróbki wymagają oznaczenia pochodzenia OpenFA, tej samej licencji oraz odpowiadających im edytowalnych źródeł.
- Przygotowanie wersji do druku 3D i komercyjne wykorzystanie wydruków wymagają wyraźnej zgody EnderDEV na zasadach opisanych w licencji.
- Zachowane licencje osób trzecich i wyłączone dane referencyjne mają pierwszeństwo przed domyślnym przypisaniem folderu. Nie nadajemy cudzym materiałom nowych praw przez samą zmianę etykiety.
