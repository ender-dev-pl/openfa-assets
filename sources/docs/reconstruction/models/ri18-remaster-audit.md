# RI18 pre-remaster mechanism audit

Tracking: openfa-assets #253 and per-building #51. This is a diagnostic milestone, not canonical delivery or an artistic acceptance. RI18 remains pending.

## Source selection and actual legacy review

ID `openfa:building/legacy/057`, definition class 14, footprint 3x3, construction updates 30. Original functional record 918 identifies missile silos. Correctly paletted surface body, every base-plus-overlay combination 2 through 17, and catalogue phases 0/10/20/30/40 were inspected. Surface progression shows a dome separating and opening to both sides. Catalogue reveal/highlight is not a turntable. Descriptor 17 additionally changes lower coloured/shadow composition and must not silently be treated as an ordinary heading or fully solved physical state.

The latest existing source is `sources/docs/assets/reconstruction/launch-facilities/rigellian/ri18/model.blend`, SHA256 `102e2f5be43bac358a3a15f3b5552e386b7b52766b0ea45f61235a8b50cc37b1`. Its GLB is `1c6ec870dafb3b661b704f3a804dfc7a11407e1d01a9d4ae46a5af2d0a75bab8`. It already splits the dome into two hinged halves. Preserve that motion family rather than reverting to the initial nominal one-piece cap or substituting a different opening mechanism to hide collisions.

Current `SelectMissileSiloLaunchFrame` maps attached-record vertical position/velocity to descriptors 2..17. Its comments describe Terran PB14-specific artwork; they do not by themselves prove Rigellian descriptor pixel semantics. The RI18 images and culture-specific mechanism evidence remain necessary. With no attached record, the selector returns closed descriptor 2. Shared RIS3 construction is separate.

## Actual saved-native and independent-import diagnostic

`audit_rigellian_launcher_source.py` reopens the existing saved Blender source without saving or modifying it, then independently imports the existing GLB. It samples all 61 integer cycle frames. Both have 28 mesh nodes and corresponding world matrices with maximum native/import difference below 0.000000597. This verifies sampled transform agreement, not complete geometry/material fidelity or continuous motion clearance.

Surface intersections between the two physical cap halves and four fixed structures occur in 40 sampled frames: 1..20 and 42..61. They involve the upper green casing. The intersecting triangle bounding intervals are confined to Z1.63..1.65 in both formats. This is a local seating/rim issue, not evidence that the whole mechanism must be redesigned. The envelope is a triangle-overlap diagnostic, not a penetration-depth or exact intersection-volume measurement. Intentional seating contact versus unwanted motion penetration remains explicitly unclassified.

At fully open frame 31, the centre and four aperture samples at radius 0.10 reach the low floor at approximately Z0.05; the centre hits a cosmetic surface at Z0.0505. This repeats and extends the earlier endpoint clearance check but does not prove clearance for a particular missile's complete volume.

Six nonclosed mesh nodes are named edge-scuff decorations, including cap and floor marks. Treat their cosmetic role separately from physical solid topology. Their signed-volume result is not meaningful for an open sheet. The two actual cap halves are closed physical solids. A canonical delivery must either retain explicitly classified cosmetic surfaces or give them appropriate thickness; it must not claim every source mesh is already a closed physical component.

Native and imported triangle-pair counts differ because export triangulates faces. The report records both; equal counts are not an acceptance criterion. No canonical model, clip/state contract or gallery selection is promoted by this audit.

## Next authoring decisions to verify

Keep the two-half dome opening. Test a focused seating/rim relief around the measured Z1.63..1.65 interval, with physically supported hinge axes, before considering larger changes. Do not use floating leaves or change the whole opening family solely to remove intersections. Preserve unaffected fixed casing, drum, angled attachment, materials and dents. Exact hidden hinge engineering and continuous timing remain authored interpretation.

Complete the artistic-concept protocol, then deliver one editable Blender/GLB with a supported mechanism and explicit descriptor lookup rather than duplicate whole-state models. Validate saved-native and independent GLB poses, maps, geometry, aperture, contacts, state mapping and sampled clearance; disclose any continuous-sweep and descriptor-17 composition limits. The current RI10 animation validator is specific to RI10 translation tracks and must not be reused unchanged for RI18 hinge rotations.

Reproduction: run this audit through Blender 4.5.15 background mode with `--python-exit-code 1 --python sources/tools/blender/audit_rigellian_launcher_source.py`. Output is the source-hash-bound `ri18-source-motion-audit.json`. Reuse the existing checkout; no additional model copy, build, archive or worktree is required. Original legacy pixels remain private. Programme #248 remains unfinished.
