# Scoped native and GLB runtime evidence

Tracked in [#976](https://github.com/ender-dev-pl/ed-openfa-game/issues/976), relates to #946/#947/#948 and the model issues below.

The first six detailed Rigellian building studies now have an explicit `native_and_glb_runtime` review in `review-ledger.json`, bound to their exact registered Blend revisions. All six verifiers and seven-view render reviewers were rerun in Blender 4.5.15 LTS on 2026-10-29 before recording the gate.

| Catalogue ID | Study | Model revision | Issue |
| --- | --- | --- | --- |
| `openfa:building/legacy/040` | Central Unit | 3 | #969 |
| `openfa:building/legacy/041` | Filtration Plant | 4 | #971 |
| `openfa:building/legacy/042` | Nourishment Bank | 4 | #972 |
| `openfa:building/legacy/043` | Community | 2 | #973 |
| `openfa:building/legacy/044` | Health Unit | 2 | #974 |
| `openfa:building/legacy/045` | Strategic Bunker | 2 | #975 |

## What this gate proves

The reviewed native model was reopened, standalone GLB imported, geometry/material/hierarchy and per-model structural checks exercised, and the imported model actually rendered. Six native views and one imported view passed their framing, transparency and native/imported comparison checks. Existing per-model reports retain their diagnostic limits; for example a connected surface-sample contact graph is not exhaustive solid-intersection proof.

RI01 previously had actual GLB geometry checks but no retained imported-render view. That view and a seven-view gallery/report are now provided. Its existing Blend, GLB, geometry and clean materials are unchanged; the pre-instruction model did not receive retrofitted wear.

## Exact evidence binding

`reviewed_model.runtime_evidence` binds the Blend, GLB, metadata, technical/render reports, verification/review scripts, relevant authoring/helpers, authored maps and retained rendered pixels: 206 file bindings across these six reviews. Binary files use exact SHA-256 bytes. JSON/Python hashes normalize CRLF to LF so a text checkout's line endings do not masquerade as a model/export change.

`model_runtime_evidence.py` validates those bindings and cross-checks catalogue identity, Blend/GLB hashes, model/report revision, mesh count, native/imported view coverage, view-pixel hashes and verified margins. `verify_reconstruction_inventory.py` invokes it whenever this technical gate is accepted. Changing a GLB, report, bound script or render now invalidates the gate even if the Blend is untouched. Changing a report and recomputing just its file hash cannot substitute evidence for a different model revision.

`test_model_runtime_evidence.py` exercises all six current reviews and checks rejection of a changed GLB digest, missing imported render, swapped catalogue identity, repository-escaping evidence path and a rehashed technical report for another model. A copied LF-only checkout verifies portability of text evidence. Temporary fixtures are created under the workspace and removed only after checking their resolved containment; user files are not modified.

## What remains open

This gate is scoped to Blender native and imported-GLB operation. It does not accept artistic fidelity, high-detail quality, material art direction, moving/construction/damage state coverage, calibrated attachments or game-client integration. All other gates remain false for these six studies. All 303 final-visual-acceptance gates remain open across the full catalogue; no race/category has been declared complete by this milestone.
