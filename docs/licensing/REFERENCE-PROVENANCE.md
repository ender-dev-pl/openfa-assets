# OpenFA resources and recovered legacy data

The project maintainer confirmed on 2026-11-06 that the three quick-menu PNGs in `sources/ui/quick-menu/` are their own work from OpenFA Classic, and that `sources/tools/extract_fragile_le.py`, `sources/tools/fragile256.py` and `sources/tools/fragile_vid.py` are their own scripts. The PNGs use the OpenFA Asset License; these three general decoder/extractor scripts use MIT. Their original bytes and the historical import records in `migration/files.json` are preserved.

The following JSON files contain OpenFA compatibility structures, descriptions, bindings and recovered legacy parameters:

- `sources/content/standard/catalogues/legacy-buildings.json`
- `sources/content/standard/catalogues/legacy-gameplay.json`
- `sources/content/standard/presentation/legacy-domain.json`

The asset license applies to OpenFA-authored contributions in these files. It does not assert exclusive ownership of recovered facts, numerical values, file formats or underlying Fragile Allegiance content. References to legacy installation files and video entries identify external resources; they are not embedded copies of those media.

In `legacy-gameplay.json`, **`rawDefinitionHex` contains the raw payloads defining the corresponding assets in legacy, recovered through reverse engineering**. There are 41 ship records of 20 bytes and 69 missile records of 16 bytes: 110 records, 1924 decoded bytes in total. Hex encoding is only their storage representation. These payloads are recovered legacy data, not newly authored OpenFA artwork or source code. Their inclusion does not grant new rights in the underlying legacy content or claim OpenFA authorship of those bytes.

Their purpose is reconstruction and compatibility, rather than mesh generation. The OpenFA game client retains these bytes in its legacy ship and missile catalogues. Its ship validator compares recovered record fields with semantic parameters such as range, armour, speed and production costs; missile validation currently checks the raw record's hexadecimal form and length. Keeping the complete records also preserves fields whose semantics have not yet been established. The current compatibility implementation requires the records; removing them would require coordinated game-code changes.

The previous whole-file `NOASSERTION` classification was provisional pending provenance clarification. The current map reflects the maintainer's ownership confirmation while retaining the field-level distinction above. This records provenance and the scope of OpenFA's grant; it is not a blanket clearance of third-party rights.

## Pochodzenie danych

Autor projektu potwierdził, że trzy grafiki quick-menu pochodzą z jego OpenFA Classic, a wskazane trzy skrypty dekodujące są jego autorstwa. Grafiki podlegają licencji assetów OpenFA, a te skrypty — MIT.

Pliki JSON zawierają opracowane w OpenFA struktury zgodności, opisy i powiązania oraz parametry odtworzone z legacy. **`rawDefinitionHex` to surowe payloady definiujące odpowiadające im assety w legacy, uzyskane drogą reverse engineeringu**: 41 rekordów statków i 69 rekordów rakiet, łącznie 1924 bajty. Zapis szesnastkowy nie zmienia ich pochodzenia. Nie przypisujemy OpenFA autorstwa tych bajtów ani wyłącznych praw do odzyskanych faktów, wartości i formatów. Licencja obejmuje własny wkład OpenFA; nie nadaje nowych praw do treści Fragile Allegiance.
