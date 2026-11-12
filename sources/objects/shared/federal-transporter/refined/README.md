# Refined Federal Transporter — IS0C (#215)

Dedicated shared model `openfa:federal-transporter`. This is the scheduled federal
trade vessel from `_S/IS0C.256`, not the player's PS05 Transporter. Keep
`openfa:transporter` and its source unchanged. Use this single GLB for the sky
visit, Command Centre preview and any other federal-vessel presentation.

The actual archive member was independently decoded with its embedded VGA
palette: one 320×200 canvas, occupied descriptor `(56,81,201,40)`, SHA-256
`b41dffea9e3bd39583ba2c10939bfb7540750196d574f66d6c894c9a2ae98a23`.
`reference-evidence.json` records the palette and indexed-pixel hashes. Original
pixels stay in ignored private reference files and are never used as textures.

Observed forms: three large spherical modules, a separate flattened tall stern,
an exposed aft machinery connection, a continuous horizontal spine, a slim blue
command prow, silver-grey tops, a dark blue-grey middle stripe, copper lower
sections and red stern accents. There is only one established original view;
no invented claim of a recovered turntable or operating animation is made.

The user's additional ship image guides the refinement: raised longitudinal
trusses, segmented shells, service equipment, structural bracing and worn
materials. Hidden geometry, hatch/pipe layouts, glazing, rear exhaust cavities,
fasteners and small servicing hardware are authored interpretations. The
flattened stern is a distinct machinery housing, not a fourth full-size cargo
module. The exact internal use of the spheres is not recovered from the sprite.

Source: editable named Blender meshes, actual curved plates and recessed seams,
closed truss members, seven packed portable colour maps, grime, scratches,
staining, rubbed edges and slight shallow plate dents. No material relies on
Blender-only procedural nodes at runtime. The GLB embeds all maps.

Coordinates: `FederalTransporterRoot`, unit root scale, forward **+X**, up **+Z**
in Blender. Standard glTF Y-up export applies the axis conversion. No physics,
weapons sockets, construction state or gameplay animation is invented. Motion
and arrival/departure remain the client's real federal schedule/placement logic.

Rebuild from the asset repository:

```text
blender --background --python-exit-code 1 --python sources/tools/blender/build_federal_transporter.py -- --root .
python tools/prepare_federal_publication.py
blender --background --python-exit-code 1 --python sources/tools/blender/verify_federal_transporter.py -- --root .
python tools/review_federal_pixels.py
python tools/register_federal_transporter.py
python tools/build_gallery.py
python tools/verify_project.py
```

The verifier reopens the saved native source, checks closed nonzero-volume meshes
and UVs, removes native geometry/materials, independently imports the GLB, compares
bidirectional world-space geometry and renders under the identical camera and
lights. `runtime-verification.json` binds the actual files and tools. The gallery
contains six full views, two close-ups and native/imported verification renders.
The [review sheet](../../../../../gallery/media/objects/shared/federal-transporter/refined/review.jpg)
shows all ten images. `pixel-review.json` reports the actual native/import colour
difference separately from the matching silhouettes; rendering equality is not
claimed.

This is source-asset delivery. Actual client scale, yaw, lighting, GPU rendering,
Command Centre framing and sky integration still require main-thread runtime
review. The user-provided artwork is a detail reference, not a second legacy view
or a guarantee of a pixel-identical reproduction.
