# Achaean building delivery and final audit

The AC01–AC26 remaster programme delivers **26 current editable Blend/GLB pairs**, one per building. The catalogue selects the same pair for gameplay, construction menus and SciTek presentation. Historical studies remain source history, not additional package choices. Tracking: openfa-assets #256; the mobile-ship programme #248 and game-client integration are separate.

Use [the delivery manifest](achaean-building-remaster-delivery.json) for canonical paths, SHA256 values, footprints, definition classes, construction counts, geometry budgets, placement roots and state/scale contracts. The machine-readable [completion audit](achaean-building-completion-audit.json) cross-checks these against the current inventory, actual GLB accessors/nodes, source-bound Blender reports, renders and gallery. [Model milestone signatures](achaean-building-milestones.json) record the actual GitHub verification of all 26 latest model commits.

## Reference and fidelity review

[The reference review](achaean-building-reference-review.json) covers all 26 correctly paletted surfaces, all **1,066 catalogue image updates**, both extra zoom layers for every building, functional records 1012–1037 and architecture record 166. Original images and verbatim legacy lore remain outside this repository. Actual current GLB front/quarter renders were compared with the additional AC01–AC16 zoom sources during the final audit; their principal assemblies were retained. AC01's original five-sample review was expanded to all 41 phases. AC03's first extra zoom layer contains a coarse reveal image in UI, not evidence for a separate operating model.

All **36 actual research subjects** were resolved through their preview and information bindings. Three spaced updates from each of the 72 colour `_MA` and technical `_SCITEK` videos were decoded with the original codec/palette and visually reviewed for subject applicability. Named PB/PH/PM surface subjects are Terran; ST images depict generic research equipment. No research video is directly assigned to an AC01–AC26 building profile. These are functional/technology references, not permission to replace Achaean body geometry with another culture's diagrams. This conclusion uses actual bindings and reviewed pictures, not the absence of an AC filename. The sampling does not claim exhaustive mechanical-state inspection of those other subjects.

There were at most three actual ImageGen concept attempts per building, with the exact prompts, selected images and fidelity feedback in each visual report. Actual GLB render feedback produced further geometry corrections. The final audit confirmed a missing fourth lower red/amber slit on AC21's outer-right chamber and restored it in the canonical model, with fresh export, source/import validation and gallery updates. Source-visible anatomy takes priority over a concept's hidden details; no numerical “80% fidelity” score is claimed.

## Runtime, geometry and preservation

Each selected model has actual saved-native and independent GLB-import verification in Blender 4.5.15. Current source, helper, binary, material/texture and render hashes remain bound to those results. The completion audit recomputes **80 native/import render pairs** and validates actual per-instance GLB triangle counts rather than counting unique meshes alone. New models carry restrained material-appropriate wear; the visual reports distinguish interpreted finish/hidden engineering from recovered detail.

All **29 original source pairs**, including the previous AC12–AC14 launch-facility studies, remain byte-identical to the initial preservation baseline. Their useful mechanisms and relevant design decisions were separately reviewed; preservation does not make an old stage label a current package selection.

AC12 retains its verified sliding-cover cycle. AC20, AC25 and AC26 retain their exact original native heading controllers/actions, with denser GLB sampling preserving original clip names/timing. Their gallery videos are heading demonstrations, not recovered autonomous firing or idle loops. Source-specific checks cover supports, openings, visibility, named moving parts and sampled states. No continuous collision-sweep proof is claimed. Static buildings have no invented operating animation inferred from catalogue reveal/highlighting.

Wireframe or diagnostic views should derive from the canonical geometry. Do not package separate “better SciTek”, construction and gameplay copies. Identity placement roots, ground height, axes and per-object state/scale limits are recorded in the delivery manifest. Client world/tile scale, heading-index/muzzle calibration, firing/activity triggers, package integration, Android frame time and final user artistic acceptance remain separate from this asset-only audit.

## Recheck the current files

```powershell
python tools/audit_achaean_building_completion.py
python -m unittest discover -s tools -p 'test_achaean*evidence.py'
python tools/verify_project.py
python tools/verify_licensing.py
node tools/test_gallery_filters.cjs
```

Run a model's bound Blender verifier after changing its source or geometry, then review the real renders, refresh its evidence/delivery and rebuild both galleries. A changed hash alone is not a new validation run. Reference-only final-review annotations did not rewrite unchanged geometry/runtime results.

The programme reused an existing isolated checkout and dependencies. No additional game builds, release archives or full asset copies were needed. Only task-created exporter/preview scratch was removed after its processes finished; original references, historical evidence and user files were preserved.
