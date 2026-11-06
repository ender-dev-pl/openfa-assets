# RI16 Shield Generator — first authored iteration (#988)

Catalogue ID `openfa:building/legacy/055`, nominal 2x2 footprint. This is an initial authored version, not final artistic acceptance. Existing reconstructions/refined versions are preserved.

## Source and function

Original ENGLISH.TXT record 916 at byte offset 0x11624 compares its shield-generation function to the Terran Screen Generator. Correctly paletted surface body (24x49) and catalogue reveal phases show three visible green lower housings, grey feet, slender grey vertical supports and a tall bronze head with lower flange, narrow waist and divided upper section. This does not establish Terran crystals, hidden machinery, moving mechanisms or emission.

Exact profiles, threefold placement, hidden surfaces, radial braces, foot interfaces and captive fasteners are independently authored interpretations. Original pixels are reference-only, absent from authored texture/mesh inputs. Catalogue reveal phases are not rotations.

## First-version implementation

The standalone model has nineteen mesh objects and eight materials. Ten radial parts have actual shallow geometric dents. Independent bronze/green/grey colour and roughness maps add restrained joint contamination, handling marks, grain and seeded scratches. Assembly grooves are actual geometry in the bronze head and green housings. Twelve source maps are packed into the native file/export materials.

Before the user's first-iteration-only instruction, actual comparison led to fuller green housings, a thicker support bundle and a less conical lower head profile. That already performed work is preserved. Further artistic refining is explicitly deferred to a later pass under `programme.json.current_pass`; it is not required to continue filling missing first versions.

## Technical checks

The verifier reopens native Blender and independently imports GLB. It checks positive closed topology, root/footprint/bounds, individual transforms/bounds, ten measured dents, body grooves/head waist, foot/stem/housing overlap, brace/support/housing overlap, support/head and flange-fastener contacts. It verifies local cylindrical/planar UVs, twenty planar caps, twelve packed source-image byte hashes, decoded colour/roughness pixel equality, material export quantization and reference/function index hashes.

Eleven actual 900x900 views include matched-camera whole-object, head-detail and base-detail pairs. Whole-object framing and native/imported silhouette/alpha/RGB comparisons are technical checks, not final artistic acceptance. Blender native/imported GLB is the target runtime for this standalone asset milestone; client integration is unchanged.

Deliverables are in `docs/assets/reconstruction/buildings/rigellian/shield-generator/`. Original comparison pixels remain under ignored `artifacts/rigellian-building-reference-study/RI16/`, outside distributable assets.

## Deferred work

Artistic refinement, exact reference proportions/finish, hidden engineering, operational/damage variants and game scale/orientation/placement remain open for later passes. No final review-ledger gate is promoted. Construction scaffolding remains separately deferred under #983.
