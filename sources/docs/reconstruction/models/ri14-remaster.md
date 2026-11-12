# RI14 Energy Gatherer: canonical broad-casing refinement

Tracking: openfa-assets #253 and per-building #47. ID `openfa:building/legacy/053`, definition class 28, footprint 2x2, construction updates 46. Original functional record 914 establishes power generation while explicitly leaving the method unknown. Culture record 18 supports elegant ergonomic architecture without specifying hidden technology.

## Evidence and concept feedback

Actual correctly paletted surface body and catalogue phases 0/10/20/30/40 show two bronze lower chambers, a long pale front conduit, grey tapered connector, bronze upper vessel and upward-facing silver crown with central tip. Broad divisions read horizontally on the upper chamber and vertically on the lower. Catalogue reveal/highlight is not a camera rotation or mechanical cycle. The current directional selector excludes ID053. Shared RIS2 construction remains separate; no reactor, solar array, emission or moving machinery is invented from the functional name.

One actual built-in ImageGen request used real surface/catalogue references. Exact prompt is `ri14-concept-prompt-1.txt`; public concept is `gallery/media/concepts/rigellian/ri14-review-1.png`. It preserves the main anatomy and bronze/silver palette but thickens the conduit and rim uprights, exaggerates side fittings and changes raised casing divisions to grooves. Those changes are rejected. Exact upright count, bowl depth and hidden engineering remain interpretation. Original pixels remain private, absent from texture and mesh inputs.

## Preserve the latest casing study

The base is the latest visible-casing refinement, not the earlier study's small service panels. Three broad horizontal ribs and three long vertical ribs remain on seated backing sectors; they leave the pale conduit visible. Five mapped radial/crown components retain exact evaluated geometry, including four measurable dents, open bowl walls/floor, slender terminal and restrained authored wear. No dense decorative grid is added.

Eight casing components are reduced from 6,464 to 3,748 triangles each. Maximum sampled old/new bidirectional vertex-to-surface deviation is below 0.000000182 source units. Total cost changes from 107,788 to 86,060 triangles, with 26 editable physical components, seven materials and nine embedded images. This is a substantial cost, not Android frame-rate or batching acceptance. Any later LOD decision must retain visible ribs, contacts and silhouette.

## UV defect found and corrected

An added local-planar UV assertion exposed that geometric decimation did not preserve the casing's established face projection. Geometry/contact tests alone had passed, so that initial result was insufficient. `finish_rigellian_energy_uvs.py` reapplies the existing dominant-axis local planar projection to all eight simplified casing pieces without changing geometry, materials or source pixels. Its exact hash is bound in metadata and runtime helper evidence. The strengthened assertion checks every resulting casing face corner in both saved-native and independently imported GLB. Protected radial/crown UVs and full decoded colour/roughness maps remain unchanged. Failed private output is not used as acceptance evidence.

## Actual runtime and one current model

Select `sources/objects/rigellian/energy-gatherer/model.blend` and `model.glb` across gameplay, build menu and SciTek. Bootstrap, earlier service-panel study and visible-casing source remain historical; package only the canonical current model. Identity `PlacementRoot`, Blender local -Y forward, +Z dorsal, ground Z0. Bounds are approximately [-0.599766, -0.599766, 0] to [0.599766, 0.599766, 3.400001]. Nominal footprint is not calibrated scene placement. Static export has no clips.

Blender 4.5.15 reopened saved native and independently imported GLB after the UV correction. All 26 welded meshes are closed and positive. Retained tests cover four dents, assembly joints, bowl/floor/upright contacts, clear crown aperture above the floor at three radii, four conduit shoes and upper-vessel insets. Current casing tests retain solid backing/body and rib/backing overlap samples, rib orientation/extent and conduit visibility. A connected sampled contact graph supplements these checks without claiming exhaustive solid intersections. Original small-panel assertions are replaced specifically by the latest casing contract; unrelated body tests remain.

Full colour/roughness pixels, ten original planar-cap surfaces, cylindrical walls and the new casing planar projections pass. Native/import surface deviation is below 0.000000031 source units. Three actual view pairs were inspected: alpha and threshold silhouettes are exact, framing margins at least 53 pixels, foreground RGB mean below 0.457/255. RGB is not claimed identical. Actual GLB keeps the source-guided slender conduit and open crown rather than the concept's heavier fittings.

Hidden/rear details, exact power-generation method, operational/damage presentation, client scale/state/mount integration, performance and final user artistic approval remain separate. Unfinished mobile-ship programme #248 is not completed here.

## Reproduction and disk

Run `remaster_rigellian_static.py` with `-- --recipe sources/objects/rigellian/energy-gatherer/recipe.json`, then `finish_rigellian_energy_uvs.py`, then `verify_remastered_rigellian_static.py` with the same recipe, all through Blender with Python exit code 1. The finish step is required before verification. Inspect actual renders, register the canonical selection, rebuild galleries and run repository checks. Source-bound reports retain exact binaries, recipe, finishing tool, imported helpers and render hashes. Reuse the existing checkout without another build/archive/worktree; remove only verified task-owned temporary output after use.
