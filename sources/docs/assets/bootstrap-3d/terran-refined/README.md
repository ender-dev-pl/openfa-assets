# Refined Terran building studies

Higher-detail, independently authored variants of PB00–PB39. `index.html` shows
the previous catalogue beside each refined model. The prior models remain in
`../full-catalogue/terran/` as the reproducible comparison baseline.

The detail pass adds actual manufactured geometry, not just larger renders:
individually separated hull plates, recessed glazing, pressure seals, equipment
access, cooling grilles, structural connections and building-specific machinery.
Generic protruding window blocks are removed. Material variation uses native PBR
materials; neither original image pixels nor original meshes are imported.

PB rotation reference sheets and the individual correctly paletted frames from
#943 inform the silhouettes and visible equipment. Hidden mechanics and new
construction details are authored interpretations, not recovered original models.
The five earlier basic-building studies remain the base for their own variants.

Each directory contains editable Blend and standalone GLB, three transparent
768px views, and metadata recording the base hash, new features and geometry
counts. Directional variants preserve the fixed base and heading pivot, include
16 fixed-camera views and a looped Blend/GLB rotation preview. New head equipment
is attached to the moving assembly, while base equipment stays fixed.

```powershell
& C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/build_refined_terran.py -ScriptArguments @('--resume')
& C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/refine_screen_generator.py
& C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/refine_radiation_filter.py
& C:/tools/blender/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_refined_terran.py
python tools/blender/review_refined_terran.py
```

Use `--ids 0,7,8,17` on these scripts for the representative review set. Resume
checks authoring-code and base-Blend hashes. The verifier checks geometry growth,
asset metadata, lack of external image dependencies, and actual fixed-base and
head movement before and after GLB import. Image review checks alpha and bounds.

These are source art variants. Palette mapping, split runtime sprite layers,
construction stages and gameplay registration remain separate integration work.

## Missile silo iris dome

PB14 uses articulated overlapping curved leaves, not a solid lid with radial
panel lines. The legacy surface overlay sequence (frames 2–14) confirms a central
aperture opening over the persistent launch-well base. Eight leaves, rim pivots
and the concealed retraction mechanism are independently authored interpretations;
the reference does not establish their exact mechanical geometry or leaf count.

Each leaf is a rigid mesh with its own pivot and rotation/vertical retraction
channels. The timeline runs closed (1), lowered (5), open (17), lowered/closed
(29), closed (33). The GLB exports the complete scene animation. `iris/00.png`
through `16.png` and `iris.gif` show opening and closing with a fixed camera.
The verifier ray-casts through the centre: a leaf must block it when closed,
and the launch-well floor must be visible when open, including after GLB import.

PB10's final emitter pass replaces the earlier wire proxies with three full,
flat-shaded faceted crystals: polished native PBR surfaces, emissive cores,
insulated sockets and short energy-corona arcs. These are force-field emitters,
not photovoltaic panels. Their shape follows the user-confirmed reference;
individual facets and concealed mounting hardware are authored details.

Rotation frames 0/15/30/45 confirm that the side crystal assemblies lean outwards
and that the three PB05 intake mouths face different directions. The final
passes tilt each complete crystal assembly at its socket, and replace the filter
with three hollow swept pipes and rounded divergent elbows. Crystal inclinations
(-22/-4/+22 degrees) and intake headings (210/330/90 degrees) are authored
approximations of the visible arrangement. The verifier checks real hollow wall
thickness, divergent mouth positions and the crystal mounting inclinations.
