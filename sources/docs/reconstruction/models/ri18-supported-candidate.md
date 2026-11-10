# RI18 supported-dome candidate

Tracking: openfa-assets #253 and per-building #51. This continues the source audit and is not canonical delivery. RI18 stays pending; current inventory/gallery selection is not promoted.

## Focused mechanism correction

Preserve the latest existing two-half dome, cycle pivots and outer cap geometry. The prior audit confined cap/casing intersections to the upper seating interval Z1.63..1.65. The candidate lowers only casing vertices above Z1.629 to that height and updates their existing cylindrical side UV height. Lower casing, foundation, ribs, bands and angled fitting are retained. The opening family is not changed to conceal intersections.

Two compact axle assemblies are added at the actual pivot axes X±0.26, Y0, Z1.63: one axle, two bearings and two short root brackets per side. These are authored hidden-engineering interpretations, not recovered original hardware. Six cosmetic scuff sheets receive 0.0001 thickness; they are not removed or falsely counted as already closed physical solids. All 38 resulting candidate components are welded closed/positive in native and imported checks. Candidate budget is 51,788 triangles; no client performance acceptance is claimed.

`remaster_rigellian_launcher.py` reads the preserved historical source and writes one candidate Blend/GLB under `sources/objects/rigellian/missile-launcher/`. It does not modify old binaries. `model.json` records source/binary/tool hashes, edited collar vertices, added hardware and thickened cosmetic nodes. The candidate remains `canonical_delivery_ready: false`.

## Two clips, explicit interpretation

`MissileDomeCycle` retains the source's 61-frame cycle: closed at 1, open at 31, closed at 61, with opposite 110-degree rotations about the existing axes. Timing is an authored technical demonstration, not a recovered gameplay timer.

`MissileDomeDescriptorStates` provides descriptor 2..17 as one animation track using the same two leaf controls. Angles increase monotonically from closed at 2 to open at 16; 17 retains the physical open pose. This linear angle calibration is explicitly authored. Source pixels establish visible progression but do not measure actual hinge angles. Descriptor 17 lower/shadow composition remains unverified and must not be advertised as solved. Native CONSTANT lookup is exported with STEP samplers. No duplicate whole-state meshes or GLBs are produced.

## Actual candidate diagnostics

`verify_rigellian_launcher_candidate.py` reopens saved native and independently imports GLB, selecting each clip explicitly. It samples all 61 integer cycle poses and all sixteen descriptor poses. All 38 meshes are closed/positive. No cap-half surface intersections with the four previously audited fixed structures occur in these samples after the local collar correction. This does not yet classify contact with new hinge hardware or prove continuous-time solid clearance.

At all cycle samples each leaf's nearest surface remains less than 0.009806 from its axle axis point, within axle radius 0.018. This supports root proximity; it does not by itself prove all bearing/bracket seating. Five open aperture rays reach the low floor below Z0.051; full missile-volume clearance remains separate. Maximum native/import cycle matrix difference is below 0.000000597, descriptor difference below 0.000000377.

The imported descriptor NLA strip starts one frame earlier than its action domain. The verifier measures that actual offset (native 0, import 1) and samples the corresponding absolute descriptor pose. It does not alter exported keys to force agreement. Initial closed/half/open native renders were inspected. Full source geometry/map preservation and matched imported render review still remain, so these diagnostics are not a final runtime acceptance report.

## Concept feedback

Two actual built-in ImageGen requests used the real closed/intermediate/open legacy composites. Attempt 1 returned no image after output moderation; attempt 2 produced `gallery/media/concepts/rigellian/ri18-review-2.png`. Exact prompts and failure identity are retained in the candidate concept report. Broad green steps, bronze drum and two-sided dome agree. The concept adds a third front band, stronger ring divisions and extra fitting details; these are not automatically transferred.

The concept's halves are hollow shells while retained source-derived halves expose broad solid cut faces. Legacy does not establish exact inner thickness. This remains a review question: retain the outer silhouette and two-sided opening while evaluating the inner construction. New hardware wear/material review, bearings/root contacts, complete source-preservation checks, descriptor calibration, final animated galleries and client contracts still need completion.

Original pixels remain private. Shared RIS3 construction and launch entity behavior remain separate. Programme #248 remains unfinished. Reuse the existing checkout without extra build, archive or worktree; remove only verified task-owned temporary output after processes finish.
