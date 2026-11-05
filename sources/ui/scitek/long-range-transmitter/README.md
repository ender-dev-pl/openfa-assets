# Sci-Tek Long Range Transmitter — research 34

Authored reconstruction based on the correctly paletted ST34.256 tile, all 60 colour frames, the 423-frame information film and all three caption anchor groups. Original pixels are private reference evidence and are not textures in this model.

The faceted tan console includes an angled dark display, three red/green/blue controls, paired cartridge drives, a right-hand encryption assembly, three physical rear ventilation slots, end markings and coloured service loops. New hardware has 20 geometric wear marks plus Blender procedural abrasion. The GLB retains geometric wear and portable material colours; procedural abrasion is not baked. Green display glyphs are authored static geometry, not a transcription of source text or a claim of independent screen scrolling. The meaning of the blue end emblem is unconfirmed.

Use long-range-transmitter.blend or .glb for the colour presentation, root TransmitterRotor at unit scale. The preview is 60 frames at 15 fps, with closure at frame 61. Use the exact solid_preview_camera and solid_framing metadata: framing has been checked across the whole rotation. Tile assets use a 144×160 canvas and legacy drawn box (5,41)..(138,123), with contain scaling and preserved proportions.

The separate information Blend/GLB and information-timeline.json provide all 423 frames at 15 fps. Apply the timeline root rotation by replacement, camera pose, orthographic scale and highlight material selection. Material colour and orthographic scale cannot be assumed to survive glTF animation. Whole information orientation differs from the tile orientation, matching the inspected source's opposite-end view. Pose interpolation and camera reconstruction remain authored approximations.

Four technical roles: chassis, audio-visual-console, data-cartridge-drives and data-encryption-device. Caption intervals are respectively 29..139, 170..280 and 311..421 (zero based). Captions come from ENGLISH.TXT records 1451..1453. Non-selected groups remain green; the selected group turns red. Solid glyphs, wear and small fasteners are excluded from technical variants.

Validation covers closed hardware topology, capped curves, role membership, all 60 projected bounds, loop closure, five solid/wire/highlight native/imported comparisons, three independent colour animation poses, complete information rendering, five independent information imports, saved-scene reload, caption selection and film decoding. Coarse source-frame occupancy comparisons are not pixel-exact fidelity evidence. Actual OpenFA integration and GPU acceptance remain the main game thread's responsibility.


## Independent source material and caption clocks

The corrected information presentation uses material-clock.json rather than treating text visibility as red selection. All 423 source red activity states match: 336 red frames and 333 caption-visible frames. Lead-in flashes, green interruptions during captions and the final red encryption-device hold are retained. Caption timing remains 29..139, 170..280 and 311..421; these intervals do not define the highlight state.

Source-reviewed component transitions are decoded updates 0, 65 and 130 (timeline frames 0, 141 and 282). Source images at the adjacent red states verify console, cartridge-drive and encryption-device identity; hashes and provenance are recorded in the clock file. The original-clock audit measures only red presence, so this separate semantic boundary review is required.

The client must consume highlight_component for material hue and caption_component for text visibility independently. Use step transitions for hue; do not interpolate the red/green state. Every saved-scene frame and half-frame flash transition was checked. Full renders were compared with the source on/off clock at all 423 frames; 19 independent GLB samples cover every previous mismatch and the original closeup anchors. Camera/geometry remain authored approximations.

The information WebM uses VP9 Profile 1 lossless RGB (gbrp): all decoded RGB frames match native renders exactly. Chroma-subsampled 4:2:0 encoding lost a tiny red fragment and is not used for this film.

All four exported information materials explicitly declare KHR_materials_unlit. Apply timeline hue to unlit technical lines; a black PBR base plus emission does not preserve the native edge response of tiny red fragments. Independent import checks reconstruct the same pure emission graph as the native scene.

Run verify_information.py OUTPUT [MATERIAL_CLOCK_FILE] with Pillow/FFmpeg and access to the registered global material-clock audit. Run verify_material_state.py -- OUTPUT MATERIAL_CLOCK_FILE in Blender before movie verification. The default clock path is alongside the verification script. The static model, colour turntable and other geometry variants are unchanged by this correction.
