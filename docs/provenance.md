# Provenance and ownership

`project/import-baseline.json` is the retained import record: original repository/commit, original path, then-current destination, role, ownership, length and SHA-256. It is no longer the active workspace configuration. `project/layout.json` records current locations, roles and explicit retirements; changing a current file does not rewrite the historical import hash.

All 396 Blend files and 405 GLB files are preserved byte-for-byte by this reorganization. The 698 authored material PNGs, original 2D inputs and three retained repair/proposal modules are relocated with their bytes and report bindings intact. Logical historical paths are restored in workspaces when needed.

Four copied game data snapshots were removed from the current asset input set because no tool consumed them. Their original hashes remain recorded, and authoritative data remains in the game repository. Nine consumed game-owned catalogue/decoder/independent-texture fixtures remain current asset inputs; the original import recorded fourteen.

Eleven game-code/naming inputs remain external, enabled only for explicit original semantic audits. C# and Java code are not versioned here. Original installations, protected recordings/decompilation, ignored experiments and existing user files remain in their original repositories/locations.

Only independently authored imagery is versioned. Original-game pixels, screenshots and composites containing them are excluded; local decoding from a licensed installation remains available. No third-party reference is reclassified as an independent replacement texture, and this maintenance introduces no new blanket licensing claim. Roughness-map duplicates retain named material/report bindings; deduplicating their bytes is not required for correctness and no existing model is regenerated for that purpose.

## Original-game media exclusion

The initial import and its three local descendants were rewritten to exclude 93 image/video files: 81 decoded explosion frames, four explosion contact sheets, one explosion GIF, four extracted exhaust images, an airburst comparison video, a missile comparison sheet containing extracted exhaust, and the legacy colony screenshot. No Blend or GLB bytes were changed.

`project/excluded-media.json` lists the excluded paths. The retained import manifest and current layout omit them; the ignore rules and current verifier enforce this boundary. Scripts and numerical reference metadata are retained. Tools that explicitly consume original reference images require local evidence; their historical reports do not imply those images are distributed here. GitHub may retain old commit URLs or cached objects after a branch history rewrite; rewriting a branch does not certify server-side erasure.
