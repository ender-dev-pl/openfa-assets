# Current asset layout

`layout.json` maps each current canonical file to the logical path expected by authoring tools in a disposable workspace. It stores paths, semantic roles and ownership, not frozen content hashes. New inputs are registered here; intentional content edits do not require changing this mapping.

Roles distinguish code/metadata (`source`), game-owned data/decoder snapshots (`fixture`), original raster/animation inputs (`source-input`), authored material maps (`material-texture`), finished/reference media (`media`) and archived one-time code (`historical-script`). Four retired import inputs have explicit reasons. Historical exact content hashes remain in `migration/files.json`, checked only by the optional import audit.

`verification_support` identifies archived modules whose functions/constants are imported by current native verifiers. This permits materialization for imports, not direct historical script execution.
