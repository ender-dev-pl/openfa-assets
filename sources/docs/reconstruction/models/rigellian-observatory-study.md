# Rigellian Observatory — first authored iteration (#1006)

`openfa:ship/rigellian/observatory`, global type 14, Rigellian local type 4, catalogue role class 7. The authoritative inventory had no registered source model. This creates a missing first version; existing reconstructions and refinements are preserved, and artistic refining remains deferred.

## Evidence and interpretation

RI4C.256 has two correctly paletted fixed-state sprites (94×126 and 153×136 pixels), not a heading bank. No catalogue video is located. State 0 shows a broad slate saucer, horizontal copper rim and round lateral joints, a dark oval central face, green/copper axial chambers, fine axial aerials and separate pointed upper/lower fins with dark gaps between them. State 1 has a blue wireframe-like presentation; its meaning is unresolved. It is neither an independent camera nor proof of an opaque cone, construction scaffold, physical deployment mechanism or animation timing.

The functional text index maps the name but no narrative for this object. Four equipment slots are declared in the authoritative catalogue, but no designer mount coordinates or recovered 3D socket transforms are provided. The single AlignmentAxis helper is explicitly authored and uncalibrated; it does not stand in for four validated mounts. Optical, weapon and communications functions of individual surface features are not established.

ENGLISH.CDB Architecture record 18 at 0x971 supports ergonomic/elegant Rigellian construction as contextual guidance. The cultural index hash and source reference are bound in model metadata. The prose does not establish this object's proportions, materials or hidden parts. Visible colours and principal forms follow the paletted sprite; hidden depth, radial fin count, maintenance treatment and precise joint sections are independent interpretation. Legacy pixels are reference-only, never texture or mesh inputs.

## Independent assembly

`docs/assets/reconstruction/ships/rigellian/observatory/` contains editable native Blend and GLB, six independent slate/green/copper colour and roughness maps, provenance, actual rendered views and technical reports. The first assembly uses a closed elliptical saucer, continuous axial chamber profile, copper equatorial ring and seven axial collars, eight separate pointed radial fins, eight chamber rails, paired aerials/collars, body-fitted service plates/insets, a curved-root oval central casting/face with three small markers, and two curved-root lateral copper bosses/caps.

Two shallow geometric dents, analytic stains, grain and seeded scratches supply wear. Bevels precede local box UV assignment. Explicit authored corner normals preserve the shading contract across export. PlacementRoot uses an authored local +Z axial orientation. Parts remain separate and editable; no original texture or geometry is imported.

The equatorial casting includes the actual hull profile break at z=0: joining only the two end radii would bury its middle in the maximum-radius hull. This is a technical contact correction within the first iteration, not an artistic refining pass. Oval bezel roots are ray-fitted again after their elliptical transformation to preserve contact with the actual saucer.

Two lateral cast-root bevels cross that sharp equatorial break. Sub-micron bevel slivers are merged/dissolved in these two new authored meshes before normals and UVs are assigned. This prevents the diagnostic imported seam weld from changing the actual geometric vertex count; the exact-count requirement remains intact.

## Verification scope

The verifier reopens native Blender and independently imports GLB. Every native physical mesh must be closed with positive volume. Diagnostic-only 1e-6-unit seam welding accounts for imported UV/normal vertex splits and must recover the exact native geometric vertex counts. Other checks cover bounds/transforms, source/map hashes, packed image bytes and decoded colour/roughness parity, all three image materials and 42 mapped meshes, actual corner normals within 0.001, both dent depths, shared interior hull/chamber and aerial/collar contacts, eight fin roots and copper rails, fitted service panels, 32 oval-root samples and 64 lateral boss-root samples, plus face/cap/marker overlaps. These samples are scoped contact evidence, not exhaustive structural proof.

AlignmentAxis is checked under four rigid root rotations. No source animation or equipment calibration is claimed. The gallery uses actual native and imported-GLB Blender renders, whole-object framing and intentional detail crops. The comparison sheet retains both original fixed states only in ignored reference evidence. Matched-camera alpha, silhouettes and foreground pixel differences are checked separately from artistic acceptance. Game-client integration is unchanged; the runtime check is scoped to these standalone modelling assets.

## Deferred

Final proportions and artistic acceptance, exact fin count/arrangement, hidden saucer depth, detailed finish and source markings, the second fixed state's meaning/presentation, calibrated scale/orientation, four equipment mounts and any required operational/damage variants remain unresolved. This first source does not accept those gates. Construction scaffolding remains separately deferred under #983.

First-version verification passed in Blender 4.5.15 for 63 meshes and six materials, including 42 meshes using authored image maps. Both dents were measured (approximately 0.00567 and 0.00380 model units). Maximum actual native/imported corner-normal vector difference was 0.000924, within the 0.001 custom-normal quantization bound. Nine actual views passed framing/export comparisons: both matched-camera alpha channels and threshold-128 silhouettes are identical, with maximum foreground mean channel difference below 0.002/255. The actual gallery and both original fixed states were inspected; exact fin arrangement, proportions and fine markings remain later artistic questions. Cultural-source validation passed for six architecture articles, and inventory verification passed for 303 definitions / 1444 reference occurrences. The required changed-code quality gate passed against milestone base `71413d59`. All five Rigellian ship definitions now have registered source studies; this is first-source coverage, not final acceptance or state/attachment completeness.
