# Cinematic surface/light iteration 2

This independent B/C/D excerpt preserves the previous pass and original opening scene. `cinematic-v2.blend` contains an editable 24 fps sequencer spanning native frames 329–826 (original 164–412), with the preserved B/C and C/D dissolves. Source shots render at 1920×786 into a 1920×1440 letterbox master.

The materials replace high-contrast terrain camouflage with layered object-space noise, fine mineral relief and roughness appropriate to basalt. Cold grazing sunlight and broad bounce produce readable cliff shadows; warm base spill and a footprint edge light separate the metalwork. Raycast-seated geometric fragments add real contact shadows. Metal panels retain fine machining marks and weathering. All textures are procedural, authored shader networks rather than legacy image projections or downloaded photographs.

Run `build.py --input PREVIOUS_FULL_PROJECT --out WORK_PROJECT` in Blender 4.5 LTS to rebuild from the preceding refining checkpoint. `render_stills.py --frame 272 --out /path/to/frame.png --samples 32` renders the loaded project in HD. Native production settings retain 128 samples; published stills use 32 samples and denoising. Full-resolution moving video is not included in this iteration.

Standalone B/C natives and static GLBs are supplied. `verify_scene.py` reopens the editable shot and independently imports the GLB to compare evaluated world geometry. Procedural shader baking, animation export and real-time integration remain deferred. Material appearance is assessed from actual Cycles renders, not GLB geometry checks.

`lighting-checkpoint.blend` preserves the exact native used for the two surface stills. The final `cinematic-v2.blend` differs only by smoothed rock normals in B; its own asteroid still is rendered again. Each HD still has a native SHA256 journal so that render provenance remains explicit.
