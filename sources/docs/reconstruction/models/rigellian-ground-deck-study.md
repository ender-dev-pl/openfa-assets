# Rigellian Ground Deck RI10: mechanism evidence

**Semantic correction:** the original English description identifies Ground Deck as the Rigellian Landing Pad, an access point to vast underground hangars. The open feature is a deep shaft. Earlier references in this document to floor ribs, a grille or a raised shallow deck are rejected modelling interpretations retained only as iteration history. Vertical lines belong to the shaft-wall presentation; exact guide engineering remains inferred.


Tracked in [#980](https://github.com/ender-dev-pl/ed-openfa-game/issues/980); relates to #948/#946 and source milestone #970. This is a mechanism-analysis milestone before the animated high-detail model. No new model or artistic acceptance is claimed.

Identity: `openfa:building/legacy/049`, global type 49, definition class 26, nominal 3x3 footprint. Existing model studies and user files remain intact.

## Actual descriptor evidence

`analyze_rigellian_ground_deck.py` verifies every nonempty reference PNG against the correctly paletted source manifest, measures raw alpha contours at source offsets, and records all 18 descriptors in `rigellian-ground-deck-mechanism.json`. Original pixels remain only under ignored `artifacts/rigellian-building-reference-study/RI10/`; the committed output contains measurements and hashes, not source artwork.

Layer 0 is the separate shadow. Layer 1 already contains the dark ribbed interior and two red fittings, surrounded by the green body, brass structural parts and the right-hand upright. Layers 2..14 are paired green cover overlays. In the source coordinate plane their outer bounds remain at X=146 and X=174 while the inner edges retreat towards the respective outer edges. Both halves decrease from 14 pixels wide in descriptor 2 to one pixel wide in descriptor 14. Initial projected heights remain 11 pixels; later heights decrease to three/four pixels.

These measurements establish disappearing paired covers and an increasingly exposed static interior. They support outward retraction as a candidate but do not uniquely establish a translation, hinge axis or hidden pocket. Low-resolution shading and contour changes do not prove the full 3D sweep. Do not label these 16 activity descriptors as directional rotations.

Layers 15 and 16 have zero dimensions and no image. They require an explicit empty state, not invented replacement geometry. Layer 17 is a lower-structure overlay with purple mixed-shadow pixels. It is not another pose of the green covers. Diagnostic base-plus-overlay sheets are not proof of all original composition rules.

## Legacy state selection

The current permanent decompile confirms `UpdateLandingPadActivitySpriteFrame` at 0x44BE0. Its caller dispatches definition class 0x1A (26) to this function. The reference catalogue independently identifies RI10 as class 26. The function reads signed attached SHIPS altitude at +0x3C; with no attached record it selects descriptor 2.

For altitude from -191 through 191 it computes activity `20 - floor(abs(altitude) * 20 / 192)`, caps activity at 16, and selects descriptor `activity + 1`. Altitudes below -191 or at least 192 select descriptor 2. This is a state mapping, not a measured animation duration. Exhaustive enumeration of all 65,536 signed inputs yields 31 contiguous descriptor bands, preserved in the JSON evidence. In particular:

| Altitude | Descriptor | Interpretation from source pixels |
| --- | --- | --- |
| absent, <= -183, >= 183 | 2 | closed paired covers |
| -76..-68 or 68..76 | 14 | final thin cover strips |
| -67..-58 or 58..67 | 15 | empty overlay |
| -57..-48 or 48..57 | 16 | empty overlay |
| -47..47 | 17 | lower structure / mixed composition |

The C# selector documents the equivalent Terran path. However, `legacy-gameplay.json` currently sets `landingPadDefinitionId` to `terran:landing-pad`, and `SelectActivityOverlayFrame` explicitly checks that ID. Legacy class dispatch does not prove current Rigellian integration. Full call-site mapping and any alien registration changes require a separate runtime milestone; none are made here.

## Model contract and unresolved work

The upcoming model needs an identity placement root, fixed static housing/interior and independently editable left/right cover assemblies. A disappearing cover must use a physically coherent authored mechanism, preserving the observed silhouette progression without shrinking solid geometry as an animation shortcut. Hidden pockets/hinges and their motion remain inferred until comparative renders support a choice. Validate open, intermediate, closed and empty states, hierarchy/pivots, sweep clearance and imported GLB animation rather than exporting only the closed body.

Separate the lower structure from cover state and from shadow composition. Do not recolour purple source pixels as physical metal. New surfaces must receive material-appropriate wear under the 2026-10-29 instruction, while existing models remain unchanged.

Pending: editable Blend/animated GLB, actual multi-state render/refinement, independent geometry/material/pivot checks, state exports, final artistic review and calibrated game integration. No acceptance gates changed during this analytical milestone.

Reproduce: run `prepare_rigellian_building_references.py --check`, then `analyze_rigellian_ground_deck.py --check` with the legacy Python runtime.

## Animated model study, revision 3

The authored Blend and animated standalone GLB are now in `docs/assets/reconstruction/buildings/rigellian/ground-deck/`. These are a mechanism study, not final high-detail artistic acceptance. The static structure has a green oval body/coaming, brass load-bearing buttresses and shoulder caps, front steps, a rear-right mast, nine internal ribs and two red inset indicators. Seven used materials include packed independently authored colour/roughness maps; the body includes a shallow geometric dent. Existing models were not modified.

An initial downward-hinge hypothesis was rendered and rejected because its deep cavity hid the source-visible interior. Revision 2/3 uses two rigid telescopic segments per side, lowered before retracting into actual side cavities. Segment scale never changes. The split, drop, side-cassette engineering and 61-frame preview timing are authored inference, not recovered legacy details. One GLB clip `GroundDeckCoverCycle` has six translation channels: two drop assemblies and four moving segments. Frame 1 is closed, 16 intermediate, 31 open and 61 closed again. This preview is not an implementation of the altitude selector or the mixed-composition descriptor 17.

Actual verification exposed collisions at the coaming and mast foundation. The model was reworked with continuous undercut channels through the body/coaming, and the mast foundation moved behind the cassette path. Duplicate end vertices on the half-ellipse were removed after topology verification failed. A front notch was cut after the first render hid the steps.

Native Blend reopen and actual GLB import verify 50 closed mesh objects, 3x3 identity placement, all eight moving meshes, stationary structure, material values and full colour/roughness pixel preservation. Twelve sampled poses check evaluated moving/fixed triangle intersections and world transforms through the opening and return cycle. This is sampled surface intersection evidence, not proof of continuous swept-volume clearance or containment-free solids. The GLB animation is explicitly checked for the single expected clip and six translation targets.

Closed, intermediate and open quarter views plus open top views are actually rendered in native/imported runtime. Six static views and these states form an authored-only gallery; source comparison stays under ignored reference artifacts. The open top view documents ribs and both red fittings, which are partly occluded by the near coaming in quarter view.

Outstanding: side-cassette outline and body proportions still differ from the legacy image; cover engraving and structural detail need further refinement; load/guide attachment engineering, continuous sweep and moving/moving checks remain incomplete. Empty descriptors and mixed lower-structure/shadow state are not fully exported as calibrated runtime states. Final artistic acceptance and game integration remain open. No acceptance gate is promoted by this animated-study milestone.

## Revision 4: silhouette and motion clearances

Reduced cassette thickness from 0.56 to 0.22 authored units and reduced the main body depth from 0.90 to 0.74 while retaining the deck cavity. The body now starts at Z=0.25 rather than 0.04, exposing more of the brass supports. Its roof reaches Z=0.99, providing a real skin over the undercut channels instead of the unintended gaps visible in revision 3. Side cassette width is 0.50 with the inlet at X=+/-0.85, leaving room for the initial cover drop.

Replaced the oval cover fields with inset D-shaped profiles, matching the flat centre-facing edges and curved outer edges visible in the catalogue highlight. The actual cover solids and inset fields are split with small manufactured gaps between telescopic stages. Stage strokes increase to 0.88/0.46 so the leaves fully clear the aperture in the open state. These dimensions and hidden telescopic engineering remain authored inference.

Verification now checks all 61 integer preview frames in both native and imported GLB, including separate moving segments against each other. The intentionally embedded inset field and shell of the same segment are not treated as an interference pair. This broader check found cassette inlet intersections at frames 2 and 60 that the earlier twelve-pose sample missed; the cassette inlet was moved outward before rerunning successfully. Continuous subframe sweep, volumetric containment and comprehensive guide/load attachments still require further evidence.

The thirteen native/imported render checks, source comparison, inventory verification and changed-code quality gate pass for revision 4. The comparison confirms reduced bulk and corrected field outlines, but main-body/brass-support proportions, source-facing projection, finer construction detail and state composition still need refinement. No final visual or runtime-integration gate is accepted.

## Revision 5: reference-facing support and mast refinement

The base-layer gold-colour component measurements are now reproducible in `analyze_rigellian_ground_deck.py` and stored in `rigellian-ground-deck-mechanism.json`. A four-connected opaque RGB mask identifies diagnostic colour regions; visual inspection assigns the two front support regions at local pixel bounds [12,17,17,29] and [26,17,33,29]. Their bounding-region centres are 15/44 of the sprite width apart. This is a low-resolution proportion cue, not an exact recovered 3D dimension or automatic semantic segmentation.

The previous front supports were almost as widely separated as the side cassettes. Replaced them with broader closed tapered castings: top centres X=+/-0.48, lower centres X=+/-0.62, widening/splaying towards the ground, with actual foot flanges. Retained the separate rear supports. Narrowed the three front steps from 0.75 to 0.56 units, fitting between the corrected front supports. These hidden depths and precise slopes remain authored inference.

The upper mast was too tall relative to the nearby rear brass caps in the source. Reduced its upper endpoint from Z=1.51 to Z=1.25 while preserving its attachment and bent top. No moving channel or preview timing changed.

Added native/imported `reference-facing` renders from a frontal oblique diagnostic camera (direction [0,-16,7]). This is an authored comparison view, not a recovered original camera or game projection calibration. The comparison sheet now pairs the actual closed base-plus-cover source composite with the closed model, rather than using the exposed static interior as the closed reference. Catalogue phases remain one presentation rather than independent spatial views.

Revision 5 passes native/imported verification at all 61 integer preview frames and fifteen RGBA framing/render comparisons, including the new matching frontal view. Current model/export/report hashes were checked against the delivered files. Inventory and changed-code quality checks also pass. No final visual or integration gate is promoted: body profile, outer side structures, detailed guide/load attachments, source-facing projection, continuous swept/volumetric clearance and complete runtime state composition remain open.

## Descriptor-pose export studies

The `states/` directory now contains fourteen unique static standalone GLB pose assets and paired native/imported diagnostic renders. `state-exports.json` maps all descriptors 2..17 to these assets and retains the verified signed-altitude bands/no-attached-record descriptor from the source analysis. Descriptors 2..14 each have their own pose. Descriptors 15/16 share a covers-stowed full-assembly pose because the legacy cover overlay is empty; descriptor 17 references this same physical pose while explicitly leaving lower-structure/mixed-shadow composition unverified. A complete 3D assembly render is not an export of an original empty overlay.

Pose controls are authored fits from the remaining X-width of each left/right source alpha mask, retaining the observed one-pixel left/right differences. All segments remain rigid. No legacy pixels are embedded. The telescopic mechanism, initial drop, world dimensions and correspondence to rendered source contours remain inferred. The static pose assets contain no preview animation clip.

`export_rigellian_ground_deck_states.py` reopens the current native Blend for each unique pose, clears preview animation, applies the pose, verifies topology/hierarchy/bounds and moving/fixed plus separate moving-stage surface intersections, and exports static GLB. Each export is actually re-imported; per-object world matrices/evaluated vertex bounds, material values and embedded texture/material content are compared. Full colour/roughness pixel preservation is verified for the first export, and every later GLB has identical embedded texture bytes/material declarations. Every pose has an actual native and imported render.

`review_rigellian_ground_deck_states.py` checks all twenty-eight RGBA renders and fourteen native/imported comparisons, produces an authored-only state gallery, and saves a descriptor-by-descriptor reference comparison under ignored artifacts. The comparison was inspected: cover progression is present, but current body/projection differences and the deep/occluded red interior indicators are still visible fidelity failures. Pose export does not resolve these failures or accept the model artistically.

The programme/inventory register the state index and its hash. `model_state_exports.py` rejects stale model/export provenance, changed mechanism evidence or generator/reviewer, missing/duplicate descriptors, changed pose files/renders, unsafe artifact paths and stale render review. Regression tests cover valid current evidence, line-ending portability and representative stale/invalid cases. JSON/Python evidence hashes normalize CRLF to LF; binary model/image hashes remain exact. This is provenance validation of an actual Blender run, not a replacement for it or an artistic gate.

Pending: refine the source-facing silhouette/interior visibility and pose correspondence; regenerate these derivatives whenever the model changes; complete physical attachment/continuous clearance checks and calibrated empty/mixed runtime composition. No acceptance gate is promoted by these pose studies, and no gameplay renderer or registration changed.

## Revision 6: functional correction to a deep hangar-access shaft

The original `_TEXT/ENGLISH.TXT` identifies Ground Deck as the Rigellian Landing Pad at byte offset 0x1137E. The Landing Pad description at 0xF421 describes ship access to vast underground hangars; the Ship Yard description at 0xF2A0 describes large pressurised underground hangars. Source file/string hashes and offsets are now preserved in the mechanism evidence. The shallow floor/grille interpretation was incorrect. It is removed rather than adjusted to force red-feature visibility.

The model now has a real hollow shaft extending to Z=-2.0, three vertical features on the far shaft wall and two red wall-mounted fittings. Its exact depth and guide engineering are authored inference. A remote dark bottom closes the model well below ground; nothing spans the mouth as a grille or shallow landing platform. The shaft liner is offset from the body bore to prevent coincident-surface artifacts. Wall fittings overlap their actual curved backing instead of floating above a floor.

Thin rigid cover segments use a small 0.035 lift followed by side retraction, with 0.012 shell thickness and 0.016 separation between stage planes. This replaces the earlier speculative downward-stow/shallow-floor arrangement; hidden telescopic mechanics remain inferred. Shallower side cassettes accommodate the thinner segments. The surface footprint and ground-level identity placement root remain 3x3, while the explicitly identified shaft parts extend below ground.

A preview-only ground holdout outside the opening masks buried geometry in surface renders. It is excluded from the GLB and from asset geometry checks. Surface cameras frame the above-ground structure; the underside view is an intentionally unmasked full-geometry cutaway. The standalone GLB retains the actual below-ground shaft for later terrain integration. This staging does not implement the original purple-shadow composition.

Verification now sends nine vertical rays through the open mouth; each must reach the distant bottom below Z=-1.9. It separately checks nine viewing rays per red wall fitting: closed covers must occlude them, and the open diagnostic frontal view must expose them. Native/imported geometry, all 61 preview frames and moving-part intersections remain checked. Only shaft-tagged geometry may extend below ground. A tiny nearly-collinear cover face exposed by GLB triangulation was removed during geometry cleanup; topology thresholds were not relaxed.

All descriptor-pose derivatives are regenerated from this corrected model and checked again. Pixel checks additionally require both red fittings in the imported covers-stowed frontal render and no red fittings through the closed covers. These checks guard visibility and function; they do not grant final artistic acceptance. Outer body/side structures, exact hidden engineering, continuous/volumetric clearances and complete calibrated state composition still need work.
