# Achaean Dedicated Ore Transporter remaster

Current canonical model for `openfa:ship/achaean/dedicated-ore-transporter`, issue [#234](https://github.com/ender-dev-pl/openfa-assets/issues/234). Use this same model in flight, build menus and SciTek. The completed first source remains available in `sources/docs/assets/reconstruction/ships/achaean/dedicated-ore-transporter/` as historical authoring material, excluded from the current selection and game packaging.

## Evidence and interpretation

Sixteen populated paletted AC2C headings establish a full copper/red axial hull, wide transverse supports and two thin upright silver/red crescents. Their open mouths face the short yellow-marked aft, opposite the longer pale fore terminal. `reference-evidence.json` binds the original archive entry, decoded frame hashes, cultural text and reviewed ImageGen concept. Original pixels are not published or used as textures. The concept is an artistic interpretation; its unsupported yellow fore markings are omitted from the model.

The Achaean Architecture text supplies curved-form context, not proof of vehicle domes, minarets or ornament. Panel layouts, service structures, vents, recessed fittings, hidden surfaces, small dents and restrained material wear are authored interpretations. Broad paint fields remain quiet instead of using a dense generic grid. Visible round fittings are not assigned recovered weapon or sensor functions. No object-specific video or operational mechanism is established by the current bindings.

## Delivery and verification

`model.blend` is editable; `model.glb` is the portable current export. Both contain 44,856 triangles, 14 mesh batches, one material and two packed 2048-square colour/ORM maps. Maps are independently generated from analytic stains, edge dirt, grain and sparse scratches. The generator scripts and material maps are in the repository. No animation is invented for this delivery.

The saved publication-cleaned native source and independent GLB import were rendered in Blender 4.5.15. Geometry comparison has zero world-position error. Closed pressure/crescent cores have positive volume; eight empty-mouth and eight occupied-rim witnesses pass in each representation. The technical wireframe is rendered from the actual imported model, not a separately improved diagram. See `runtime-verification.json` for source-bound results and `delivery-review.json` for image comparisons. Technical checks do not establish final user artistic or game integration acceptance.

Local forward is -Y and up is +Z. Maximum native extent is 18. Proposed world size 180 is an authored transporter-class recommendation; the current game falls back to 96 and this change does not apply an override. Four gameplay equipment slots have no calibrated 3D sockets. Client orientation, scale, attachments and GPU performance require separate integration review.

Current previews, concept, actual geometry wireframe and source/export downloads are indexed in the Markdown and interactive model galleries. The concept is a target/reference, not a screenshot of the final model.

## Exported-model visual feedback correction

User review identified excessive separation of the crescent arms in the first remaster (commit `a353157c`). The subsequent feedback loop compared correctly paletted AC2C headings 0/4/12/20, the reviewed concept and independently imported GLB renders. The distal arms now converge into a narrower opening while retaining the root structures, lateral mounting positions, body proportions and coherent closed 3D surfaces. This corrects the arm curvature instead of compressing the entire ship. No new ImageGen iteration was needed.

`feedback-baseline.json` records measurements from the previous actual GLB import. `visual-feedback.json` binds the current independent-import measurements, reviewed references, render hashes and qualitative findings. These proportions are authored comparison aids, not recovered physical dimensions or a calculated fidelity percentage. `feedback-comparison.jpg` distinguishes the artistic concept, prior model and corrected actual GLB render; it contains no original-game pixels. The four additional verified views in the galleries are renders of the imported export. Original paletted comparison boards remain outside the repository.

The geometry/visual correction has been reviewed by the authoring agent; user artistic approval and actual game integration remain separate. Concept microdetail and wear are simplified for the game model, and original cameras/hidden construction are not exactly recovered. Successful correction does not calibrate equipment sockets or establish client performance.

### Leading shield width follow-up

The user's marked concept detail required a broader leading crescent shield around the hub. Its root fore/aft width now measures approximately 1.12 authored units, versus the previous 0.64 source parameter. Expansion is confined to the forward edge near the root and fades along the arms; lateral mounts, inner mouth, distal convergence and hull remain unchanged. The imported vertex measurement is recorded in the runtime and visual feedback reports. The gallery's leading-shield comparison isolates the concept, previous export and corrected actual GLB. Diagnostic views confirm the broad shield without closing the crescent opening.
