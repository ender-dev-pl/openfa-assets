# Mikotaj mobile ships

Canonical editable sources and GLBs are in sources/objects/mikotaj/<slug>/. The inventory selects exactly one current model per ship for gameplay, ship/build menus and SciTek. Previous studies remain historical evidence outside current packaging selection. Na-Xanth is an orbital station and is outside this pass.

| Ship | Legacy sheet | Role | Equipment slots | Triangles | Proposed WorldSize |
|---|---|---|---:|---:|---:|
| Hiero | MK0A.256 | Small scout | 2 | 31,188 | 40 |
| Ylikt-shan | MK1A.256 | Small craft | 2 | 26,672 | 48 |
| Falari-Lourn | MK2C.256 | Large combat craft | 5 | 34,934 | 112 |
| Ruth-Strivakh | MK3C.256 | Large transporter | 2 | 52,162 | 128 |

WorldSize values are size-class proposals, not recovered dimensions or changes to gameplay definitions. Alignment helpers and local -Y convention are retained; final client scale, heading and weapon mounts need runtime calibration. Each model uses four batches, one material and three packed PBR maps. Named vertex groups preserve component identities in the editable sources.

## Legacy and design decisions

All 32 sheet descriptors per ship were reviewed; Ruth-Strivakh uses populated even headings. No matching MK0A/MK1A/MK2C/MK3C mobile-ship animation entries were found in the _MA archive. No operational animation was invented. Original pixels remain outside the repository and are not used as textures.

Keep Hiero's faceted body, four fins and axial spike; Ylikt-shan's separate rails and central bridge; Falari-Lourn's continuous pointed green wing and blue central shell; and Ruth-Strivakh's open copper frame, end pods and central blue shell. Render feedback identified overly tall large-craft baseline shells: Falari-Lourn and Ruth-Strivakh are lowered in Z by factor 0.55 while preserving their planforms and open spaces. Surface-deviation checks account explicitly for this intentional correction.

The palette remains opaque slate blue, green metal, copper structure, dulled gold fixtures and silver service alloy. Home-world crystal architecture does not establish transparent spacecraft. Wear adds isolated scratches, small stains and existing dents without a dense panel grid. New underside cassettes, seated structural pins and internal frame braces are authored interpretation; they do not establish recovered mechanisms, weapons or thrust directions.

Comparison-camera elevation is explicitly an estimate for each sheet. Ruth-Strivakh's crosswise beam also requires a 90-degree comparison-camera azimuth adjustment relative to the longitudinal craft. These render settings do not establish a client heading transform or alter the canonical orientation. Matching-side aspect checks are a coarse diagnostic, not a claim of pixel-level or percentage artistic fidelity.

No ImageGen stage was used. Actual imported GLB renders are compared directly with paletted legacy frames retained privately. Wireframe images derive from exactly the same GLB geometry and do not create another model.

## Verification and reproduction

Each model includes source-bound model.json, runtime-verification.json and metadata-only publication-preparation.json. Blender checks sample earlier surfaces with declared Z correction, check fitted detail attachment points, compare saved-source/imported geometry and render both formats. Focused tests check PBR embedding, primitive counts, matching-view aspect and one current inventory selection per ship.

Generate maps with tools/author_mikotaj_ship_maps.py. Run sources/tools/blender/remaster_mikotaj_mobile_ships.py in Blender with `-- --ship <slug>`, then tools/prepare_mikotaj_mobile_publication.py and sources/tools/blender/verify_mikotaj_mobile_remasters.py per ship. Register, run tools/test_mikotaj_mobile_remasters.py and rebuild both galleries. Geometry/UV/material primitives are reused from the prior Braccatian remaster; their source hash is checked independently. New colours, details, size proposals and shape corrections are Mikotaj-specific.

Native/GLB verification does not establish final user artistic acceptance, calibrated equipment mounts, game/Android scaling, operational behaviour or device performance certification.
