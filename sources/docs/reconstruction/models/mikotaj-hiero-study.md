# Mikotaj Hiero — first authored iteration (#1012)

`openfa:ship/mikotaj/hiero`, global type 20, Mikotaj local type 0, role class 2. The gameplay catalogue tags it as a scout. The authoritative inventory had no registered source study. This creates a missing first source and preserves previous reconstructions/refinements; artistic refining remains deferred.

## Source evidence

MK0C.256 is absent; the runtime fallback selects MK0A.256. All 32 populated, correctly paletted headings were inspected. Sprites are approximately 17–21 pixels wide and 13 pixels high. They show a compact blue/grey body with short radial projections, a tall central spike and a small gold lower-spike detail. Exact projection count, cross-sections, hidden surfaces and front/rear calibration remain unresolved. No catalogue video is located.

The functional text index maps the name but no narrative. Two equipment slots have no recovered mount coordinates; metadata binds the gameplay catalogue hash and records two declared slots / zero calibrated 3D mounts. The authored local -Y alignment helper and four modelled fins are not assigned to equipment slots or a proven weapon/engine function.

The original ENGLISH.CDB Mikotaj Architecture article, record 76 at 0x39fa, distinguishes heavy ore-like metallic mining-colony structures from light resonant crystal architecture on home worlds. These are architectural statements. Their contextual use for robust metal interfaces on a scout does not establish this ship's geometry or materials. The opaque blue/grey treatment follows the actual sprite colours; no transparent crystal ship or universal cultural shape is inferred. Metadata binds the cultural/reference indexes and generator/helper sources. Original pixels remain reference-only, never mesh or texture inputs.

## Independent assembly

`docs/assets/reconstruction/ships/mikotaj/hiero/` contains editable Blend/GLB, four independent blue/gold colour and roughness maps, provenance, actual render gallery and technical reports. The 34 closed meshes/four materials comprise an eight-sided low hull, upper spike and lower keel, four separately closed tapered fins with dark fitted insets, an octagonal gold collar and front spike stripe, four body-fitted roof covers/eight slots, eight cover fasteners and a narrow upper needle.

Four radial fins, eight-sided sections, gold collar/stripe and all maintenance details are independently authored interpretations below the source resolution. Profile shells retain planar octagonal faces with dense subdivisions for physical wear, and explicit triangle-fan caps. Fins use dense closed upper/lower surfaces and taper in width/thickness. The collar is an actual open annular mesh matching the spike facets; the stripe follows its flat front plane. Roof covers/slots are sampled from the actual body mesh, and fasteners align to the measured roof normal.

One hull dent and four independent fin dents, analytic stains, grain and seeded scratches supply new-object wear. Two packed image materials cover 13 meshes; oxidized alloy and carbon-dark seams use authored rough solid materials. Bevels precede local box UV assignment. Explicit corner normals preserve native/imported shading. All components remain separately editable under PlacementRoot, without regenerating any earlier source.

## Verification scope

The verifier reopens native Blender and independently imports GLB. Checks cover closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, actual corner normals within 0.001, transforms/bounds, source/helper/binary hashes, packed image bytes and decoded colour/roughness/material parity, box UVs and all five measured dents.

Odd/even actual mesh-ray containment checks spike/keel roots, 36 fin/body root samples, 36 fin-inset samples, eight collar roots with a clear axial-void witness, nine gold-stripe roots, 108 roof-cover/slot contacts, eight roof fasteners and needle attachment. Sampled contacts are scoped evidence, not exhaustive structural proof. AlignmentForward is tested under four rigid root rotations, without inferring source animation, heading calibration or two recovered equipment sockets.

Actual native/imported Blender renders exercise the standalone modelling runtime. Whole-object framing, intentional detail crops and matched-camera alpha/silhouette/pixel checks remain separate from artistic acceptance. Eight paletted headings are compared qualitatively; all-heading inspection and original crops remain ignored reference evidence. Game-client integration is unchanged.

## Deferred

Exact proportions/fin count and arrangement, spike/keel construction and material divisions, hidden interfaces/functions, two calibrated equipment mounts, runtime scale/orientation and required operating/damage variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.

The actual gallery and original-heading comparison were inspected. First-version verification passed in Blender 4.5.15 for 34 meshes/four materials, including 13 mapped meshes. The hull dent measured approximately 0.00499 model units, and four fin dents about 0.00290 each. Maximum actual corner-normal vector error was below 0.000615 (bound 0.001). Nine rendered views passed framing/export checks: both matched-camera alpha channels and threshold-128 silhouettes are identical, with maximum foreground mean colour difference below 0.003/255. Cultural-source validation passed for six architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `6d840675`. Existing models were not regenerated or refined.
