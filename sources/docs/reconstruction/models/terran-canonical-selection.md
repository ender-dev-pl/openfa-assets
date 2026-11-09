# Terran shared-source candidates: selection deferred

Programme #248's source audit found that three already-authored shared ship models were documented as authoritative but lacked explicit canonical selection in the main inventory. The initial metadata selection was withdrawn after the user reported loss of detail in the SciTek refinements and reserved artistic review. These existing sources remain candidates; no new canonical selection or replacement recommendation follows from technical validation.

| Runtime object | Candidate source/export directory | Existing physical meshes | SciTek information |
| --- | --- | ---: | --- |
| `openfa:terminator` | `sources/objects/terran/terminator/refined/` | 71 | Research30 |
| `openfa:fleet-battleship` | `sources/objects/terran/fleet-battleship/refined/` | 45 | Research09 |
| `openfa:command-cruiser` | `sources/objects/terran/command-cruiser/refined/` | 82 | Research35 |

Each directory contains `model.blend` and `model.glb`. These files were not changed. The per-ship README and metadata already establish shared use by gameplay, the ship catalogue and SciTek. The preceding inventory/gallery choices are restored so both existing studies remain available for comparison. Do not change gameplay or package selection on the strength of this report; wait for the user's detail review. Historical physical SciTek solids are not extra gameplay payloads. Dedicated information/timeline assets remain distinct, since they carry presentation semantics rather than another current coloured ship.

Gameplay uses frame1 without the presentation turntable animation. The three documented roots are identity at that pose. This selection does not establish client scale, equipment mounts or the client's animation handling; integration must apply those rules explicitly.

## Fresh read-only runtime evidence

`verify_terran_canonical_selection.py` reopens each saved native source with scripts disabled and independently imports its existing GLB in Blender4.5.15. It checks mesh identities/counts, material presence, embedded images, identity of the gameplay root and matching world matrices/evaluated bounds at frames1/31/61. Actual source/export hashes are checked before and after; no model, geometry, material, animation or accepted exterior is rewritten. The companion JSON binds the verifier, actual binaries and measured results.

Run Blender with `sources/tools/blender/verify_terran_canonical_selection.py -- <report-path>`. Reusing existing binaries avoids unnecessary regeneration and extra full copies. Three pose samples are a smoke check, not exhaustive animation, topology, UV, material-parity or legacy-fidelity proof. Existing subject-specific source-retention, wire correspondence and animation checks remain separately documented in each ship's SciTek source directory.

## Remaining protocol work

No ImageGen concept is fabricated or claimed by this metadata correction. Terran source-specific concept and corresponding legacy/imported-render feedback remain open under #248; construction-stage reports for the three small Terran ships likewise do not prove that requirement. All cultures' completed spacedocks remain excluded.

The earlier `mobile-remaster-protocol-audit.json` is an immutable cross-branch snapshot. Its historical selection state is not rewritten; this report retains technical evidence while deferring the proposed selection. Original legacy pixels remain outside published sources. Gallery entries retain the prior comparison choices, with no new media or model copies.
