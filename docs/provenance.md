# Provenance and ownership

`migration/files.json` is the retained import record: original repository/commit, original path, then-current destination, role, ownership, length and SHA-256. It is no longer the active workspace configuration. `project/layout.json` records current locations, roles and explicit retirements; changing a current file does not rewrite the historical import hash.

All 396 Blend files and 405 GLB files are preserved byte-for-byte by this reorganization. The 698 authored material PNGs, original 2D inputs and five archived repair scripts are relocated with their bytes and report bindings intact. Logical historical paths are restored in workspaces when needed.

Four copied game data snapshots were removed from the current asset input set because no tool consumed them. Their original hashes remain recorded, and authoritative data remains in the game repository. Ten consumed game-owned catalogue/decoder/texture/reference fixtures remain current asset inputs; the original import recorded fourteen.

Eleven game-code/naming inputs remain external, enabled only for explicit original semantic audits. C# and Java code are not versioned here. Original installations, protected recordings/decompilation, ignored experiments and existing user files remain in their original repositories/locations.

Independent generated artwork and original reference imagery retain distinct provenance. No third-party reference is reclassified as an independent replacement texture, and this maintenance introduces no new blanket licensing claim. Roughness-map duplicates retain named material/report bindings; deduplicating their bytes is not required for correctness and no existing model is regenerated for that purpose.
