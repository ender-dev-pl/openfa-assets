# Spy Satellite — first authored iteration (#1001)

`openfa:spy-satellite`, Terran type 9. The authoritative inventory contained no source model. This first iteration preserves existing reconstructions/refinements; further artistic refining remains deferred.

## Function and reference evidence

ENGLISH.TXT at 0x17781 states that a satellite orbiting an asteroid continuously transmits surface video. `ship-reference-index.json` binds the single correctly paletted PS9C surface sprite and sixty-frame PS09.VID catalogue animation. Actual sampled phases 0/15/30/45/59 show a wide green dome, banded narrow stem, lower rounded observation module, small lateral plates/probes and changing lower details. These phases do not establish a complete rigid-body rotation. Lamp/state timing and exact movement remain unresolved.

Original pixels are reference-only and absent from mesh/texture inputs. Hidden cross-sections, camera axis, mounting detail and plate function are independent interpretations. The lateral opaque plates are not asserted to be photovoltaic. No hardpoint/equipment slots are declared for this catalogue entry, and none are invented.

## First authored assembly

Editable Blend/GLB, four independent green/bronze colour and roughness maps, provenance, technical report and render gallery are under `docs/assets/reconstruction/ships/terran/spy-satellite/`. Thirty-one meshes and five materials form separate editable dome and combined stem/lower globe, three stem bands, one dome band, crown cap, two supported lateral plates with dark strips, two lower probes, sensor bezel/dark face, lower aerial/collar and rim fasteners.

Two measured physical dents, analytic stains, grain and seeded scratches implement new-object wear. Small details use independent rough alloy/soot material values. Bevels precede local box UV assignment. SensorAxis is a single authored uncalibrated optical helper using local +Z forward, parented to the local +Z station assembly axis. It is not an equipment slot or proof of the original camera mount.

## Verification scope

The verifier reopens native Blender and imports standalone GLB separately. Native physical meshes must be closed with positive volume. Diagnostic-only seam welding at 1e-6 units must recover closed geometry with exactly the native geometric vertex count for every imported part. Original files are not mutated. Other checks cover bounds/transforms, source/helper provenance, packed image bytes and decoded colour/roughness pixels, UV projections, two dent depths, shared interior contacts for stem/dome, all four bands, plate supports, lower probes/aerial and crown. The sensor bezel has 32 flange-root samples and a face/rim overlap check. SensorAxis position/direction is checked under four rigid root rotations, without claiming that this establishes legacy animation timing.

Actual native/imported Blender renders exercise the standalone runtime. Whole-object framing, intentional sensor-detail crops and matched-camera export comparisons are kept separate from artistic acceptance. Samples are scoped correctness evidence, not exhaustive structural proof. Game renderer/integration is unchanged.

## Deferred

Exact dome/body proportions, additional source surface detailing, sensor/light state semantics and animation timing, hidden surfaces, calibrated game scale/orientation and final artistic acceptance remain for later passes. No final artistic gate is promoted. Construction scaffolding remains separately deferred under #983.

Initial render comparison exposed different flat/smooth-face treatment after GLB import, especially on bronze bands. A saved-native diagnostic preserved every corner-normal vector, set all faces smooth and restored those vectors as explicit custom normals. Against the existing imported render, full-view mean channel error fell from approximately 1.705/1.400/1.287 to 0.00161/0.00132/0.00131 out of 255 without changing geometry or shader inputs. The generator now uses this explicit shading contract after bevel application. Verification requires explicit custom normals on every authored mesh and compares actual native/imported corner vectors at corresponding positions. This is export correctness work on the new first iteration, not artistic refining or a retrofit of older models.

The normal comparison also accounts explicitly for Blender custom-normal storage quantization: the maximum permitted vector difference is 0.001 (about 0.057 degrees), with the diagnostic observing approximately 0.000634. Imported meshes may optimize flat-face normal storage; actual corner vectors, rather than the importer storage flag, are compared. This bound does not alter the render comparison threshold.

Final first-version checks passed in Blender 4.5.15 for 31 meshes and five materials. Nine actual views passed framing/export comparison. Both matched-camera alpha channels and threshold-128 silhouettes are identical. Foreground mean channel differences are below 0.002/255 in the full view and below 0.00062/255 in the sensor macro, using the unchanged 1.5/255 render bound. Inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `ec2ceb46`. Existing models were not regenerated or refined.
