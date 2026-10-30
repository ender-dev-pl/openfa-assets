# Provenance and ownership

`migration/files.json` records the source repository, exact source commit, original path, destination, file size, SHA-256, role and ownership for every imported file. All 396 native Blend files and 405 GLB files were copied byte-for-byte; migration generates contact sheets and indexes, not model geometry or new refinements.

Most files move to this repository. The 14 explicitly marked game-owned data/decoder/texture/reference fixtures are copied for reproducibility and remain authoritative in the game repository. Historical scripts/evidence refer to their original relative paths; the workspace materializes those paths without changing source-bound checksums.

The imported collection includes independent generated artwork and separate historical reference imagery. Existing reference images retain their provenance and are not reclassified as independent authored textures. No new blanket license or ownership claim is introduced for imported third-party reference material.

This migration covers versioned canonical authoring files. Ignored `.asset-lab` research environments, temporary working copies in `artifacts/`, original installations, protected recordings and the durable decompilation stay in their existing locations. They are neither deleted nor silently represented as canonical completed models. Historical game commits remain available in the origin repository; this new repository begins with a provenance-preserving import, not rewritten game history.

The 11 game-code/naming inputs are recorded separately as `external_inputs`, with their original hashes. No C# or Java game-analysis source is versioned in this repository. Semantic audits require the matching game checkout.

The three quick-menu source PNGs have been reclassified from gallery media into `sources/ui/quick-menu/`. Their original paths, byte lengths, SHA-256 values and fixture ownership are unchanged in the import manifest; only their canonical destinations and roles changed.
