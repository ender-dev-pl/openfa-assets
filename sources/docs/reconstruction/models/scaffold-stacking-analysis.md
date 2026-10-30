# Construction scaffolding: stage chaining and 3D feasibility (#983)

These are scaffolds erected during construction, as clarified by the user, rather than generic unfinished versions of each completed building. Successive descriptors represent erection stages. This distinction changes both the model family and its required state contract.

## Confirmed in the current decompile

`UpdateBuildingConstructionDescriptorFrames` at 0x449F0 derives a total stage from constructionUpdates minus the remaining counter plus one, lower-clamps it to one, and upper-clamps it by a per-building resource byte at 0xE6276 + globalType*0x14. Follow-up source extraction identifies this as byte +2 of the global building definition, and records its actual values for all 177 buildings in `scaffold-stage-limits.json`. It must not be replaced with the number of scaffold sprite frames or presumed duration.

The per-tier frame capacity is 32 shifted right by the first byte of the global building definition for Terran global types below 40. This agrees with observed PBS1..4 capacities 16/8/4/2. Other global types use capacity 2, agreeing with the two body descriptors per alien construction sheet. The routine consumes stages across a linked chain: a full lower descriptor stays at its last frame while an additional child begins at frame 1. Further stages fill that child and can create another.

`EnsureBuildingAnimationDescriptor` at 0x44990 allocates or reuses a same-resource child. New children inherit the resource and scale and begin at frame 1. The construction updater subtracts capacity*4*256*effectiveScale from the parent screen-Y field to position the child. This is 16.16 screen arithmetic: at scale 256, a full two-stage alien tier repeats 8 screen pixels upward; a full 16-stage PBS1 tier repeats 64 pixels upward. Scale byte zero means 256, not zero. These are screen distances, not recovered world heights.

`CreateAsteroidSurfaceBuildingDescriptorPair` at 0x3DB90 creates the initial descriptor-zero plus descriptor-one pair for an unfinished site. Its original resource choice uses asteroid owner and a definition byte; the current OpenFA loader's direct definition-culture mapping is not proof of every original ownership case. `UpdateAsteroidSurfaceBuildingAnimationDescriptors` at 0x450F0 invokes the construction routine while remainingUpdates is nonzero, then switches to the completed building resource and removes same-resource construction children on completion.

The analysis JSON binds the actual decompile and relevant current runtime sources. No legacy symbols or data were renamed for this analysis.

## Example, not recovered RI11 timing

For an alien scaffold with capacity two, total stages 1 through 7 give frame chains `[1]`, `[2]`, `[2,1]`, `[2,2]`, `[2,2,1]`, `[2,2,2]`, `[2,2,2,1]`. At full scale, their levels sit at screen offsets 0, -8, -16 and -24 pixels as needed. These synthetic cases demonstrate carry and stacking. They do not establish the actual RI11 stage ceiling or number of tiers.

Eight analytical tests cover carry for every observed capacity, exact multiples, repeated two-stage tiers, fixed-point offsets, scale zero/half scale, the distinct resource ceiling, decompiled signed remaining counts and lower clamping. This is a fresh-chain mathematical model of the decompile, not an execution of the original binary. Nonmonotonic progress, descriptor exhaustion and an already inconsistent chain require separate handling before runtime integration.

## Current OpenFA gap

The current sprite path in `LegacySurfaceObjectRenderer.QueueGpuConstruction` queues descriptor zero and one progress-selected body descriptor. `LegacyConstructionSpriteFrameSelector` clamps progress within one sheet; it does not return a linked stack. A successful current screenshot therefore cannot establish stacking parity. Semantic presentation overrides also require a stack-aware state contract if used for reconstruction. No application behavior is changed in this milestone.

## Can generic 3D scaffolding work?

Yes, as a family of repeatable structural modules with explicit stage states. A single fixed scaffold mesh or uniform scaling of an entire mesh cannot faithfully reproduce this contract. Nor should one scaffold shape be reused across all cultures: the decoded sources have substantially different framing, cladding and top profiles.

For each culture/footprint family, author a ground/base piece, a repeatable tier with matching bottom/top sockets, and a terminal piece. Separate stage variants determine how much of the upper active tier has been erected; completed lower tiers remain unchanged. At an exact multiple, retain one complete top tier without creating an empty extra tier. Add a new partial tier when the next stage is reached. Do not duplicate foundations, end caps or shadows at each repeated joint. Source-derived domed or clad silhouettes, especially ARS2, require culture-specific joint design rather than blindly stacking complete closed shells.

The simulation/presentation model must carry the recovered total stage/ceiling and selected tier states. A presenter converts them to family instances and attachment transforms; the renderer draws that state. The renderer must not invent progress or infer a height from the final building mesh. Scaffold height is governed by the legacy stage contract and resource ceiling, which may exceed a nominal single-tier height.

Calibrate the physical repeat pitch from the actual projection and source offsets. The recovered screen displacement is evidence for a repeat relation, not permission to equate 8 pixels with 8 world units. Preserve constant XY footprint and weld-free clean connections; use root transforms plus child sockets rather than stretching cross-braces. First validate one, two and at least three tiers in orthographic comparison renders, then validate the required range from actual per-building ceilings. Check native/imported hierarchy, socket transforms, seams, positive geometry, overlap/gaps, shadows, framing and completion cleanup. Repeat the test at minimum and maximum supported camera scales and relevant view headings.

The first practical prototype should be RIS2, shared by twelve Rigellian buildings including RI11. Its two body stages provide a small but sufficient case for partial/full upper tiers. High-detail style, material wear and source-reference comparison remain required. This analysis does not accept a new scaffold model.

## Open evidence

The stage-limit source milestone has resolved the definition-byte location/values and validated the signed-counter opcode. Continue with original owner/culture selection; calibrate screen-to-world height; investigate ARS2 descriptor zero without deleting it. Keep damage effects separate from construction scaffolds. When an object's function is unclear, read its language-pack description before interpreting its geometry.


## Follow-up: actual required stack range

See [scaffold-stage-limits-study.md](scaffold-stage-limits-study.md): RI11 requires one tier, RIS2 as a family requires up to nine, and the complete building catalogue requires up to eleven. The previously synthetic examples remain arithmetic tests, not the required-range boundary cases.
