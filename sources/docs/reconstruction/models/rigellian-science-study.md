# Rigellian Science Labs RI07

Tracked in [#977](https://github.com/ender-dev-pl/ed-openfa-game/issues/977), relates to #948/#946 and reference milestone #970.

The independently authored editable Blend, embedded-texture GLB, authored-only gallery, maps and review reports are in `docs/assets/reconstruction/buildings/rigellian/science-labs/`. Preserve `openfa:building/legacy/046`, global type 46, definition class 255 and nominal 3x3 footprint. `PlacementRoot` is identity at ground Z=0. Previous models remain intact; runtime scale/projection/orientation calibration is pending.

## Evidence and interpretation

The embedded-palette surface body and catalogue phases 0, 10, 20, 30 and 40 were inspected. RI07 shows a flared pedestal, single broad saucer, dark left roof feature, circular roof/foot features, small rim fittings, pale/gold exposed neck, tall segmented green mast and a silver three-prong crown. The silver crown and single saucer distinguish it from RI06. Hologram phases reveal/highlight one view; they are not five camera rotations.

Reference provenance is in `rigellian-building-references.json`; original pixels and comparison sheets remain under ignored `artifacts/rigellian-building-reference-study/RI07/`. Exact well depth, sleeves/fins, circular-cover engineering, hidden surfaces, neck struts and fork connections are authored inference. Original pixels or meshes are not distributed in the new asset.

## Construction and refinement

The pedestal overlaps the saucer's actual lower cap. A solid brass neck and four pale struts connect the saucer to the green mast; the silver crown stem and fork bowl overlap the mast and each other. The interpreted roof well is cut into the saucer, with an embedded sleeve/floor and supported cooling fins. Both circular covers and two rim bezels embed into actual surfaces. Three shallow dents alter the pedestal, saucer and mast geometry.

Revision 1 exposed radial roof shading near the mast. Revision 2 adds analytic radial/profile corner normals after Boolean triangulation while keeping real bore/floor transitions. Rendering showed that material modulation also contributed: the cylindrical wear field turned repeated angular modulation into a starburst on the sloped roof. Revision 3 removes the misplaced roof-height dirt band and greatly reduces periodic modulation, retaining local stains, scratches and subtle roughness variation. Actual top and quarter views confirm removal of the starburst. Precise proportions and interpretation of small fittings still require artistic review.

Independent 1024x1024 shell and 512x512 cap colour/roughness maps are packed in Blend and embedded in GLB. Explicit world-placement cylindrical side and planar cap UVs are assigned after construction. There are no external texture dependencies or imported original image pixels.

## Verification and gates

`verify_rigellian_science.py` reopens native Blend and imports standalone GLB in Blender 4.5.15 LTS. It checks topology, positive closed-shell volumes, evaluated bounds, identity hierarchy, nominal footprint/ground, actual well/sleeve/floor/fin contacts, three dent depths, pedestal/saucer and neck/mast overlaps, four strut/mast contacts, circular-cover and bezel/face contacts, and silver crown attachments/terminals. The connected nearest-surface sample graph is diagnostic evidence, not exhaustive solid-intersection proof.

Every mapped polygon loop and six planar cap surfaces are checked. Native packed images match authored PNG hashes; full colour and roughness pixels survive GLB ORM packing. Eight material values agree within one 8-bit quantization step. The imported model is actually rendered with the exact saved native camera. `review_rigellian_science.py` checks six native 900x900 transparent views plus the imported view, 24-pixel framing margin, identical threshold-128 silhouettes, bounded antialiased-edge alpha and foreground RGB differences.

Revision 3 has 38 meshes and eight used materials. Native/imported and seven render checks pass. Only the scoped Blender `native_and_glb_runtime` gate is recorded against exact-file evidence under the #976 policy; all other gates remain false. This does not accept artistic fidelity, high-detail quality, construction/damage states, calibrated attachments or game-client integration. No gameplay renderer/registration changed. Further review of mast/pedestal proportions, cover/fork engineering and comprehensive contacts remains open.
