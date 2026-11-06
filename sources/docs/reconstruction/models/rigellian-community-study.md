# Rigellian Community RI04

Tracked in [#973](https://github.com/ender-dev-pl/ed-openfa-game/issues/973), relates to #948, #946 and reference evidence #970.

The independently authored editable Blend, standalone GLB, authored-only gallery, renders, maps and provenance are in `docs/assets/reconstruction/buildings/rigellian/community/`. Preserve `openfa:building/legacy/043`, global type 43, definition class 0 and nominal 2x2 footprint. `PlacementRoot` is identity at ground Z=0. Earlier coarse models are retained; runtime scale/projection calibration remains open.

## Evidence and interpretation

RI04's embedded-palette surface body and catalogue phases 0, 10, 20, 30 and 40 were inspected, including an enlarged highlighted view. The source shows two rounded green pods separated by a narrow waist, six upper gold square fittings (three columns/two staggered rows), two lower gold fittings, pale lower vertical equipment with a red core, a stepped gold crown foot and a compact three-prong gold fork. The hologram reveal/highlight sequence is not a turntable. Reference hashes and catalogue identity are in `rigellian-building-references.json`; original pixels and comparisons remain under ignored `artifacts/rigellian-building-reference-study/RI04/`.

The model gives each fitting an embedded dark retaining bezel, inset square brass face and small captive corner screws. The lower equipment has an actual cut recess, solid backing, continuous curved retaining frame, paired pale louvres and a red structural core. Exact recess depth, louvre engineering, screws, hidden sides and crown connections are independently authored inference. The visible source silhouette and colour ordering guide construction; hidden engineering is not presented as recovered original geometry.

## Refinement

The first actual render comparison showed a narrow lower equipment panel and thin fork arms. Revision 2 widens the cut/frame/louvres and thickens the outer gold conductors, supported by a flared fork cradle. The central conductor remains taller and slimmer than the side arms. Pod proportions, square fitting placement and the stepped gold foundation remain readable against both surface and highlighted source views. Further artistic review is required for precise crown/pod proportions, lower-equipment engineering and fine detail.

Native/imported UV checks also exposed a sequencing defect: the waist's bevel was applied by the exporter after UV assignment. The builder now applies its modifiers before assigning cylindrical side UVs and planar cap UVs, so both formats retain the same mapping on final geometry. The two pods and solid waist use independent packed 1024x1024 shell and 512x512 cap colour/roughness maps. Analytic contamination, soft stains, deterministic scratches and two actual geometric dents implement the new-object wear instruction. No legacy pixels are imported into the model.

## Verification and remaining gates

`verify_rigellian_community.py` reopens the Blend and imports GLB in Blender 4.5.15 LTS. Checks cover topology, positive closed-shell volumes, actual evaluated bounds, identity root/parenting, nominal footprint/ground, actual service-recess depth, two measured dents, waist/pod cap overlaps, eight bezel/body and brass-face/bezel contacts, red-core/backing contact and three crown terminal positions. A sampled nearest-surface contact graph is supplementary diagnostic evidence rather than exhaustive solid-intersection proof.

All mapped polygon loops are checked: six planar end surfaces use their actual cap radii, and side/pocket faces preserve cylindrical mapping in world placement space. Packed image bytes are checked against independently authored PNG hashes; complete colour and roughness pixels are compared through GLB ORM packing. Used material values are compared within one 8-bit quantization step. The imported model is actually rendered in the same camera/light setup.

`review_rigellian_community.py` checks six native 900x900 RGBA views plus the imported-GLB view, at least 24 pixels of framing margin and foreground colour difference. The imported render uses the exact saved native camera. Revision 2 differs at one antialiased edge pixel by 4/255 alpha, while its threshold-128 silhouette matches exactly. The review records these values and permits at most four edge pixels with alpha error at most 4/255, retaining exact binary-silhouette equality and the existing colour-difference limit. The authored-only gallery is deliverable; original-pixel comparison sheets remain reference-only. No gameplay renderer/registration changed, and no client integration is claimed.

Revision 2 has 62 mesh objects and eight used materials. Native/GLB checks and all seven render checks passed, with a single connected sampled contact component in each format. Final artistic acceptance, comprehensive structural contacts, construction/damage states and runtime scale/orientation/placement remain open. This is a registered reference-refined study, not an accepted completed asset.
