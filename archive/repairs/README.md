# Historical one-time repairs

These five Python files are immutable evidence from previously completed repairs:

- `tools/blender/apply_detail_uv_repair.py`: one-time UV repair.
- `tools/blender/apply_fighter_armour_repair.py`: one-time armour topology repair.
- `tools/blender/probe_fighter_armour_tessellation.py`: proposal against the original unrepaired topology.
- `tools/blender/refresh_uv_repair_indices.py`: dependent index retention using original game commit history.
- `tools/blender/refresh_fighter_armour_indices.py`: dependent index retention for the armour repair.

They are not reusable current model generators. Their exact bytes are retained because historical reports bind them. The active layout restores their original `tools/blender/` paths with `prepare --include-history` or optional evidence preparation. Two modules provide measurement functions/constants imported by current fighter verifiers, so their entries explicitly mark `verification_support` and are also materialized by ordinary preparation. No archived script is executed during preparation.

The launcher refuses direct execution unless `--allow-history` is explicit. In that case Git reads use the original game repository's actual Git directory, supplied with `--game-root`, rather than looking for old game commits in the new asset repository. A matching historical model/data workspace is still required. Do not reapply already-completed migrations to current corrected models. No historical execution is part of ordinary preparation or verification.
