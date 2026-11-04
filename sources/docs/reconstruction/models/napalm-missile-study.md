# Napalm missile reconstruction study

Tracking: #960; relates to #951 and #946. References: #958 and `missile-reference-index.json`, PM02 management preview plus runtime frames 0, 3, 6 and 9. No original pixels or meshes enter the authored source.

## Observed form

The management preview shows a separate copper/red pear-shaped head above an exposed pale neck with red supports, amber feed equipment, tapered red reservoir forms and gray angular lower shrouds. The runtime frames support a broad gray lower region, red upper body and small amber feature, but their tiny pixel count does not resolve hidden shroud counts or establish a turntable. This is a distinct construction rather than a recolored PM00/PM01 cylinder.

## Actual render iteration

Revision 1 supplied a lofted head, genuinely open neck, independently shaped tapered reservoirs, thick sector shrouds, hollow cup and nozzle. Comparison against the management preview and four runtime frames found lower gray coverage too short, gray/copper surfaces too light and the amber feed hidden by a reservoir.

Revision 2 extends the shrouds, darkens the intended body and head materials, exposes the feed bottle and line, seats head seam rings into their casing and adds an annular lower reservoir support. The ring supports the reservoir bases without obstructing the propulsion axis. Six transparent views were regenerated and front/oblique/nozzle renders reviewed again. The head/neck/body separation, tapered red forms and angular gray coverage remain readable without extra decorative geometry hiding the main structure.

## Interpretation and pending fidelity

Three reservoirs and three shroud sectors are authored hidden-side interpretations from one management perspective. Exact dimensions, retaining rings, fasteners, lower reservoir support and nozzle interior are inferred construction. Materials reproduce the visible color regions with new shaders, not sampled legacy textures. The reference contains more irregular subtle shading than these clean manufactured surfaces; it does not prove mechanisms or deployable panels. No shroud animation or independently moving nose is invented.

Nose axis is +Z, front is -Y, dimensions are uncalibrated authored units. Weapon/missile socket transforms, gameplay axes, exact scale and final artistic acceptance remain open. This study is not a completed catalogue asset under the programme acceptance ledger.

## Deliverables and checks

Editable named meshes and an asset collection are saved in `docs/assets/reconstruction/missiles/terran/napalm/model.blend`; standalone GLB and six views plus gallery/provenance/review JSON sit alongside it. The reference comparison sheet is regenerated under ignored `artifacts/missile-reference-study/napalm-comparison.png` by `review_terran_missiles.py --ids napalm`.

Run `build_napalm_missile.py` and `verify_napalm_missile.py` through Blender. Native reopen and GLB import checks examine actual topology, positive closed volumes, materials/bounds, side-neck empty spaces, all three 0.085-unit shroud walls, annular support under the reservoir bases, and the complete open nozzle axis to the recessed throat. No external image dependencies or animation are present. Run reconstruction inventory regeneration/verification and Python compilation as well as the repository changed-code-quality gate. No game renderer or gameplay registration changes are part of this milestone; Blender generation/reopen/import is the exercised target runtime.
