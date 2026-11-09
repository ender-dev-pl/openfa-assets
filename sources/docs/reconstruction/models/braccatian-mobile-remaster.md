# Braccatian mobile ships

Four current canonical models are under `sources/objects/braccatian/`. The inventory selects one source/export per ship for gameplay, build/ship menus and SciTek. Previous studies remain historical evidence, excluded from current packaging selection. SkyMech is an orbital station and remains outside this mobile-ship pass.

| Ship | Actual legacy sheet | Role/size interpretation | Triangles | Proposed WorldSize |
|---|---|---|---:|---:|
| Rattlesnake | BR0A.256 | Small scout, 2 equipment slots | 21,580 | 40 |
| WidowMaker | BR1C.256 | Large combat craft, 4 slots | 42,926 | 112 |
| HeartsBlood | BR2C.256 | Large transporter, 6 slots | 53,390 | 128 |
| Morning Glory | BR3A.256 | Small craft, 4 slots | 37,518 | 48 |

Size values are explicit authoring proposals for relative presentation, not recovered dimensions or changes to gameplay definitions. Existing local -Y alignment and alignment helpers are preserved. Weapon socket calibration and client scaling require integration checks. All models use four mesh batches, one material and three packed PBR maps. Named vertex groups retain the component structure inside the editable merged sources.

## Reference and visual decisions

All 32 sheet descriptors were inspected. HeartsBlood has populated even headings and empty odd descriptors. Small BR0A/BR3A sprites constrain broad form and colour rather than fine engineering. No matching BR0A/BR1C/BR2C/BR3A ship animation entries were found in the _MA archive. No operational motion is invented.

Preserved forms: the curved rose Rattlesnake with pale-gold prow; tapered ochre WidowMaker with rose nose, slate cheeks and four rear openings; the related HeartsBlood with four banded rose pods; and Morning Glory's gold spindle, broad rose terminal and opposite silver tip. Render feedback identified overly thin small-craft baselines: their transverse sections are corrected by factors 2.2 (Rattlesnake) and 1.62 (Morning Glory), preserving length. The side-view alpha aspect is checked within 15% of the observed legacy bounds. Baseline surface-deviation checks account explicitly for this intentional section correction.

Comparison cameras use an additional 180-degree azimuth for BR1C/BR2C/BR3A relative to BR0A, matching nose/aft features rather than assuming identical first headings. This camera adjustment does not change the canonical asset orientation or prove a client heading transform.

Shared materials use worn ochre brass, rose copper, slate armour and silver service metal. Sparse scratches, stains and small existing dents replace the clean prototype finish. Broad legacy colour fields remain readable. There is no dense tiled hull-panel grid. Fitted service cassettes and recessed duct stators are authored interpretation; the rear openings are not assigned an unsupported weapon/engine function. No clan emblem or glass bridge is inferred from a few pixels.

No ImageGen stage was used; the feedback loop compares actual imported GLBs directly with paletted legacy frames retained outside the repository. Original pixels are neither textures nor public gallery content. Source identities and palette hashes are recorded in the existing ship-reference index and the private reference audit.

## Verification and reproduction

Each source has model.json, runtime-verification.json and publication-preparation.json. Independent Blender checks sample baseline surfaces, validate fitted service attachment points and compare saved-source/imported world geometry and actual renders. Matching-heading and technical-wireframe images derive from the imported canonical GLB. The wireframe is a render of that geometry, not an additional model.

Generate shared maps with tools/author_braccatian_ship_maps.py. Run sources/tools/blender/remaster_braccatian_mobile_ships.py in Blender with `-- --ship <slug>`, then tools/prepare_braccatian_mobile_publication.py, followed by sources/tools/blender/verify_braccatian_mobile_remasters.py for each slug. Register with tools/register_braccatian_mobile_remasters.py, run tools/test_braccatian_mobile_remasters.py and rebuild the gallery. Regeneration requires refreshing actual runtime evidence; changing hashes alone is insufficient.

Technical verification is not final user artistic acceptance or a game/Android smoke test. No performance certification, operational animation, exact physical dimensions or recovered 3D equipment mounts are claimed.
