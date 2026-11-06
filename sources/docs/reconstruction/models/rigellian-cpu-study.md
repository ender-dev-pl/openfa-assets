# Rigellian Central Unit RI01 study

Issue: [#969](https://github.com/ender-dev-pl/ed-openfa-game/issues/969), relates to #948 and #946.

The independently authored revision 2 source is `docs/assets/reconstruction/buildings/rigellian/central-unit/model.blend`, with standalone `model.glb`, six transparent renders, an authored-only gallery, provenance and technical/render reports. The earlier coarse catalogue study remains intact. Catalogue identity is `openfa:building/legacy/040`; the nominal footprint is 3x3 with an identity `PlacementRoot` at ground Z=0. Runtime calibration is pending.

## Evidence and reconstruction

`rigellian-cpu-reference.json` records source, indexed pixels, expanded embedded VGA palette and reference frame hashes. `prepare_rigellian_cpu_references.py --check` revalidates these sources. The ground layer and complete body layer are distinct. RI01.VID is a hologram reveal/overlay sequence: frames 0, 10, 20, 30 and 40 are presentation phases, not five spatial views. Unseen geometry cannot be inferred as observed from this sequence.

Observed features are the broad upper saucer, flared and waisted foundation, exposed neck grille, gold three-prong crown, dark/pale roof features and circular gold foundation details. Hidden sides, underside, dimensions, exact aperture depth, seam/fastener counts and internal grille construction are authored interpretations. Original pixels are retained only under ignored `artifacts/rigellian-cpu-reference-study/`; none are packaged with the model.

Actual render comparison is saved there as `comparison.png`. Revision 1 exposed an intersecting flat roof cap and discontinuous foundation joints. Revision 2 follows the roof with a closed conformal cap, splits joints at profile changes, and adds a solid crown mounting socket. The saucer and waisted-base silhouette is recognizable against both surface and hologram references. The brighter, smoother materials, projected crown/neck proportions, circular feature placement and hidden construction still require artistic review; this is not final acceptance.

## Verification and limits

`verify_rigellian_cpu.py` reopens the Blend and imports the GLB in Blender 4.5.15 LTS. It checks actual mesh topology, positive closed-shell volumes, six materials, no external image dependencies, identity placement hierarchy, evaluated vertex bounds, nominal footprint and ground level. Rays confirm a cut roof well, open neck grille shell, three crown terminals and a roof-following cap whose backing embeds in the saucer. All 83 meshes survive export; bounds agree within 0.002 units. Structural contact coverage beyond the roof cap remains incomplete.

`review_rigellian_cpu.py` verifies all six 900x900 RGBA renders, transparent background and at least 24 pixels of framing margin. Native generation, rendering, reopening and GLB import were exercised in the actual Blender runtime. No gameplay renderer or registration changed; no client integration or placement acceptance is claimed.

### Revision 3: roof equipment seating

An evaluated world-space contact diagnostic found two disconnected groups in both native and imported files: the 78-part main body and the five-part roof-well assembly. The insert bottom sat 0.006 units above the cut floor and the sleeve outside radius was 0.015 units smaller than the bore. Revision 3 lowers and widens the sleeve and floor to embed into the actual saucer. The cooling fins now overlap the floor instead of relying on an exact tangent contact. Top-view inspection also exposed coplanar crown socket/rim faces; the socket is now recessed below the rim, with a ray-based separation regression check.

`audit_rigellian_cpu_contacts.py` samples evaluated vertices and polygon centres against world-space nearest surfaces. Both formats now produce one connected 83-part component with no isolated pieces. `contact-review.json` records the model hashes, links and connected components. This diagnostic can miss edge-only intersections and does not establish exhaustive solid-contact quality. Additional ray checks explicitly verify sleeve/saucer, floor/saucer, floor/sleeve and all three cooling-fin/floor contacts. Native/GLB geometry checks and all six render checks pass again. The authored silhouette and clean material treatment are preserved.

Construction/damage states, animation requirements, comprehensive structural contacts, runtime projection/orientation/placement and final artistic approval remain open. The model is registered as a study with final acceptance false.

The surface-wear instruction dated 2026-10-29 applies to subsequent newly created objects. This CPU was generated before that instruction and is intentionally not retrofitted with dirt, stains or dents; existing-model updates require the user's separate request.

Issue #976 adds an actual imported-GLB render using the saved native camera and updates the authored gallery/render report to seven views. Native/imported comparison passed with identical alpha and low foreground colour error. The Blend, GLB and original six native views remain unchanged. The scoped technical runtime gate is now recorded against exact model/export/report/script/render evidence; artistic quality, state coverage and client calibration/integration remain open. See `native-glb-runtime-reviews.md`.
