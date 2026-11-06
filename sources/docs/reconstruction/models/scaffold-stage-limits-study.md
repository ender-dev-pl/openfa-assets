# Original per-building scaffold stage limits (#983)

## Source and validation

`index_scaffold_stage_limits.py` reconstructs the installed FRAGILE.LE through the existing LE object/page reader into ignored research output. Its memory image matches the permanent decompilation memory image byte-for-byte (SHA-256 `3aa6bc162e0233933a16d0204e68ea333bbc044beb9924b9df3ecfd1f582e23b`). Original executable, memory, generator, source tables and decompile hashes are recorded in `scaffold-stage-limits.json`.

The ceiling consumed by 0x449F0 is byte +2 of the 20-byte building definition at `0xE6274 + globalType*0x14`, hence `0xE6276 + globalType*0x14`. It is not an unlocated field of the 12-byte resource loader record. This identifies its construction-stage role; no broader physical-height semantic label is assigned to the legacy field.

The generator validates the raw table's width/height/class against every catalogue definition and the construction-duration byte at `0xB9FD1 + globalType*6` against all 177 catalogue durations. Original instruction bytes at 0x44A0A/0x44A53 confirm the ceiling/width reads, while `0F BE 49 0A` at 0x44A27 confirms sign extension of the remaining counter. Raw LE operands retain data-object-relative addresses 0x36276/0x36274; the data object's base is 0xB0000. The flattened image is suitable for data reads but has not thereby become a fully relocated executable for direct emulation. No DOSBox was run and no Ghidra symbols were renamed.

## Required ranges

All 177 ceilings are positive and no ceiling exceeds its catalogue construction duration. With ordinary active remainingUpdates in 1..duration, each ceiling is therefore reachable before completion; remainingUpdates=0 takes the completed-building branch. Of 177 definitions, **155 require more than one scaffold tier**, while 22 fit in one. The maximum is **11 tiers**.

RI11 Probe Launch has ceiling 2, capacity 2 and maximum chain `[2]`: it needs no stack. Databanks (global 47), using the same RIS2 family, has ceiling 17 and maximum chain `[2,2,2,2,2,2,2,2,1]`: nine levels including the partial top. The current RIS2 prototype's stage-6 three-tier case is therefore insufficient as evidence for the family's required range. The tallest observed definition is Elite Block (global 136), ceiling 22 and eleven complete two-stage tiers in MNS3.

| Family | Dependent buildings | Maximum required stage | Maximum required tiers |
| --- | ---: | ---: | ---: |
| PBS1 | 2 | 18 | 2 |
| PBS2 | 28 | 14 | 2 |
| PBS3 | 8 | 9 | 3 |
| PBS4 | 2 | 4 | 2 |
| RIS1 | 0 | 0 | 0 |
| RIS2 | 12 | 17 | 9 |
| RIS3 | 9 | 20 | 10 |
| RIS4 | 2 | 8 | 4 |
| BRS1 | 0 | 0 | 0 |
| BRS2 | 13 | 18 | 9 |
| BRS3 | 10 | 16 | 8 |
| BRS4 | 0 | 0 | 0 |
| MKS1 | 0 | 0 | 0 |
| MKS2 | 13 | 17 | 9 |
| MKS3 | 8 | 13 | 7 |
| MKS4 | 0 | 0 | 0 |
| ARS1 | 0 | 0 | 0 |
| ARS2 | 12 | 18 | 9 |
| ARS3 | 10 | 10 | 5 |
| ARS4 | 1 | 5 | 3 |
| MNS1 | 0 | 0 | 0 |
| MNS2 | 11 | 20 | 10 |
| MNS3 | 8 | 22 | 11 |
| MNS4 | 2 | 17 | 9 |
| ACS1 | 0 | 0 | 0 |
| ACS2 | 17 | 18 | 9 |
| ACS3 | 9 | 17 | 9 |
| ACS4 | 0 | 0 | 0 |

Zero entries mean an installed family has no current catalogue dependency; they do not establish an empty source or an invalid scaffold family. Terran capacities 16/8/4/2 and alien capacity 2 are kept distinct. Number of descriptors, duration and stage ceiling are separate values.

## Integration and limits

Every building in the generated reconstruction inventory now links its exact ceiling, capacity, maximum stage and maximum tier count to this source index. Verification reconstructs and rereads the original data and validates the linked values. Family limits drive the next modelling/validation cases; they do not accept physical pitch, silhouette, mechanisms or application integration.

Six source integration tests check all 177 global identities, the RI11/Databanks same-family contrast, the actual eleven-tier maximum, independence from duration, family coverage and signed-counter opcode evidence. The eight earlier arithmetic tests remain applicable.

Original owner-based family selection, malformed/nonmonotonic state handling, resource-allocation exhaustion and physical world-height calibration remain unresolved. Existing stacks and source examples are descriptor requirements; do not infer height from the final building mesh. In particular, stage limit discovery does not validate the prototype's provisional pitch.

This is an analytical milestone. No application or model runtime changed. See `rigellian-scaffold-study.md` for the existing prototype and its outstanding range/calibration/artwork work.

## RIS2 range coverage follow-up

The revision-2 RIS2 prototype now exports all source-required stages 1..17, including eight full levels at stage 16 and a partial ninth level at stage 17. This supersedes the earlier stage-6 boundary limitation above. The new coverage and GLB instance-preservation tests do not accept artwork or calibrate physical pitch.
