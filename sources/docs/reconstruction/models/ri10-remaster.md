# RI10 Ground Deck: one animated canonical model

Tracking: openfa-assets #253 and per-building #41. Preserve `openfa:building/legacy/049`, definition class 26, footprint 3x3 and construction updates 18. Original functional record 910 identifies the Rigellian Landing Pad. Related original descriptions establish access to underground spacecraft hangars: the open mouth is a deep shaft, not a shallow grille or floor. Culture record 18 supplies architectural context without specifying machinery.

## Reference, concept and retained geometry

Correctly paletted body, closed base-plus-cover composite and cover descriptors were inspected. Two rigid green D-shaped halves disappear progressively toward the sides; descriptors 15/16 are empty cover overlays, while 17 has separate lower-structure/mixed-shadow pixels. Purple shadow is not metal. The existing mechanism evidence binds source hashes, measured cover widths and all 65,536 signed-altitude cases. Current game selector code is equivalent for its Terran Landing Pad ID; current Rigellian client registration is not established by that equivalence.

One actual built-in ImageGen request used those original images. Exact prompt: `ri10-concept-prompt-1.txt`; public concept: `gallery/media/concepts/rigellian/ri10-review-1.png`. It preserves paired covers, deep shaft, two red wall fittings, brass buttresses, front steps and bent right mast. Its added seams, compact body and changed support proportions are interpretation. The established side cassettes/telescopic mechanics and body proportions remain an approximation, not final artistic acceptance. Original pixels stay private.

The latest revision-six source is preserved, including its corrected deep shaft, narrow front supports, shortened mast, undercuts and rigid covers. All 45 asset mesh surfaces match the original evaluated closed geometry exactly. There are 19,010 evaluated/export triangles (13,170 before modifiers), seven used materials and four embedded maps. Preview terrain holdout is excluded from the GLB. These counts do not certify Android performance or exhaustive engineering fidelity.

## Single model, two clips, no pose-model duplication

Use `sources/objects/rigellian/ground-deck/model.blend` and `model.glb` for gameplay, build menu and SciTek. Earlier full-model pose exports are historical studies and must not be added to the package alongside the canonical pair.

- `GroundDeckCoverCycle` preserves the original authored 61-frame preview: frame 1 closed, 16 intermediate, 31 open, 61 closed. Its timing and lift/two-stage retraction are inferred, not recovered legacy timing.
- `GroundDeckDescriptorStates` contains discrete rigid poses for descriptors 2–17, with STEP interpolation. Sample the absolute glTF input time `descriptor / 24` seconds, using the explicit mapping in model.json. All six translation controls share the same meshes/materials/maps as the cycle. Do not tween this lookup or interpret the descriptor index as a direction.

No attached ship maps to descriptor 2. The preserved signed-altitude bands select the descriptor; the model does not implement simulation selection. Descriptors 15/16 leave physical covers fully stowed while retaining the static housing. Descriptor 17 uses that physical cover pose, but its original lower-structure/purple-shadow composition remains explicitly unverified. A complete 3D model is not an original empty overlay.

Named controls are `CoverLeft`, `CoverRight`, `CoverLeftInner`, `CoverLeftOuter`, `CoverRightInner`, `CoverRightOuter`. Only translation is animated; solid segment scale stays one. Root is identity `PlacementRoot`, local -Y forward, +Z dorsal, ground Z0. Closed full-geometry bounds are [-1.350000, -1.155000, -2.020000] to [1.350000, 1.020000, 1.290084]. Shaft-tagged geometry deliberately extends below terrain; integrate an opening/mask rather than raising the whole model to hide it. Nominal footprint does not establish scene-to-game scale.

## Actual source and independent GLB validation

Blender 4.5.15 reopens the saved native model and independently imports GLB. All 45 physical surfaces are positive and closed after welding UV/normal splits. The existing 61-pose moving/fixed and separate-stage intersection checks run in both formats. Six rigid controls, eight moving meshes, stationary housing, return-to-closed transforms, shaft-only underground geometry, full colour/roughness pixels and material values are preserved. Nine open-mouth rays reach the remote dark bottom below -1.9; viewing rays verify that closed covers occlude both red wall fittings and the open frontal diagnostic view reveals them.

All sixteen descriptor poses also undergo topology, rigid-scale and moving/fixed/separate-stage checks. An initial import discrepancy was diagnosed: Blender places the descriptor NLA strip at frame 1 while its action keys retain frames 2–17. The verifier measures the action/strip offset (native 0, imported 1) and samples accordingly, without changing imported keys or GLB data. The continuous cycle remains frame-aligned. Maximum native/import matrix error is below 1.50e-7 and closed surface error below 1.20e-7.

Twenty actual native/imported view pairs were inspected, including closed/intermediate/open/top and fourteen distinct descriptor renders. All alpha channels and threshold silhouettes match; mean channel differences stay below 0.0026/255 with margins at least 72 pixels. Two source-bound gallery videos are rendered from the independently imported GLB with the measured time mapping. Their temporary frames are removed after encoding.

These are sampled surface-intersection checks, not continuous swept-volume or containment proof. Exact guide/load attachments, outer body/cassette fidelity, construction/damage states, descriptor17 composition, terrain/client calibration and final user artistic acceptance remain separate. No client or simulation code changes here.

## Reproduction and disk

Run `remaster_rigellian_ground_deck.py`, `verify_remastered_rigellian_ground_deck.py` and `render_rigellian_ground_deck_animations.py` in Blender background mode with Python exit code 1. Inspect outputs and record feedback, then register the canonical folder and rebuild galleries. Bind reports to the exact model, tools, mechanism evidence, concept/prompt, renders and videos; never replace hashes to imply a run. Reuse the existing checkout. No game build, archive or additional worktree is required. Clean only precisely identified task-owned temporary frames and empty exporter folders after their processes finish.

## Final audit correction

The initial budget counted raw native tessellation before existing modifiers. The final audit counts evaluated native/imported meshes and actual GLB index accessors, correcting the runtime budget from13,170 to19,010 without changing geometry or mechanisms. Full native/imported geometry, state sweep, forty renders (twenty native/imported pairs) and both playable previews were regenerated and reviewed after correcting the author/verifier.
