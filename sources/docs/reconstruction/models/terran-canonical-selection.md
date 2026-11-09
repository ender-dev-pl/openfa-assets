# Canonical Terran SciTek models

The user confirmed on 2026-11-09 that the latest Terran iteration from the SciTek work is canonical. This supersedes the earlier temporary deferral after the detail-quality concern. It is a source-selection decision, not a request to remaster these ships again.

| Runtime object | Canonical Blend/GLB directory | Physical meshes | SciTek |
| --- | --- | ---: | --- |
| `openfa:terminator` | `sources/objects/terran/terminator/refined/` | 71 | Research30 |
| `openfa:fleet-battleship` | `sources/objects/terran/fleet-battleship/refined/` | 45 | Research09 |
| `openfa:command-cruiser` | `sources/objects/terran/command-cruiser/refined/` | 82 | Research35 |

Each directory contains `model.blend` and `model.glb`. The inventory selects one current payload per ship and preserves earlier studies as historical, outside current packaging selection. Reuse the canonical model in gameplay, build/ship menus and SciTek. Dedicated technical diagrams and timelines retain their presentation role. Other Terran mobile records keep their existing sources, including the three canonical ships with layered construction. Completed spacedocks remain outside this programme.

Gameplay uses frame1 without the presentation turntable animation. The documented roots are identity at that pose. Client size, orientation, mounts and animation handling require integration validation; user source selection does not prove those checks.

## Read-only runtime verification

`verify_terran_canonical_selection.py` reopens each saved native source with scripts disabled and independently imports the existing GLB. It checks mesh identities/counts, materials, embedded images, identity of the gameplay root, and matching world matrices/evaluated bounds at frames1/31/61. Actual source/export hashes are checked before and after; no binary is rewritten. The JSON binds the verifier, binaries and measured results.

Run Blender with `sources/tools/blender/verify_terran_canonical_selection.py -- <report-path>`. Three sampled poses are a smoke check, not exhaustive topology, UV, animation or legacy-fidelity verification. Subject-specific SciTek wire/animation and source-retention evidence remains separate.

No retrospective ImageGen concept is fabricated. Source-specific concept and legacy/imported-render feedback gaps remain recorded under programme #248; the user's canonical decision is not a waiver of unrelated protocol requirements. Historical audit snapshots retain their original findings. Legacy pixels remain private. Gallery selection follows the inventory without creating additional model copies.
