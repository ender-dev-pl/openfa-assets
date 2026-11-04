# Public snapshot and gallery deployment

This checkout is a clean publication snapshot of the private authoring repository's
main branch. It starts a new Git history with a project publication identity.
The chosen migration replaces main in the existing repository and removes obsolete
remote branches and tags; the previous history is preserved in a local private Git
bundle. Do not merge the old history back or mirror-push private backup refs.
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

Use Settings > Pages > GitHub Actions after publishing this clean repository.
`public-pages.yml` verifies pull requests and pushes to `main`. Deployment requires
an explicit workflow dispatch with the `deploy` input enabled; a history push alone
does not publish the site. Its deployment job alone receives Pages/OIDC write
permissions. It uploads only `_site`, never
the checkout, raw logs, migration evidence, Blender files or private workspace files.

`build_public_pages.py` produces three HTML entry pages, metadata-free WebP previews
and only referenced animation media. Full images and editable model downloads link
to public repository files; source/evidence links open their GitHub pages. A local
link check and a 900 MiB artifact budget run before upload. The full gallery source
is larger than the [1 GB Pages site limit](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

When publishing under another repository name, pass `--repository owner/name`.
The workflow supplies this automatically. Before first publication, also review
the existing repository's issues, attachments, releases and Actions artifacts;
those are not part of a Git snapshot and remain after replacing branch history.
