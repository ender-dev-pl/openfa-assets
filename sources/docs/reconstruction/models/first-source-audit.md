# First-source coverage audit (#1099)

The first-iteration-only pass has registered native sources for all 303 catalogue definitions: 177 buildings, 41 ships/vehicles, 16 shared hardpoints and 69 missiles. This is not final reconstruction acceptance. The coverage inspection itself changes no model. Subsequent authorized technical corrections are documented separately in #1111 and #1108; artistic refining remains deferred.

Run `python tools/blender/audit_first_source_coverage.py --check` after generating the report with the same command without `--check`. The report binds the inventory and review ledger by SHA-256 and contains the exact selected Blend hash, sibling file hashes, evidence gaps and accepted ledger gates for every definition. Selection uses the last present registered study, matching the existing culture sheets; it is not an artistic ranking. Earlier registered studies remain preserved.

## Verified evidence and limits

All 303 selected Blend files exist and match the inventory hash. All 303 also have a sibling GLB, including the transporter's existing `transporter.glb`; lack of the canonical `model.glb` name is not missing geometry. No native source or export was regenerated.

141 selected studies have no gaps in the narrowly checked file contract. This checks current Blend/GLB bindings in metadata/reports and render pixel hashes, not the substantive validity of every assertion or current execution in Blender. Ten selected models have an accepted `native_and_glb_runtime` gate in the persistent ledger. Report presence must not silently promote the other models to accepted gates.

155 selected directories lack canonical technical and render reports. For 154, canonical metadata does not bind the current Blend/GLB and catalogue identity; older building metadata uses other schemas. This is missing comparable verification evidence, not proof that those models are broken. The transporter has `manifest.json`, native/export files and reference views, but lacks canonical model/technical/render JSON. Seven older equipment reports do not provide either supported per-view hash dictionary. Combat Eagle and Scoutship use a legacy `hashes` dictionary; their actual listed pixels were verified rather than classified as absent.

The full inventory verifier passed for 303 definitions and 1444 reference occurrences. It validates the ten accepted runtime evidence bundles separately. The file audit does not rerun Blender, validate geometry/materials/UVs or visually accept any asset. No game integration, animation completeness, state completeness, calibrated attachments or high-detail artistic acceptance follows from these counts. Required changed-code quality base: `05cc17ad`. This milestone is analytical; no application smoke test is required.

## Handoff boundary

The user's current instruction authorizes first versions only. First-source coverage is now full, so do not duplicate an existing model or automatically begin refinement. Obvious technical corrections are now explicitly authorized by the user. Further verification can reconcile historical evidence formats and identify specific missing verification; never manufacture successful runtime results by converting old report shapes. Any accepted technical gate needs actual native/import verification and exact evidence binding. Artwork refinement and construction scaffolding remain deferred until directed.

The complete long-term goal remains open. Outstanding final acceptance covers quality/detail, source fidelity, required operating/damage/launch variants, calibrated attachments and integration. These require their own evidence; the first-source total does not close them.
