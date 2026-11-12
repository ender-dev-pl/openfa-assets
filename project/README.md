# Current asset layout

`layout.json` maps each current canonical file to the logical path expected by authoring tools in a disposable workspace. It stores paths, semantic roles and ownership, not frozen content hashes. New inputs are registered here; intentional content edits do not require changing this mapping.

Roles distinguish code/metadata (`source`), game-owned data/decoder snapshots (`fixture`), original raster/animation inputs (`source-input`), authored material maps (`material-texture`), finished/reference media (`media`) and archived one-time code (`historical-script`). Retired import inputs have explicit reasons. Historical exact content hashes remain in `project/import-baseline.json`, checked only by the optional import audit.

`verification_support` identifies archived modules whose functions/constants are imported by current native verifiers. This permits materialization for imports, not direct historical script execution.

The three modules in `sources/tools/historical-repairs/` retain their original bytes: `apply_detail_uv_repair.py` is checksum-bound by the current UV repair checker; `apply_fighter_armour_repair.py` and `probe_fighter_armour_tessellation.py` also supply constants and measurements to current fighter verifiers. Workspace preparation restores their logical `tools/blender/` paths. They retain the `historical-script` role and direct execution requires explicit `--allow-history`; relocation does not make completed repair operations safe to reapply. The two obsolete historical index-refresh scripts have been retired.
