# Clean initial publication validation

Preparation date: 2026-11-06. Tracking: asset repository issue #223.

## Scope

The initial tree contains the reviewed main content and the confirmed ownership/provenance clarification. It excludes unfinished intro and other unmerged feature work. Preparing the root does not replace remote main or change repository visibility.

Current documentation no longer depends on retired asset-repository commit links. Game-repository provenance revisions, file SHA-256 values, generator bindings and historical runtime evidence remain intact: they identify actual inputs and are not claims that private asset history is publicly available. Historical source-bound evidence is retained rather than rewritten to fabricate a new validation run.

The previous authoring commits are not parents of this initial commit. The author and committer use the maintainer's configured Git identity with GPG signing, as explicitly requested. This intentionally retains the configured commit identity; workstation paths and previous commit ancestry are excluded. Existing source/model/image files are preserved; this preparation does not regenerate assets or change their payloads.

## Boundaries

The private-path and known credential-signature guard inspects current text, native models, exported model metadata and image metadata. It cannot certify the absence of every possible secret or identify copyright ownership from pixels. Legacy provenance and license boundaries are documented separately.

A root commit cleans its own ancestry only. Other remote branches, pull-request refs, issues, attachments, Actions history and GitHub caches are outside this tree. They must be considered before making the existing repository public. Do not merge old-history branches into this root; port reviewed file changes instead.

The game repository pins asset revisions in `tools/OpenFA.Content/graphics-model-sources.json`; its `provide-native-models` action verifies that those commit objects exist. Before replacing remote main or discarding old refs, migrate those pins and any reviewed runner snapshot bindings to the new published root through a separate verified game integration change. Matching file bytes alone do not satisfy the current commit-existence checks.

## Verification

See `project/initial-publication-validation.json` for checks actually run against this prepared tree. Earlier publication/runtime reports remain historical evidence and have not been relabelled as fresh Blender validation.
