# Cultural architecture as reconstruction evidence

The original `_TEXT/ENGLISH.CDB` contains explicit `Architecture` articles for six alien cultures. The NUL-delimited record index, exact byte offset, payload length and SHA-256 are recorded in `cultural-architecture-index.json`; `tools/blender/index_cultural_architecture.py --check` revalidates both the source bytes and culture/section headings. No Terran Architecture article was located in this CDB. This index paraphrases the evidence rather than distributing original articles.

| Culture | Direct architectural evidence | Record / offset |
| --- | --- | --- |
| Rigellian | Ergonomic, elegant and comfortable even in mining facilities; less ostentatious than Artemian luxury. Research is integrated into everyday colony life. | 18 / `0x971` |
| Braccatian | Large, lavish, richly decorated buildings express display. Clan gatherings and sporting spaces matter on mining colonies too. | 47 / `0x2142` |
| Mikotaj | Mining structures are heavy, metallic and reminiscent of the ores being extracted. Light, resonant crystal structures describe home worlds. Designs can appear unrelated to their actual function; names express emotional associations. | 76 / `0x39fa` |
| Artemian | Metal and advanced alloys, including decorative alloys; secure exteriors, open interiors, planes, edges and shell forms. Water/hygiene facilities have exceptional importance. | 105 / `0x5734` |
| Mauna | Angular concrete blocks, no decorative or comfort-driven features; immediate practical utility dominates. | 137 / `0x7bea` |
| Achaean | Curves, onion domes and occasional slender towers outside; low barrel vaults, crowded decoration and textile furnishings inside. Comfort is important. | 166 / `0x9d65` |

These are direct statements about architecture. Their use for spacecraft, missiles or equipment is contextual authoring, not proof of geometry or mechanisms. They do not override a specific object's correctly paletted sprite, functional description, established layering or animation evidence. Rigellian elegance does not mandate curves or a particular metal; Mauna architectural angularity does not authorize replacing an actually curved ship component with a box. Mikotaj colony structures must not become generic transparent crystal towers merely because their home worlds use crystal architecture.

For each new model, read the relevant article summary and individual functional description, inspect available original frames, then record which decisions are observed, text-supported or independently interpreted. Use the cultural context to choose ambiguous hidden details and construction treatment. Keep authored wear compatible with the user's request for used equipment; elegance is not a requirement for pristine surfaces.

`programme.json.cultural_style_index` makes this guidance persistent. New Messier-Lukannon metadata binds the index hash and Rigellian article reference; the latter is contextual for a ship. Existing models, their hashes and review gates are preserved. This new source does not authorize retroactive changes or an artistic refining pass. Current work remains first iterations only; scaffolding remains deferred.
