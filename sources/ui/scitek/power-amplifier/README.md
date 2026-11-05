# Sci-Tek Power Amplifier

Dedicated research presentation for ST20 / research20. Actual colour tile,60-frame colour rotation and all three information-caption studies establish a slender warm-alloy chamber, three collars, an upper U-ended service opening, vapour-generator controls, shallow distorted top reflector and two lower optical couplings. Original pixels remain private evidence and are not textures. Exact hidden internals, topology and camera transforms were not recovered.

The opening is physically cut through a closed hollow shell. Six vertical control blocks, a large dial, smaller indicators, lower slits and two upper indicators form the source-labelled generator; the backing/opening stay in chassis. A slightly warped reflective plate forms the reflector; the enclosing cap and support tabs stay green. Both oval optical gaskets/lenses are selected together. Their physical detailing and shallow reflector distortion are authored interpretations. The original colour preview shows whole-device rotation; internal vapour behaviour is not reconstructed by this asset.

New casing has procedural abrasion, dark joints and27 small explicit scuff meshes retained in GLB. Portable PBR retains these meshes, colours and metal/roughness properties; Blender procedural noise is not baked to textures. Fine rivets and wear details are excluded from technical display-wire LOD.

Solid:60 frames at15fps, negative-Z revolution of AmplifierRotor, scale[1.04,1,1], loop closes at Blender61. Component bind matrices already include a-30-degree orientation placing the panel and ports on the observed side. Root starts at zero; preserve these mesh/node bind transforms. The metadata solid_preview_camera records actual saved framing. Registered native/disabled144x160 and4x576x640 tiles contain the model inside measured ST20 box(47,7)..(97,153) without stretching.

Information:423 frames/15fps, four named wire groups. Ethereal-vapour-generator29..139, distorted-reflector170..280 and optical-coupling-ports311..421. Reflector is shown axially from above; generator and paired optical ports receive their own settled closeups. Separate information GLB/Blend and explicit information-timeline.json carry XYZ Root pose, camera, ortho scale and highlighted component. Initial information pitch12 degrees must be replaced by evaluated timeline pose. Apply explicit component hue and ortho scale; these channels are not portable glTF animation. Camera interpolation is authored from observed order/anchors, not recovered original camera data.

Bind scitek:power-amplifier / openfa:presentation/profile/research/20. Paths in gallery/media/ui/scitek/integration.json. Verification covers closed geometry, ray-cast opening, three collars/paired ports/reflector ownership, retained27 scuff nodes, cycle closure, all five native/imported static variants, independent solid cardinal poses, three source-bound information framing comparisons, full423-frame information/import/reload checks and complete video decoding. Game integration and GPU acceptance remain with the main thread.

Build: Blender -b -t 4 --python-exit-code 1 --python build_amplifier.py -- OUTPUT. Run render_preview.py / animate_information.py with INPUT_BLEND OUTPUT while preserving model.json. --keyframes-only is a review subset, not a full deliverable. Geometry/preview-pose/information-state checks run in Blender; device/raster/information/framing checks use Python/Pillow/FFmpeg. Raster checks expect sibling amplifier-preview-poses. Information validation needs saved-source frame88 reload-0088.png; framing validation takes the private original-codec ST20 directory. Outputs belong outside sources.


## Independent source material and caption clocks

The corrected information presentation uses material-clock.json rather than treating text visibility as red selection. All 423 source red activity states match: 336 red frames and 333 caption-visible frames. Lead-in flashes, green interruptions during captions and the final red coupling-port hold are retained. Caption timing remains 29..139, 170..280 and 311..421; these intervals do not define the highlight state.

Source-reviewed component transitions are decoded updates 0, 65 and 130 (timeline frames 0, 141 and 282). Source images at the adjacent red states verify vapour-generator, reflector and coupling-port identity; hashes and provenance are recorded in the clock file. The original-clock audit measures only red presence, so this separate semantic boundary review is required.

The client must consume highlight_component for material hue and caption_component for text visibility independently. Use step transitions for hue; do not interpolate the red/green state. Every saved-scene frame and half-frame flash transition was checked. Full renders were compared with the source on/off clock at all 423 frames; 19 independent GLB samples cover every previous mismatch and the original closeup anchors. Camera/geometry remain authored approximations.

The information WebM uses VP9 Profile 1 lossless RGB (gbrp): all decoded RGB frames match native renders exactly. Lossless RGB avoids chroma-subsampling artifacts on tiny coloured lines.

The information sequence uses 64 Cycles samples. Four-sample rendering lost a source-visible subpixel reflector fragment at frame 266; controlled 16/64-sample probes retained it without changing geometry, line width or camera. Antialiasing therefore changes pixels beyond the fifteen hue-clock discrepancy frames.

All four exported information materials explicitly declare KHR_materials_unlit. Apply timeline hue to unlit technical lines; a black PBR base plus emission does not preserve the native edge response of tiny red fragments. Independent import checks reconstruct the same pure emission graph as the native scene.

Run verify_subpixel_import.py -- OUTPUT in Blender after the full render to reproduce the frame266 import regression check.

Run verify_information.py OUTPUT [MATERIAL_CLOCK_FILE] with Pillow/FFmpeg and access to the registered global material-clock audit. Run verify_material_state.py -- OUTPUT MATERIAL_CLOCK_FILE in Blender before movie verification. The default clock path is alongside the verification script. The static model, colour turntable and other geometry variants are unchanged by this correction.
