# Catalogue topology audit (#1107)

Actual evaluated native and independent GLB topology was inspected for all 303 current last-present sources: 177 buildings, 41 ships, 16 hardpoints and 69 missiles, totaling 10,727 asset meshes in each representation. All object identities match. Explicit `preview_only` geometry is excluded. No source was saved, exported, repaired or regenerated.

`audit_catalogue_topology.py` ran in Blender 4.5.15 LTS, selecting native frame 1 and imported start frame 0. It measures raw and diagnostic-only world-space 1e-6 welded topology: boundary/loose edges and vertices, edge fans, face areas, connected components and triangle-based signed volume. All source Blend/GLB hashes were checked unchanged. Full 303 marker set and final success marker, exit zero. Welding occurs only in temporary BMesh diagnostics and is not an asset repair.

## Results and interpretation

No loose edges/vertices, greater-than-two-face edge fans or faces below the 1e-12 zero/1e-10 tiny area thresholds were found after diagnostic welding. Flag sets agree between native and imported representations for all 303 definitions.

347 meshes have remaining open boundaries, affecting 73 building definitions and three ship definitions together with the armour concern below (76 flagged definitions total). These include collars, pipe ends and exhaust details. Open boundaries are findings requiring assembly/function classification, not automatically 347 invalid assets. Embedded open ends can be legitimate render construction; this audit does not inspect every endpoint's coverage by adjacent geometry.

The original pass found one closed component with nonpositive triangle volume: Assault Fighter's `Swept tessellated wing armour`. The [authorized #1108 correction](fighter-armour-repair.md) now resolves its cap connectivity and the related panel self-intersections. The current complete audit has zero nonpositive closed-component findings. This does not establish absence of self-intersections in every other positive-volume mesh.

Raw imported boundaries occur on 10,678 meshes, compared with 774 native meshes. Current diagnostic welding merges 2,669,577 imported and 25,603 native vertices. These counts show why raw seam splits must not be declared topology failures. Per-object raw/welded values are retained, so weld-induced changes remain reviewable. The fixed tolerance can merge very close distinct features and does not prove continuous geometric equivalence or final manifold acceptance.

## Assault Fighter follow-up

The original independent probe excluded a mirrored transform (determinant +0.82999998): polygon-based BMesh volume was +0.0006896415 local, while actual Mesh triangle volume was -0.0011095283 and maximum face nonplanarity was 0.06966354. Those baseline measurements are preserved under `fighter-armour-repair/baseline-winding.json`.

After the user authorized obvious technical fixes, #1108 corrected the twelve armour panels' cap connectivity while preserving their original vertices and the other 138 meshes. Four panels had detected self-intersections despite only one failing the signed-volume diagnostic. The current independent probe measures native and imported actual triangle volume +0.0030942615 for the originally flagged panel, agreeing in sign with polygon volume. Bevel-generated faces retain small nonplanarity (native maximum 0.00019296); the correction does not pretend that every bevel polygon is mathematically planar. Actual panel triangles are closed, positive-volume and free of the tested nonadjacent intersections. The shape/silhouette and remaining final-art boundaries are documented separately.

## Reproducibility and scope

Evidence: `docs/assets/reconstruction/evidence/catalogue-topology/`. `check_catalogue_topology_evidence.py` checks all current selected source/report hashes and produces explicit per-definition findings, without executing Blender itself. Evidence is exact-byte scoped to this checkout. The controlled Blender test `test_catalogue_topology_metrics.py` passed closed cube, rotated/reversed winding, export-style separate corner vertices with diagnostic weld, open plane and loose-edge cases, exit zero. The targeted winding probe also completed with success marker and exit zero.

This audit does not prove global self-intersection absence, exhaustive planarity, all operating/damage/animation states, UV/material quality, legacy visual fidelity, calibrated mounts or game integration. The original #1107 milestone promoted no gate; the later source-specific #1108 verification accepts only the corrected fighter's narrow native/GLB runtime gate. Artistic refining and construction scaffolding remain deferred; obvious technical corrections are explicitly authorized. Original quality base: `f1a49767`; repair quality base: `44e3fd4f3`.
