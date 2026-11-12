# Public snapshot and gallery deployment

This checkout is a clean publication snapshot of the reviewed asset repository's
main content plus the confirmed ownership/provenance clarification. It starts a
new Git history signed with the maintainer's configured Git/GPG identity. Preparing this root commit
does not replace remote main, publish unfinished branches or change visibility.
Keep old authoring history private. Port unfinished work as reviewed file changes;
do not merge old-history branches into this root or mirror-push backup refs.
GitHub-hosted pull-request refs, cached commits, issues, attachments, releases and
Actions history are outside this branch rewrite and are not certified erased.

## Metadata transformations and evidence

`project/publication-sanitization.json` records every transformed asset by its
relative path, original hash and public hash. Native models have only their
fixed-width path strings replaced and zero-filled; all other decompressed bytes
are identical. Existing in-repository dependencies are rebased to relative paths.
Geometry, animation, materials, packed pixels and Blender DNA are preserved.
PNG ancillary text/EXIF/timestamps and JPEG EXIF/IPTC/comments are removed without
re-encoding image data. Decoded pixels were compared before and after each change.
GLB exports are unchanged. No model refinement is included.

Current inventory and report hashes are rebound only after these invariants are
verified. Existing visual checks remain historical checks of identical model/image
payloads; they do not claim a new artistic review. The separate native-reopen and
independent-GLB-import run is recorded in `project/publication-runtime.json`.
Frozen `project/import-baseline.json` hashes remain original import provenance. Consequently the
optional `audit-import` comparison is expected to report metadata transformations;
it must not be treated as a current publication failure.

Earlier documentation describing byte-for-byte imported preservation refers to
the pre-publication archive. The transformation manifest explicitly supersedes
that statement for public files, without rewriting the original import record.

## Publication checks

```sh
python -m pip install -r requirements.txt -r requirements-publication.txt
python tools/test_publication.py
python tools/verify_publication.py
python tools/verify_project.py
node tools/test_gallery_filters.cjs
python tools/build_public_pages.py
```

The guard inspects compressed native models, GLB JSON, text and image metadata;
credential matches are reported without printing their values. It is a regression
guard, not a certification that arbitrary secrets or original-game media cannot
exist. Do not add local authoring logs, personal credentials or original-game pixels.

To repeat native runtime checks with Blender 4.5 LTS:

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/verify_public_models.py
```

## GitHub Pages from main

The repository has one public branch, `main`, published as a signed parentless snapshot. Historical source branches, including unfinished intro work, are preserved privately in `openfa-assets-archive` under `history/2026-11-12/`. Do not merge pre-snapshot histories back into the public root.

GitHub Pages uses **Deploy from a branch → main → /docs**. `docs/index.html` redirects to the optimized current gallery in `docs/pages/`, preserving catalogue filters. There is no `gh-pages` branch. Source downloads point to current `main`; editable models and the large authoring gallery remain outside the Pages source folder.

Build the deployable gallery once after changing its inputs:

```sh
python tools/build_public_pages.py --output docs/pages --repository ender-dev-pl/openfa-assets --ref main
```

The output folder must be empty or absent; do not create another copy as a substitute for checking an existing result. Reuse the committed result for verification and publication:

```sh
python tools/build_public_pages.py --output docs/pages --check-existing
```

The manifest binds every embedded source and emitted file by SHA-256. CI rejects stale source pages/media or modified output without rebuilding the site. A push to main updates native Pages from the same committed bytes. This does not depend on Actions artifact storage or recreate a publication branch. The old branch publisher fails closed.

The optimized site has a 900 MiB budget. Full-resolution source images and model downloads are linked to GitHub rather than embedded in the published site. Historical metadata-normalization evidence remains provenance of unchanged geometry and pixels, not a claim of a new model-rendering run.
