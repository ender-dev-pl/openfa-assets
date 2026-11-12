# Public snapshot validation

Historical metadata/runtime validation was performed on 2026-11-04 against the
private pre-publication snapshot. The results below describe that run, not the
current expanded catalogue. See [the clean initial validation](initial-publication-validation.md)
for current preparation checks.

- 761 native Blender sources sanitized. Every decompressed byte outside replaced
  path strings is identical to the input archive; model payloads are unchanged.
- 5,513 PNG files had ancillary metadata removed. Every decoded pixel was compared
  with the original. Other unchanged images remain available.
- Blender 4.5.15 reopened all 761 native sources and resolved external image
  dependencies. All 770 GLB exports were independently imported successfully.
- Current project verification passed: 303 definitions, 444 registered studies,
  972 Python sources. Current hash references and animation bindings are valid.
- Six publication tests, six animation tests, five Braccatian audit tests and eight
  orbital-station mutation tests passed. Portable font lookup was exercised for
  all eight affected Python tools at three font sizes.
- Gallery tests passed for all 63 race/type combinations, 54 animated studies,
  440 catalogue entries, 118 UI entries and 19 scaffold families / 281 stages.
- Actual headless Edge loaded all three generated Pages entry points without
  JavaScript or HTTP errors. Filtering, empty/reset state, video playback and
  a 390-pixel mobile viewport passed. Desktop/mobile screenshots are retained
  only as local evidence outside the public Git tree.
- Pages artifact: 13,988,530 bytes before its small build manifest, with 652
  explicitly referenced assets. Only generated HTML, metadata-free previews and
  referenced animation media are included. Download/source links target the
  public repository rather than embedding the full authoring archive.
- The repository-wide publication guard passed with no private-path or known
  credential-signature findings. Its scope and limitations are documented in
  `publication.md`.
- The game `tools/Verify-ChangedCodeQuality.ps1 -BaseSha HEAD` passed in an isolated
  checkout of committed game revision `f87d7f872`. No game source was changed by
  publication preparation. The initial invocation in the shared game working
  directory encountered unrelated concurrent C# formatting changes; those were
  left untouched.

These historical checks validate the earlier sanitized snapshot. Preparation of
the new root is tracked separately; visibility remains private and Pages
deployment requires a separate explicit workflow dispatch. Hosted pull
requests, issues, attachments, Actions history and cached commit objects are not
erased by a branch rewrite.
