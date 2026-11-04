# RI13 Gravitic Converter — initial reference-refined study (#985)

Catalogue ID `openfa:building/legacy/052`, global type 52, nominal 2x2 footprint. This is a missing-model reconstruction; no existing refined model was replaced.

## Function and source evidence

Original ENGLISH.TXT record 913 at byte offset 0x11492 describes the combined functions of Gravity Nullifier and Asteroid Engines. The correctly paletted 25x73 surface body and readable catalogue phase show a round grey upper body, narrower lower equipment module, green side risers, red side details, a front circular green feature, flared green foot with a pale fitting and a high segmented tip. Catalogue reveal/highlight phases are not spatial rotations or evidence of moving mechanisms.

Precise 3D dimensions, spherical interpretation of the upper housing, hidden rear/bottom surfaces, shallow assembly seam, brackets, inspection fitting construction, fasteners and service pods are independently authored interpretations. The low-resolution source establishes visible feature placement, not those hidden engineering details. No original pixels are used as textures or mesh input.

## Actual render refinement

The first render exposed a problem missed by basic overlap checks: straight side risers passed inside the sphere and reappeared as small protruding tips. The revised risers follow the front surface of the housing instead. Their actual geometry remains visible and rooted in the sphere at four checked heights per side. UV mapping compensates for that curved centreline; it does not reuse an undeformed cylindrical projection.

A second reference comparison identified the pale fitting on the foot and the asymmetric lower-front panel/vertical strips. These were added without inferring an exhaust, vent or moving mechanism. The foot fitting initially lacked support beneath part of its flange; it was moved onto the actual sloped foot and aligned to that slope. Offset panel contact checks also found a small frame/body gap, corrected by embedding the frame into the drum. The original contact assertions were retained.

Green and grey painted parts have independently generated colour/roughness maps, planar cap mapping, restrained joint dirt, handling stains, grain and seeded scratches. Six authored shallow dents are measured in the actual geometry. Small fittings use separate material values. These additions apply to this newly generated model and do not retrofit prior assets.

## Verification and evidence

Editable `model.blend`, standalone `model.glb`, eight authored source maps, model metadata, technical/render reports and eleven actual 900x900 renders are under `docs/assets/reconstruction/buildings/rigellian/gravitic-converter/`. Original comparison pixels remain in ignored `artifacts/rigellian-building-reference-study/RI13/comparison.png`, outside distributable model assets.

The Blender verifier reopens the native file and imports GLB independently. It checks positive closed topology, identity placement root, footprint/bounds, individual object transforms/bounds, six actual dents, the foot/drum/sphere/tip joints, riser and support contacts, red side insets, lower panel/frame and stiffeners, plus 32 sampled flange roots on each of the two curved-body fittings. It verifies local/deformed-centre UVs, twelve planar caps, eight packed source image byte hashes, decoded colour/roughness pixel equality and material export quantization. These are scoped contact samples, not exhaustive mechanical proof.

Matched-camera whole-object, body-detail and base-detail render pairs verify silhouette, alpha and RGB differences. Whole-object views require transparent unclipped framing; macro crops are intentional. The target runtime for this standalone model milestone is Blender native/imported GLB; no client renderer integration changes are included.

## Remaining acceptance work

This remains a reference-refined study rather than final high-detail artistic acceptance. Surface finish and the exact upper/lower proportions need further quality review; rear engineering, operational/damage presentation and game scale/orientation/placement are unresolved. No rotation or mechanism animation is invented from reveal phases. Construction scaffolding stays deferred under #983. No final review-ledger gate is promoted.

Native/imported verification passed in Blender 4.5.15 for the final 34-object, eight-material study. Eleven render views passed framing and three matched-camera pair checks with identical threshold-128 silhouettes and alpha. Full inventory verification passed for 303 definitions and 1444 reference occurrences. Required changed-code quality verification passed against milestone base `eeeec951`.
