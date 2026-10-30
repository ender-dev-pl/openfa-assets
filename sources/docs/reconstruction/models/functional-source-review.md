# Original functional text for model reconstruction

Tracked in [#981](https://github.com/ender-dev-pl/ed-openfa-game/issues/981), relates to #946/#947, category workstreams #948..#951 and source studies #970/#980.

`functional-text-index.json` links every catalogue definition to the actual original English name record and any narrative records established by this milestone. It preserves byte offsets, lengths and payload hashes. Full original paragraphs stay in the ignored local reading aid `artifacts/issue-981-functional-text/functional-reading-aid.md`; they are not embedded in models or copied wholesale into the committed index.

## Scope and evidence

All 303 source names match catalogue identities using the original global index: 177 buildings, 41 ships, 69 missiles and 16 shared equipment definitions. Building names use ENGLISH.TXT record 604+globalType, consistent with the existing Ghidra exporter and named building-name table. Ship/missile/equipment blocks are checked against every corresponding catalogue name, not guessed from a substring search.

| Established source block | First record | Count | Coverage |
| --- | --- | --- | --- |
| Building names | 604 | 177 | All cultures |
| Terran building short descriptions | 821 | 40 | Terran only |
| Building long descriptions | 861 | 177 | All cultures |
| Missile names | 1038 | 69 | All cultures |
| Terran missile short descriptions | 1133 | 13 | Last two are placeholders |
| Ship names | 1146 | 41 | All cultures |
| Spy Satellite narrative | 1197 | 1 | Identified specific record |
| Equipment names | 1198 | 16 | Shared catalogue |

The long-description block is positionally aligned with the complete building order, with explicit beginning/end and cross-culture anchors. This source correspondence is verified; every original runtime long-description lookup is not traced here. No new decompiler labels or legacy code semantics were introduced.

The index does not establish narrative mappings for 112 definitions: 40 ships, 56 non-Terran missiles and 16 equipment definitions. This is unresolved coverage in these mapped blocks, not proof that descriptions do not exist. Other banks such as ENGLISH.CDB remain unreviewed here. The Bug Hunter/Meat-Eater short entries only repeat their names and are explicitly classified as placeholders.

## Read functions before interpreting geometry

Located records are not automatically reviewed functions or accepted geometry. Six critical source functions are explicitly reviewed; every record still has geometry_review=false. Runtime capabilities, role classes and effect IDs are separately labelled supporting catalogue evidence and do not substitute for narrative text.

Ground Deck is explicitly the Rigellian Landing Pad. The Terran Landing Pad description explains access to vast underground hangars, and the Ship Yard description confirms their pressurised underground construction. This supports a deep access shaft, not a shallow grille/platform.

RI11 Probe Launch is a facility for building and launching research/espionage satellites. RI12 Deep Space Probes, despite its name, is described as a sensor installation. RI09 Construction Unit builds spacecraft. These statements constrain what subsequent geometry must represent; they do not determine hidden dimensions or unobserved mechanisms.

Every generated inventory record now links its function reference, description record numbers and review status. Inventory verification recomputes the functional index from the installed source and rejects stale names, offsets, source hashes or catalogue associations. No artistic acceptance gate changes as a result.

## Reproduce

Run with the existing legacy Python runtime:

```powershell
& ../legacy/system/python/python.exe tools/blender/index_legacy_functional_text.py
& ../legacy/system/python/python.exe tools/blender/index_legacy_functional_text.py --check --show openfa:building/legacy/050
& ../legacy/system/python/python.exe tools/blender/test_legacy_functional_text.py
& ../legacy/system/python/python.exe tools/blender/inventory_reconstruction.py
& ../legacy/system/python/python.exe tools/blender/verify_reconstruction_inventory.py
```

This milestone is analytical. It changes source provenance and review workflow, not model geometry, gameplay registration or rendering. Full narrative coverage and per-asset high-detail visual acceptance remain open.
