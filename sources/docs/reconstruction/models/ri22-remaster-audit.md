# RI22 Ex-Fang canonical collector/yaw verification

Tracking: openfa-assets #253/#55 and PR #254. ID `openfa:building/legacy/061`, class 40, footprint 4x4, construction updates 48. One current editable Blend/GLB is selected in `sources/objects/rigellian/ex-fang/`; historical studies remain evidence rather than additional current package payloads. Existing good geometry, wear and the manual yaw hierarchy are retained.

## Actual evidence and two concept iterations

Original ENGLISH.TXT record 922 describes energy draining while leaving the operating means uncertain. CDB Architecture record 18 guides ergonomic/elegant industrial style, not a recovered collector mechanism. Correctly paletted RI22 headings 2..17, shadow and catalogue phases 0/10/20/30/40 plus the colour/outline close-up were inspected. The raw private RI22.256 SHA256 matches the recorded reference payload, whose descriptor 1 has dimensions 0x0. Unlike RI19, each directional frame is a complete building, not a separate upper overlay on a persistent body image.

The current game selector/rules include ID061 in `2+(((heading+8)>>4)&15)`. This establishes the bank/selection rule rather than calibrated model yaw sign or phase. Catalogue reveal/highlight is not operating timing. RIS4 construction remains separate.

Two actual built-in ImageGen requests were used. Attempt 1, using four actual headings, invented an extra green plate behind the collector and was rejected. Attempt 2 used one clear actual source heading and corrected the single-dish silhouette. Exact prompts `ri22-concept-prompt-1.txt` and `-2.txt`, both generated outputs and explicit feedback are retained; only attempt 2 is the selected concept. Its additional articulated rear linkages/collars, rim details and changed base proportions remain unsupported artistic interpretation and are not copied automatically. The existing simpler support construction and shallow single collector are retained. No third request was needed.

## Native, independent GLB and rig verification

All sixteen evaluated source components are geometrically protected exactly. The model has 30,492 triangles, nine materials and eight embedded images. It retains the shallow closed collector, its thickness, three profile dents plus one collector dent, full decoded authored green/copper colour/roughness pixels, six planar caps and planar collector mapping. No reduction or unrelated material restyling is claimed.

Eleven upper mesh components and CollectorAxisSocket inherit the local +Z YawPivot. Five base meshes stay under identity PlacementRoot. Actual native and independent GLB tests retain concavity/thickness rays, feed root embedment, support/head/shell contact, yoke caps, four fittings and lower insets. One sampled contact component connects the assembly. Contact sampling is not exhaustive solid-intersection or continuous-sweep proof.

All sixteen authored yaw samples at 22.5-degree intervals check the actual feed endpoint, socket position/forward axis, all eleven moving world matrices and fixed-base invariance in both formats. Maximum moving-matrix export error is below 0.000000179; surface export error below 0.000000136; source surface preservation error is zero. Complete material-bound UV matching gives source/native 100,352 directed corners and native/import 126,172 after triangulation. UV error is zero against source and below 0.000000030 on export. Different directed counts reflect triangulation, not missing UV coverage.

Nineteen paired actual renders cover three whole-object views and every authored yaw pose. They were inspected against original views and concepts; export pixel agreement is distinct from a numerical legacy-fidelity claim. Both galleries include the selected concept, actual GLB and explicitly authored 90/180/270-degree head views. Technical diagrams derive from this same canonical geometry rather than an independently remodelled collector.

## Explicit integration limits

PlacementRoot is identity, Blender -Y forward/+Z dorsal; YawPivot rotates around local +Z. CollectorAxisSocket uses local +Z and denotes a collector-axis reference, not a proven firing origin. Exact fixed/moving division, elevation, concavity and pivot sections remain authored interpretation. Model yaw phase/sign relative to the game's heading is uncalibrated. No firing/pitch/timed operating clip, glow or invented energy effect is supplied. Bind bounds and full articulation contract are recorded in model/runtime metadata and the delivery manifest.

Client scale/placement/direction calibration, construction/damage/state integration, Android performance and final user artistic acceptance remain separate. Mesh/material counts do not establish batch consolidation or certified frame rate. Original pixels remain private.

Reproduction uses `remaster_rigellian_ex_fang.py`, `verify_remastered_rigellian_ex_fang.py` with the model recipe, and `tools/review_rigellian_ex_fang_pixels.py` with private legacy/contact-sheet paths. The public evidence binds both selected and rejected concept outputs/prompts as well as model/runtime/helper/render identities. Existing checkout reused; no new checkout/build/archive. Former mobile-ship programme #248 remains unfinished.
