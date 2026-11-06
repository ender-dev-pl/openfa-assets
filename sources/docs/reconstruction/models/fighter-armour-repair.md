# Assault Fighter armour cap connectivity repair (#1108)

The existing revision-3 fighter had a genuine topology defect, rather than merely a mirrored transform or an artistic proportion question. The user's authorization for obvious technical fixes permits this correction. Revision 4 reuses the existing saved model: no complete model rebuild, new wear, new textures or artistic refining. Relates to #1107, #949 and #946.

## Cause and minimal correction

The twelve armour segments were generated as extruded nonplanar quadrilaterals. Two front segments have crossed projected boundary order. Independently tessellating the upper and lower nonplanar caps also produces inconsistent surfaces and asymmetric volumes on mirrored panels. Four segments contain **70 detected nonadjacent triangle-intersection pairs**, although only one had negative total triangle volume. Flipping all normals to make the sign positive would not resolve those intersections.

`fighter_plate_topology.py` retains every original corner coordinate and plate thickness. It corrects the two crossed boundary cycles and gives upper/lower caps explicitly corresponding triangles, with consistent side winding. The existing bevel and weighted-normal modifiers remain. The same helper is wired into the builder for reproducibility, but the applied migration edits only the twelve existing mesh datablocks.

All **96 original panel vertices**, object transforms, material choices and **138 other mesh snapshots** remain unchanged. Global bounds and binary silhouettes at front-quarter, top, side and belly views are identical. The model still contains 150 meshes and seven materials. The small internal shading changes come from corrected surfaces/normals, not a redesigned ship. Original files, including earlier directional views, are preserved in the unique `artifacts/issue-1108-armour-repair/` backup recorded in `applied.json`.

## Executed verification

The actual native sources and independently imported GLB pass the original structural assertions: four recessed dorsal wells, four hollow nozzles, material count, bounds, asset marking and expected component counts. Additional checks evaluate all twelve modified panels: triangle volumes are positive, welded surfaces are closed, face areas remain nondegenerate and the tested nonadjacent self-intersections are absent. Diagnostic welds are used only on temporary imported seam-split geometry, never saved to the asset.

The originally flagged panel now has native/imported actual triangle volume **+0.0030942615**, rather than -0.0011095283. Its polygon-volume estimate agrees in sign. The old winding report is retained as baseline evidence; the current probe is source-bound to revision 4. Bevel output can still contain slightly nonplanar polygons; this is not a claim of universal planarity or global intersection-free assemblies.

Controlled regression tests reproduce the original crossed geometry from recorded vertices, confirm mirrored repaired volumes, preserve coordinates, reject an accidental second migration and reject unreviewed UV-bearing input. All pass in Blender 4.5.15 LTS. The original shared verification helpers and their contracts remain unchanged; the new source-specific verifier adds the actual-triangle/intersection contract that the old polygon-volume estimate lacked.

Six native and six matched-camera imported views were rendered, together with the existing 32 static-model camera headings: **44 checked render files**. Native/import alpha and binary silhouettes match in every paired view; maximum mean foreground RGB difference is **0.010856/255**. All images have at least 67 pixels of margin. Existing original-reference comparisons and the new before/after/import sheet were visually inspected. The direction views remain presentation samples, not operating animation or calibrated gameplay headings.

Bound evidence and the authored comparison sheet are in [`fighter-armour-repair`](../../assets/reconstruction/evidence/fighter-armour-repair/findings.json). Current canonical technical/render reports accompany the model. No original reference pixels enter geometry or textures.

## Catalogue and acceptance boundaries

The five existing catalogue/attachment audits were executed again. The complete 303-model topology report now has **zero nonpositive closed-component findings**. Open-boundary findings remain 347 meshes and require their existing assembly interpretation. The boundary containment analysis was actually rerun; counts remain unchanged. Unchanged topology measurements are retained only for the 302 byte-identical source/export bundles and the identical auditor, with explicit provenance; this source retains newly executed measurements.

UV dependencies remain clean: 698 packed/source-bound images, 1,730 required finite UV accessors. All 7,136 decoded four-input comparisons still match at their stated 8-bit precision. Hierarchy and attachment counts remain unchanged. First-source/state indexes were regenerated; all 23 unrelated Rigellian source/verifier/report bundles were proven unchanged before rebinding their inventory index. No source-specific result was invented by changing a checksum.

Actual source/import checks and the exact-file evidence bundle now support the fighter's **native_and_glb_runtime** gate, bringing accepted narrow runtime bundles from nine to ten. Comparable first-source file coverage increases from 140 to 141 because actual canonical reports are now present. This does not accept final artistic quality, exhaustive geometry validity, legacy fidelity, full states, heading/mount calibration or game integration.

The real client smoke test built with one MSBuild node and disabled shared servers/compilation, initialized, entered gameplay, rendered and closed cleanly at 1600x900. Its run is under `artifacts/issue-1108-client-smoke/faa6d348382446bd9b7e5ad601e82f56/`. This is startup regression evidence, not integration of the study GLB into gameplay. The required changed-code quality base is `44e3fd4f3`.

## Reproduction

```text
[local]/openfa-blender.ps1 -Background -PythonScript tools/blender/test_fighter_plate_topology.py
[local]/openfa-blender.ps1 -Background -PythonScript tools/blender/verify_fighter_armour_repair.py
[local]/openfa-blender.ps1 -Background -PythonScript tools/blender/render_assault_fighter_directions.py
python tools/blender/review_fighter_armour_repair.py
python tools/blender/check_fighter_armour_repair.py
python tools/blender/verify_reconstruction_inventory.py
./tools/Verify-ChangedCodeQuality.ps1 -BaseSha 44e3fd4f3
```

The migration and original in-memory proposal are guarded for the recorded baseline and must not be rerun over the corrected topology. Current regression/verifier/reviewer commands validate revision 4. Artistic refining and scaffolding remain deferred; the full reconstruction goal remains open.
