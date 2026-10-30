# Scaffold body descriptor paint order (#983)

## Finding

For positive nonwrapping priorities, scaffold body descriptors dispatch **bottom-to-top (lower-first)**. Each upper descriptor has its parent's priority plus one; prepared descriptors sort in ascending priority and the raster dispatch loop visits them in that same order. The reverse-order image remains a diagnostic contrast, not an equally supported reference.

This recovers body callback order. It does not claim pixel-exact colour/shadow composition, full original application execution, or final 3D fidelity.

## Evidence chain

- `EnsureBuildingAnimationDescriptor` at 0x44990 writes child +0x14 = parent +0x14 +1 (instructions 0x449D3..0x449D7), sets frame 1 and reuses existing same-resource children.
- The actual instructions at 0x7FF91..0x7FF96 copy priority +0x14 into prepared key +0x38.
- `PrepareDirtyImageRenderCommands` at 0x7FE2E inserts descriptors by ascending unsigned prepared key. The compare/branch at 0x7FFC3/0x7FFC6 and insertion walk at 0x80000/0x80003 establish the direction.
- `RasterizePreparedImageRenderCommands` at 0x804A5 follows the prepared +0x28 linked list and calls each type-specific callback at 0x8066D; advancing at 0x80670 retains ascending order.

`probe_scaffold_composition.py` reconstructs the installed original LE image and executes these original instruction regions in Unicorn. Five child-chain fixtures cover one, two, three, nine and eleven levels; input insertion order is deliberately reversed. A sixth fixture uses mixed keys [103,100,102,101]. Both prepared order and actual callback order are [100,101,102,103] for that case. The eleven-level fixture spans the current catalogue maximum. Existing same-resource children are explicitly reused without another allocation.

The JSON binds original executable, reconstructed memory and probe hashes, records every fixture's keys and substituted helper addresses, and keeps final acceptance false. The main inventory verifier reruns the actual instruction fixtures and compares this evidence, rather than accepting a status label alone. Four regression tests check maximum-tier chaining, dispatch order, mixed insertion order and the limited pixel-execution scope.

## Controlled substitutions and limits

Fixture globals deliberately occupy the raw data-relative locations expected by the unrelocated code. This is not a fully relocated executable or running game. The original child helper executes, but its allocator call at 0x72393 returns controlled empty descriptors. The raster loop executes, while cache-release and clipping/dirty-region helpers are substituted where invoked. Fixture sprite callbacks record their keys instead of rasterizing pixels. Executed child/order/dispatch instruction regions are not patched; the probe checks the core order/dispatch regions against original bytes after execution.

Distinct positive keys avoid unsigned wrap and equal-key ambiguities. Original ownership/visibility decisions, arbitrary image flags, palette remapping, shadow ramps, clipping correctness, allocator exhaustion and complete pixel composition remain outside this result. No Ghidra symbol was renamed and no DOSBox was launched.

## Consequence for the 3D study

The RIS2 reviewer now labels the lower-first stack as recovered body order and the upper-first stack as a reverse-order diagnostic. It binds this evidence into the render report. Existing Blend/GLB geometry and its native/imported verification are unchanged by this analytical milestone.

Reference-mask occupancy is also measured to guide the next geometric refinement. Each source body stack is cropped to alpha bounds; authored alpha is cropped to its threshold-128 bounds, BOX-resized to the source dimensions, then thresholded at 128. This is diagnostic coverage, not mask-fidelity acceptance or a physical-volume measure. In stage 2, the original covers about 64% of its body bounds while the authored lattice covers about 47%. In stage 17, the proportions are about 87% versus 72%. Stage 1 is about 59% versus 34%.

Thus a denser source appearance remains under the recovered ordering. The open 3D framework still needs reference-driven cross-section/tie or cladding analysis and refinement. Colour/material differences also remain; a successful ordering probe does not accept those omissions. Inspect the reference-only `artifacts/shared-construction-reference-study/RIS2/stack-comparison.png` alongside the original descriptors before adding structural details. Exact hidden construction must remain labelled inference.
