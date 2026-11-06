# RI14 Energy Gatherer — initial reference-refined study (#986)

Catalogue ID `openfa:building/legacy/053`, global type 53, nominal 2x2 footprint. This newly authored model fills a missing study; existing reconstructed/refined assets are preserved.

## Function before geometry

Original ENGLISH.TXT record 914 at byte offset 0x11501 identifies power generation and explicitly leaves the method undisclosed. The correctly paletted 19x54 surface body and readable catalogue phase show a two-chamber bronze lower body, long silver front conduit, tapered grey connector, bronze upper vessel and an upturned silver crown with central tip. Reveal/highlight phases do not establish rotations, moving machinery or an operational effect.

Exact hidden geometry, rotational cross-sections, crown depth, fourfold upright arrangement, internal floor, conduit-retaining shoes, service panel construction and fasteners are independently authored interpretations. The source supports feature placement and broad proportions, not those hidden engineering details. No solar array, exhaust or reactor mechanism is inferred from the functional name. Original pixels are reference-only, absent from texture and mesh inputs.

## Render/refinement evidence

The first actual render showed a bronze vessel cap protruding above the crown floor. The floor now covers that cap while remaining joined to the lower crown casting. Round posts were replaced by angular outward-flared rim uprights, making the edge read as part of the crown rather than additional antennae. Their exact count and hidden placement remain inferred.

The open-crown check initially demanded that a vertical ray never meet any part of the casting, including below the bowl floor. That was the wrong contract for an open bowl with a bottom. The revised check samples three radii and requires no crown closure above the actual floor surface. Assembly contacts are sampled within overlapping volume, avoiding a ray placed exactly on a floating-point boundary plane.

Four main radial bodies have actual shallow geometric dents. Independent analytic colour/roughness maps add joint contamination, handling marks, grain and seeded scratches for bronze and grey materials. Planar caps use separate maps. The crown inner/outer walls and end rings have explicit UVs; legacy images are not read by the authoring scripts.

## Deliverables and target-runtime checks

`docs/assets/reconstruction/buildings/rigellian/energy-gatherer/` contains editable Blender source, standalone GLB, eight authored source maps, metadata and native/imported technical/render reports. Eleven actual 900x900 renders include matched-camera whole-object, crown-detail and base-detail pairs. Original comparisons stay in ignored `artifacts/rigellian-building-reference-study/RI14/comparison.png`, outside distributable model assets.

The verifier reopens native Blend and imports GLB independently. It checks closed positive topology, identity root, footprint/bounds, per-object transforms/bounds, four geometric dents, body/connector/vessel/floor/probe joints, crown/floor/upright overlap, open bowl above the floor, four conduit retainers, lower panels and upper-vessel insets. It also verifies cylindrical and planar UVs, ten planar caps, packed source-image bytes, decoded colour/roughness pixel equality and material export quantization. These are scoped samples, not exhaustive mechanical proof.

Whole-object renders require transparent unclipped framing. Intentional macro crops are labelled. Matched pairs require identical threshold-128 silhouettes and bounded alpha/RGB difference. This standalone asset milestone uses Blender native/imported GLB as its target runtime; it does not change or verify client integration.

## Remaining quality/acceptance work

This is a reference-refined study, not final high-detail artistic acceptance. Upper-vessel/crown proportions and manufactured finish need further review against available evidence. Rear details, operational/damage presentation and game scale/orientation/placement remain unresolved. Construction scaffolding stays explicitly deferred under #983. No final review-ledger gate is promoted.

Final study verification passed in Blender 4.5.15 with 36 mesh objects and seven materials. Eleven render views passed framing and all three matched-camera comparisons have identical threshold-128 silhouettes and alpha. The full 303-definition / 1444-reference inventory and required changed-code quality gate passed against milestone base `26f63b15`. Actual source/render comparison keeps upper vessel and crown proportions open for further refinement.
