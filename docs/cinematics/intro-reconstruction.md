# Intro reconstruction source backup

The dedicated `feat/intro-first-sequence-reconstruction` branch preserves the editable opening cinematic through original frame 412, its earlier source checkpoints, procedural authoring scripts and restoration instructions.

Start with the [source README](../../sources/docs/assets/cinematics/intro/README.md) and [current Blender project](../../sources/docs/assets/cinematics/intro/stages/first-sequence-v8-to-frame-412/first-sequence-to-412.blend).

The project contains four native scenes and a MASTER sequencer with scene-to-scene cross dissolves. Output is 826 frames at 24 fps, 34.4167 seconds, 640×480 letterbox. The early ship uses the corrected display aspect and smoothed angular motion. Newly reconstructed terrain, rocks and mechanical feet remain inferred approximations.

The public source snapshot excludes original-game media and authoring logs, following [publication policy](../publication.md). It retains authored packed textures, geometry, animation and a traced vector logo. Optional original audio can be reattached from a locally owned installation. Do not add the original GDV, ISO, decoded screenshots or comparison movies to this branch.

Full-sequence rendering is in progress at the first backup commit. Native project recovery and representative scene rendering are verified independently; no final artistic, GLB export or game integration acceptance is implied.
