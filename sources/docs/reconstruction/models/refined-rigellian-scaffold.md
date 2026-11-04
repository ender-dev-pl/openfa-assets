# Refined RIS2 scaffolding

Refinement issue: [#186](https://github.com/ender-dev-pl/openfa-assets/issues/186), related to the shared construction programme #44.

The preserved prototype remains at `sources/docs/assets/reconstruction/scaffolds/rigellian/size-2/`. The new variant is `sources/docs/assets/reconstruction/scaffolds/rigellian/size-2-refined/`; reviewed images are under the same suffix in `gallery/media/`. See [the stage gallery](../../../../gallery/scaffolds-ris2.md).

The paletted RIS2 descriptors show dense green uprights, copper cross ties and an open interior. Refinement thickens hollow sections, adds a third row of ties to complete tiers, and adds split clamp collars and square locking pins. Darker painted green and copper materials have edge oxidation, grease stains and handling scratches. Clamp engineering and hidden structure are authored interpretations, not recovered original geometry. Pins extend 0.003 beyond the nominal 1.8 envelope; the complete assembly stays within 1.82 units.

All stages 1–17 remain discrete native Blend and standalone GLB files. A stage is the sum of its tier frame values: stage 3 is `[2,1]`, stage 16 is eight complete tiers, stage 17 adds a partial ninth. Foundations occur only once. Lower tiers retain their dimensions; open sockets and hollow sleeves connect consecutive tiers. Mesh data is shared across repeated parts. The existing prototype, textures and reports are preserved.

Integration contract:

- Use the real construction counter and the per-building ceiling from `scaffold-stage-limits.json`. Do not derive height from duration alone or select stages by the final building mesh height.
- `PlacementRoot` is identity; family is RIS2, footprint is 2×2. `construction_stage` and each tier's `stage_frame` are exported as extras. BottomSocket and TopSocket mark attachments. Coordinates in Blender use Z-up; glTF uses its standard Y-up export transform.
- Nominal pitch is about 0.567 units, derived from the eight-pixel legacy repeat at a diagonal orthographic projection. It remains provisional until the game presenter calibrates placement, footprint and camera projection.
- The requested presentation has four phases: erection, insertion/reveal of the target building at full scaffold height, reverse-order dismantling from the top, and completion. The building remains visible throughout dismantling. `construction-sequence.json` supplies ascending/descending stage lists for all twelve definitions and explicit interior-shoring node masks, leaving the outer shell visible while avoiding internal supports intersecting the inserted building. Interior shoring is removed at reveal. This sequence is a user requirement, not a newly claimed legacy timing discovery. The simulation/presenter owns durations and transitions; the renderer draws its state.
- This variant covers twelve Rigellian 2×2 definitions, including RI11; it is not a substitute for the other culture/footprint families. RI11 stops at stage 2; Databanks reaches stage 17.

Technical native/imported checks and actual renders establish the editable/export contract and reviewed refinement. They do not establish exact legacy pixel fidelity, original ownership-based family selection, world-height calibration or completed OpenFA3D integration. The broad programme acceptance remains open.
## Verified refinement result (2026-11-02)

All 17 native sources and 17 independent GLB imports passed the Blender 4.5.15 runtime checks. All 51 front/rear/imported views passed framing, exact alpha/silhouette comparison and RGB tolerance; maximum masked RGB mean difference is 0.0312/255 and alpha difference is zero. The nine-tier stage 17 has 3,428 mesh nodes sharing nine geometry templates. Joints, sockets, native/imported UVs, packed image pixels, material values, transforms and single foundations were checked. The stage overview, stage-2 close view and stage-17 rear view were inspected visually.

Diagnostic alpha occupancy improves from approximately 47% to 58% at stage 2 (source 64%) and from 72% to 86% at stage 17 (source 87%). This measures structural density, not pixel-mask fidelity or original world-height calibration.

Fourteen workspace regression tests and three construction-sequence tests passed. Current project/gallery verification passed for 303 definitions and 384 existing catalogue studies; the refined scaffold is linked separately, without changing prototype/inventory acceptance. `Verify-ChangedCodeQuality.ps1` passed in the game checkout against its current HEAD, including its existing unrelated C# working changes. The asset repository has no C# changes; the game-specific gate cannot run directly from the asset-only directory because it reads game source contracts. Logs are retained in ignored `artifacts/issue-186/`.

Reproduce from the assembled workspace: `author_refined_rigellian_scaffold_wear.py`, then Blender `build_refined_rigellian_scaffold.py` and `verify_refined_rigellian_scaffold.py`, followed by Python `review_refined_rigellian_scaffold.py`, `describe_refined_scaffold_sequence.py` and `test_refined_scaffold_sequence.py`. Publish reviewed media and editable assets to the registered paths. No game code was modified and no game runtime acceptance is claimed by this asset-only milestone.
