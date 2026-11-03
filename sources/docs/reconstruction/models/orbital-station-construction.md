# Orbital station state pairs — issue 192

The user identifies the second fixed sprite descriptor of each culture's orbital station as a construction state: dense scaffolding and temporary shields. Each completed pair has two independent editable Blender files and GLB exports. `orbital-station-variants.json` explicitly maps descriptor 0 to the finished model and descriptor 1 to construction. Do not select the latest gallery study as the runtime default: the gallery also contains older studies and construction alternatives.

## BR4C SkyMech

Both correctly paletted BR4C descriptors were reviewed. Descriptor 1 has an enclosing, densely latticed envelope with temporary opaque coverage, rather than a different heading of the finished station. Source descriptors and archive hashes are bound in `braccatian-refining-baseline.json`; original pixels remain private reference evidence. Full Braccatian CDB evidence is recorded in `braccatian-lore-evidence.json`. The warm gold/rose finished structure is retained, with worn warm-metal scaffold members and dull temporary shielding.

The finished state is the independently verified expanded two-chamber core from issue 190. Its 112 meshes, geometry, UVs, corner normals and placement helpers are preserved exactly in the construction variant. The construction state adds 33 actual horizontal hoops, 24 longitudinal ribs, 768 diagonal braces, 16 body-anchored stays, three annular work decks, 16 curved shields and a small servicing carriage. Connected components are individually closed and have positive signed volume; support contacts and native/imported materials are checked. This is actual geometry, not a wireframe shader.

`ConstructionActivity` is an authored six-second loop moving only three carriage meshes by 0.30 units peak to peak along a scaffold rail. All other meshes remain static through 13 sampled poses. This suggests work without rotating the station or implying that construction progress repeats. The exact member layout, shield pattern and animation timing are interpretations; they are not recovered legacy mechanics.

Actual Blender 4.5.15 and independent GLB import verification covers 138 meshes / 975 positive closed components, finished-body preservation, helpers, support contacts, PBR channels, 13 animation poses and five paired renders. Maximum sampled position error is below 0.000002 units. Gallery playback is rendered from the actual GLB at 24 fps, 144 frames, with source-bound preview metadata. Native/imported views and the moving work detail were visually inspected against the original descriptors.

The manifest distinguishes asset runtime verification from final game calibration. In-game placement, equipment socket calibration and final artistic acceptance remain separate integration work. Other cultures are explicitly pending until their own source/lore review, refinement, runtime checks and gallery playback are complete.
