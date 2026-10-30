# Ship and equipment attachment readiness (#1115)

All 41 selected ship sources and 16 shared equipment sources were reopened in Blender 4.5.15 LTS, followed by actual import of each existing GLB. All original files in their asset directories retained their exact SHA-256 values. No geometry, source metadata, builder, export, game code, original acceptance report or ledger gate changed. Relates to #946, #949, #950 and #1112. UV repair #1111 and artistic refining remain deferred.

## Evidence and findings

The catalogue defines **145 hardpoint slots across 40 ships**; Spy Satellite has none. Nine Terran ships have **29 explicit 2D designer coordinates**. Five authored Terran models declare **23 equipment-socket candidates**:

| Model | Catalogue slots | Authored equipment socket candidates |
| --- | ---: | ---: |
| Destructor | 3 | 3 |
| Terminator | 4 | 4 |
| Fleet Battleship | 6 | 6 |
| Space Dock | 4 | 4 |
| Command Cruiser | 6 | 6 |

The metadata expressly calls these sockets `authored-uncalibrated`. Matching their count to slot capacity does not establish slot ordering, a calibrated attachment position, an equipment mating interface or acceptable assembly clearance. They remain useful existing work and should not be regenerated merely to obtain a new convention.

The other **35 ships with slots account for 122 slots**, without declared equipment-socket helpers. Four are the existing Assault Fighter, Combat Eagle, Scoutship and Transporter studies, together accounting for six slots. The remaining 31 alien definitions account for 116 slots. Their whole-model alignment markers are not per-slot mounts.

The 57 sources contain 3,001 mesh objects and **117 EMPTY helpers**, all retained on actual GLB import. Seventy-one helpers are declared under the existing metadata field `sockets`: 23 equipment candidates, seven engine helpers, 40 alignment helpers and one sensor helper. The remaining 46 helpers are placement roots. Eleven older studies have no explicit placement root: the four ships named above, Photon Cannon, Plasma Cannon and the five Shield tiers. Absence of a root is an integration-contract gap to resolve, not evidence that the original geometry should be rebuilt.

Nine shared equipment studies have an `AlignmentForward` helper and a placement root. Seven older equipment studies have neither. An orientation marker alone does not establish the physical contact point, attachment roll, mounting scale or acceptable clearance. This audit does not accept a mating interface for any of the sixteen equipment definitions.

For all 71 declared helpers, native and imported positions and normalized forward axes match their existing metadata at frame 1: **142 declaration checks passed**. The maximum position error is 1.91e-7 source units; maximum direction-component error is 3.03e-7. The native/imported helper sets, parents and custom properties match, with maximum root-frame matrix-component error 2.39e-7. Zero diagnostics means this narrow transport/declaration contract passed, not that all slot attachments are ready.

[`attachment-readiness/findings.json`](../../assets/reconstruction/evidence/attachment-readiness/findings.json) summarizes all 57 records. Per-model reports retain every helper's root-frame transform and custom properties, exact source hashes, catalogue slot/default-loadout data, authored socket declarations and native/import checks. The summary binds the current inventory, catalogue, auditor, reused hierarchy helper and inspected C# source files.

## Why the 2D mounts cannot supply 3D transforms

`ShipYardWorkspaceModel.CreateShipOptions` assigns slot indices by catalogue mount-array order and forwards each mount's X/Y into `ShipHardpointMountScene`. `LegacyManagementWorkspaceRenderer.ShipConstruction` adds blueprint-canvas and sprite offsets before drawing the mounted overlay. The inspected code therefore establishes designer sprite coordinates, not local-space 3D position, orientation, depth or physical scale. Some valid coordinates lie outside the nominal 0–127 range; do not clamp or normalize them into invented model mounts.

The current native helper names and authored metadata do not establish a verified ordered bridge from those UI slots to 3D socket nodes. Names such as `Hardpoint port` should be preserved as useful authoring evidence; alphabetical ordering would not be proof of the original slot ordering. Likewise an existing equipment surface named "mount" is not automatically an attachment transform.

## Remaining integration work

Resolve a versioned attachment contract before changing sources: stable slot-to-socket identifiers, units, handedness, full orientation including roll, and a mating frame for each equipment model. Preserve all existing geometry and source refinements. Distinguish reference-supported placement from authoring choices and retain unresolved calibration explicitly.

Given those frames, the assembly transform is `equipment_world = ship_world * socket_in_ship * inverse(mating_frame_in_equipment)`. Aligning only a forward vector leaves roll unresolved; placing the equipment origin directly on a socket assumes an unproven mating origin. Verify the actual assembled geometry with default and representative alternative loadouts, including overlap, clearance, scale, firing direction and any established motion. Runtime/game integration needs its own real-client evidence. No such assembly or acceptance is claimed by this audit.

## Reproduction and limits

```text
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/audit_attachment_readiness.py
C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/test_attachment_readiness.py
python tools/blender/check_attachment_readiness.py
./tools/Verify-ChangedCodeQuality.ps1 -BaseSha cd7513fce
```

Controlled transform tests cover a translated/rotated root, signed axes, normalization, a missing declaration target, lost custom properties, unknown axes and a singular root. The audit samples frame 1 and EMPTY helpers plus existing socket declarations; it does not search mesh geometry for hypothetical mounts, infer unregistered attachment semantics, test an assembled loadout, calibrate against a legacy camera or accept artistic quality. Scaffolding remains deferred. The read-only audit milestone is complete; attachment reconstruction and acceptance remain open.
