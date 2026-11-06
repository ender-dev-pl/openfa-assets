# Open issue scope review — 2026-11-06

Tracking: [#224](https://github.com/ender-dev-pl/openfa-assets/issues/224).
The [decision register](issue-review-2026-11-06.json) reviews the 170 issues that
were open at the start: 126 completed scopes can close; 44 retain required work.
GitHub remains authoritative for live issue state. This register records review
decisions, not a continuously synchronized issue export.

## Completed scopes

- 97 first-source ship, equipment and missile tasks have exact issue-to-asset
  mappings through the migration crosswalk. Their Blend/GLB hashes match model
  metadata and applicable technical/render report bindings; native/imported
  evidence and rendered reviews are present. This completes their explicitly
  limited first-source scope, not final programme acceptance.
- 16 analytical/runtime diagnostic tasks have committed results and documented
  findings. Their recorded historical baselines are retained; closure does not
  claim that subsequent models were covered or that reported defects are fixed.
- Reusable explosions, gallery filtering/playback, HUD/menu deliveries, launch
  mechanisms, PB21 refinement, the all-35 Rigellian pass, refined RIS2/culture
  scaffold kits and seven construction videos have published deliverables and
  existing runtime/review evidence.
- #209 specifically preserves the first 412 original intro frames on a dedicated
  branch. Its published native and 826-frame silent preview match the retained
  delivery hashes. Closing preservation does not merge intro or complete the
  later fidelity work in #212/#213.

Each closed issue receives an English technical comment linking current evidence
and this review commit. Only the verified first-source checkboxes in #62–#66 are
marked complete; unrelated body text and historical comments remain intact.

## Required work remains open

The programme/category issues and earlier high-detail reconstruction issues keep
their explicit final visual, state, calibration and integration gates. #31 keeps
its outstanding mechanism/phase review; #44 keeps its broad acceptance gate even
though used scaffold families were authored in narrower delivery tasks.

- #199: the reported audio inventory is absent from current asset/game main; its
  original implementation is not an ancestor of game main. Publish or migrate
  that analytical deliverable before closing it.
- #204: native menu-generator ownership is implemented only in unmerged PR #205.
- #211–#213: active character/cinematic work remains incomplete or unmerged.
- #214: 101 models and gallery refinements do not satisfy the explicitly deferred
  202 legacy-size compact/detail UI image targets.
- #217: the narrowed PS7C core still needs its scaffold-envelope correction and
  dedicated runtime/render evidence.

## Verification limits

This is an analytical/documentation review. No model, generator, material,
original import manifest or acceptance ledger is changed. Existing actual Blender,
render and browser evidence is retained; no fresh artistic acceptance or rerun of
every historical Blender audit is claimed. Current project/licensing validation
and the required changed-code quality gate are recorded in the decision register.
