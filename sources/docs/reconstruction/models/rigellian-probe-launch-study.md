# RI11 Probe Launch Ă˘â‚¬â€ť initial editable study (#982)

Catalogue ID `openfa:building/legacy/050`, global type 50, definition class 9, nominal footprint 2x2. This study is not final artistic acceptance or game integration.

## Function before geometry

Original ENGLISH.TXT record 911, byte offset 0x113AC, describes construction and launch of research and espionage satellites. The functional index binds the source bytes and catalogue identity. This is separate from RI10 Ground Deck, an entrance to underground ship hangars.

## Observed and inferred

The correctly paletted RI11 surface body (28x18) and catalogue phases show a low stepped green circular housing, raised central opening, pale vertical features inside it, and a small gold front fitting. Catalogue reveal/highlight phases are not spatial rotations. The dark region left of the upper opening is ambiguous; this study does not assume it is a separate vent.

The precise rotational profile, hidden bore depth, three internal guides, liner, low mechanism floor, rear/bottom geometry, casting and captive screws are independently authored engineering interpretations. Legacy pixels are reference-only and are not textures or mesh inputs.

## Refinement and checks

Actual Blender renders exposed a front fitting face intersecting the lower curved shell. Its planar front was moved outward while retaining a body-fitted embedded back. Verification now samples 32 perimeter roots and checks the inset face and four captive screws. The shell has a measured geometric dent; analytic colour/roughness textures add restrained joint contamination, handling stains and scratches. An inherited wear-generator height mismatch was corrected to the actual 0.75-unit UV domain.

Native Blend and imported standalone GLB checks reopen both files and inspect closed positive topology, identity placement root, footprint, bounds, deep centre rays through the open port, liner/body overlap, three guide/liner contacts, the measured dent, fitting contacts, UV mapping and every packed colour/roughness pixel. Material values are compared within export quantization. The imported render uses the exact saved native camera. Seven 900x900 transparent views pass framing checks and native/imported silhouette and pixel comparison.

## Deliverables and outstanding work

Editable `model.blend`, standalone `model.glb`, authored maps, metadata, technical/render reports and gallery are under `docs/assets/reconstruction/buildings/rigellian/probe-launch/`. Reference comparison remains under ignored `artifacts/rigellian-building-reference-study/RI11/comparison.png`.

The broad silhouette is established, but this remains an initial study: investigate the left dark feature against additional original evidence, refine the upper opening/profile proportions and manufactured finish, and review the internal pale structures without pretending their hidden engineering is confirmed. Construction/damage states, runtime orientation/scale/placement and final high-detail quality remain open. No review-ledger gate is promoted by this milestone.

## Revision 2 â€” collar/shoulder refinement

The first profile rose continuously from the broad base toward the mouth. A controlled hard-key experiment showed that this shape did not produce a bounded left-side shadow comparable to the original dark area. Revision 2 replaces the broad upper conical slope with a distinct, nearly vertical raised collar over a wide lower shoulder. The port aperture, low floor, liner and guides remain open and unchanged.

Three actual Blender renders at key-light elevations 25, 40 and 55 degrees use the same orthographic camera (direction 0,-16,10), one right/front sun, low ambient illumination and identical unchanged materials. See `lighting-study/` under the model deliverables. Its JSON records source Blend and script hashes plus the three rendered-image hashes. The 25-degree render produces a bounded shadow extending left across the shoulder without introducing a separate vent or recess. This makes a cast-shadow interpretation plausible; it does not establish the original light position or prove that no secondary feature exists.

The low-resolution surface and catalogue images were inspected again alongside the revised renders. The distinct collar better explains the abrupt left dark region than the first continuous cone. Exact collar taper and height remain inferred. The three pale guides and hidden launch mechanism are still engineering interpretations, not newly confirmed source details. Final high-detail artistic acceptance remains open.

## Revision 3 — flat internal launch guides

Reinspection of the surface body and readable catalogue phase showed that the pale features inside the port read as broad vertical faces. The first thin round rods under-represented their projected width. Revision 3 uses three flat guide webs (0.054 wide relative to the 0.38-clear-diameter port) with recessed dark running tracks and paired attached wear strips. Their rectangular sections, track construction and precise count/placement remain authored mechanical interpretation; the low-resolution original does not establish those hidden details.

Each track and wear strip is verified by attachment rays at three heights in the actual native and imported geometry. There are 21 mesh objects and six used materials. Centre rays still pass through the open port to the low mechanism floor. Topology, textures, UVs, bounds, identity root, liner contacts, fitting contacts and measured shell dent are rechecked. The verifier also binds the actual builder, parts and wear generator hashes.

Added matched-camera native/imported port detail renders to make guide construction inspectable. These intentionally crop the overall shell and are excluded from whole-object framing margins; all whole-object views retain the previous framing requirements. Both detail and whole-object pairs independently pass exact threshold-128 silhouette comparison, antialias alpha tolerance and RGB mean difference below 1.5/255. The macro pair has identical alpha and maximum channel mean difference about 1.06/255. The gallery now includes nine views, with seven whole-object views and two detail views. All three lighting diagnostics were refreshed against revision 3.

This resolves the thin-rod presentation in the study; final materials/detail quality, construction/damage states and game calibration remain open. No overall or final artistic completion is claimed.

## Shared construction dependency review (#983)

RI11 construction states belong to RIS2, the shared Rigellian 2x2 site family, rather than hypothetical extra completed-body descriptors. See `shared-construction-study.md` and the per-building dependency in `shared-construction-references.json`. Its two visible body stages show structural framing; descriptor zero is a perimeter-like mask. These states still require independently authored editable models and calibration. Damage-effect coverage remains a separate unresolved source question.
