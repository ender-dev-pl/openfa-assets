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
Frozen `migration/` hashes remain original import provenance. Consequently the
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

## GitHub Pages

The prepared site lives on the dedicated `gh-pages` branch, at its root. This
branch contains only generated HTML, metadata-free WebP previews, `.nojekyll`,
referenced animation media and the build manifest. It has its own publication
history; authoring files, logs and private working directories are not copied.

The current GitHub plan does not support Pages while this repository is private.
Content can be prepared and pushed beforehand, without changing visibility or
requesting a Pages build. After making the repository public:

1. Open Settings > Pages.
2. Set Source to **Deploy from a branch**.
3. Select **gh-pages** and **/(root)**, then Save.
4. Wait for GitHub's Pages deployment. The expected address is
   `https://ender-dev-pl.github.io/openfa-assets/`.

`public-pages.yml` verifies pull requests and pushes to main without uploading
Actions artifacts. This avoids the organization's exhausted artifact-storage
quota during verification. For later content updates, manually run the workflow
with `deploy` enabled. Only that job gets contents/Pages write permissions. It
rebuilds the site, replaces gh-pages with a clean content commit using an exact
SHA lease, and explicitly requests the native Pages build. Pages must already be
configured to the gh-pages branch; no token with administration privileges and no
extra repository secret are required for routine updates.

For local preparation, choose a new output directory and use authenticated Git:

```sh
python tools/build_public_pages.py --output artifacts/public-pages-content --repository ender-dev-pl/openfa-assets --ref main
python tools/publish_public_pages.py --site artifacts/public-pages-content --repository ender-dev-pl/openfa-assets
```

The second command updates only gh-pages. It does not change repository visibility,
configure Pages, or request a build unless `--request-build` is explicitly supplied.
The publisher checks allowed file types, all local page links and private metadata
before creating a content-only root commit; it refuses source directories,
symlinks and previously initialized output repositories.

The builder keeps a 900 MiB output budget. Full images and editable source/model
links point to the public source repository rather than embedding the authoring
archive. The full gallery source exceeds the
[1 GB Pages limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).
The native Pages deployment is managed by GitHub; this repository's workflow does
not upload build artifacts or delete existing organization artifacts.
