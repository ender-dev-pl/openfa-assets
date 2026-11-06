# Rigellian Strategic Bunker RI06

Tracked in [#975](https://github.com/ender-dev-pl/ed-openfa-game/issues/975), relates to #948, #946 and reference milestone #970.

The independently authored editable Blend, embedded-texture GLB, authored-only gallery, maps and review reports are in `docs/assets/reconstruction/buildings/rigellian/strategic-bunker/`. Preserve `openfa:building/legacy/045`, global type 45, definition class 24 and nominal footprint 3x3. `PlacementRoot` is identity at ground Z=0. Prior models are retained; runtime scale/projection/orientation calibration remains pending.

## Source evidence and interpretation

The embedded-palette surface body and catalogue phases 0, 10, 20, 30 and 40 show three broad saucer levels, dark left roof features, small rim fittings, a central upper neck with pale/gold equipment, a tall green mast and a compact gold fork. These are one spatial presentation revealed and highlighted over time, not five recovered camera angles. The source record is in `rigellian-building-references.json`; original pixels and comparisons remain under ignored `artifacts/rigellian-building-reference-study/RI06/`.

The model interprets each dark roof feature as a cut well. Exact bore/floor depths, sleeves, cooling fins, hidden underside/column structure, mast retaining struts, fitting counts and fork engineering are authored inference. Broad roof highlights are produced by curved geometry and lighting rather than treating every bright source patch as a separate invented fitting. The precise rendered aspect, mast/disc proportions and roof-feature interpretation still require artistic review.

## Construction and refinement

Each independently shaped saucer has an actual cylindrical roof cut, a sleeve embedded in the cut wall and bottom, an overlapping recessed floor and two supported fins. A solid central column overlaps all three levels. The exposed gold mast neck overlaps the top saucer and green mast; four pale retaining struts meet the mast. Six small square gold rim faces are inset into dark bezels that embed into the saucer rims. The crown stem/fork bowl and all three terminals are separate editable solids.

Revision 1's lower roof wells were heavily occluded in the source-facing quarter render. Actual surface/hologram comparison led to revision 2: level starts change from 0/0.9/1.8 to 0/1/2 authored units, the connected mast assembly moves upward by 0.2, and wells move toward the visible left/front roof region. Sleeve tops remain below the surrounding roof. All three dark wells are now readable in the quarter view, with their structural contacts retained. Close top inspection also exposed triangular shading around the Boolean bores; recalculated normals, continuous nonplanar-face shading and sharp bore transitions remove those artifacts in the regenerated views. Overall source matching remains a study rather than a final silhouette acceptance.

Independent packed 1024x1024 shell and 512x512 cap colour/roughness maps provide joint contamination, soft stains and fine scratches; three measured shallow dents alter actual saucer geometry. Explicit world-placement cylindrical side UVs and planar end UVs are assigned after mesh construction. All four authored maps are embedded in the GLB and packed in the Blend. No original image or mesh is imported into the authored model.

## Verification and remaining gates

`verify_rigellian_bunker.py` reopens the native file and imports GLB in Blender 4.5.15 LTS. It checks topology, positive closed-shell volumes, evaluated bounds, identity placement hierarchy, 3x3 footprint/ground, actual roof-cut depth, sleeve/bore contacts, floor/sleeve/base contacts, six cooling-fin supports, three dent depths, six bezel/body and face/bezel contacts, all three column/level overlaps, neck/roof/mast overlaps, four strut/mast contacts and crown attachment/terminals. The sampled nearest-surface contact graph is supplemental diagnostic evidence, not exhaustive solid-intersection proof.

Every mapped polygon loop and ten planar end surfaces are checked in both formats. Native packed images match authored hashes; full decoded colour/roughness pixels survive glTF ORM packing. Seven used material values are compared within one 8-bit quantization step. Imported rendering uses the exact saved native camera. `review_rigellian_bunker.py` checks six native 900x900 transparent views plus the imported-GLB view, 24-pixel framing margin, exact threshold-128 silhouettes, tightly bounded antialiased edge alpha and foreground RGB differences.

Revision 2 has 53 meshes and seven used materials. Actual native/imported checks and seven render checks pass; sampled contact graphs are connected in both formats. No gameplay renderer/registration changed and no client integration is claimed. Final artistic acceptance, precise mast/level proportions, fine construction detail, comprehensive contacts, construction/damage states and runtime calibration remain open. This is a registered reference-refined study, not an accepted completed reconstruction.
