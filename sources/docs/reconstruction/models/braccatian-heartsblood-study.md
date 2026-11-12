# Braccatian HeartsBlood — first authored iteration (#1009)

`openfa:ship/braccatian/heartsblood`, global type 17, Braccatian local type 2, role class 5. The gameplay catalogue supplies transporter, ore/missile transporter and combat-direct-approach tags. The authoritative inventory had no registered study. This creates a missing first source while preserving all previous reconstructions/refinements; artistic refining remains deferred.

## Source evidence and reuse

BR2C.256 has 32 entries: 16 populated even headings, approximately 53–81 pixels wide and 40–42 pixels high, and 16 empty odd entries. Inspection distinguishes empty entries from failed exports. The runtime explicitly uses even heading samples. No larger catalogue video is located; BR2A is absent.

The paletted headings show gold/rose main forms, a circular rose nose and four dark round aft openings resembling BR1C. HeartsBlood adds four longitudinal rose radial modules with three gold bands each, replacing the broad grey armour/strakes. Exact proportions, hidden sections and end-fitting function are not fully recovered. This similarity supports authored shared-body reuse, not a claim that the original executable used shared 3D geometry.

Twenty-four already independently authored OpenFA objects are appended from the committed WidowMaker Blend: pressure hull, nose, nose casting/face/studs, aft housings/floors and neck accents. No prior model is rebuilt or modified. The new metadata binds the source Blend and metadata hashes, exact source object list and independent helper sources. A verifier opens that source separately and compares exact vertex/face signatures and object transforms with the new native source. Shared source geometry is preserved; new-model maps and pod assemblies are independently authored. Original game pixels remain reference-only.

The functional text index maps the name but no narrative. Six catalogue equipment slots have no recovered mount coordinates. Neither the round openings nor four added modules are assigned to those slots. The aligned local -Y helper is authored and uncalibrated. Transport tags do not prove opening doors, cargo compartment arrangements, engine function or loading animation.

ENGLISH.CDB Braccatian Architecture record 47 at 0x2142 provides contextual support for decorated surfaces. It does not establish spacecraft geometry, heraldry or hidden mechanisms. The first model retains independently drawn neck accents and uses functional gold clamps/cradles; no clan insignia is invented. Cultural/index hashes are bound without changing existing models.

## New assembly

`docs/assets/reconstruction/ships/braccatian/heartsblood/` contains editable Blend/GLB, six independently authored rose/gold/grey colour and roughness maps, provenance, actual renders and technical reports. The 56 meshes comprise 24 reused authored meshes and 32 new meshes: four closed lathed pod bodies, twelve closed annular clamps, eight closed terminal fittings and eight radial cradle supports.

The four new pod profiles have independent shallow outward dents. Clamps embed into the pod bodies. Each cradle has shared interior contact with the central hull and pod, while the fore/aft fittings embed into the pod ends. Existing independent hull/nose dents remain intact. Three packed image materials cover 50 meshes; oxidized titanium and carbon-dark recesses use authored solid rough materials. New analytic stains/grain/scratches are authored for this model; source materials/images are local copies, and the source Blend is unchanged.

Only newly created meshes receive topology orientation and bevel application. Shared meshes keep their existing finished geometry and normals. Stable local box UVs and explicit corner normals support export parity; all meshes remain separately editable under a fresh PlacementRoot.

## Verification scope

Native/imported checks cover closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, transforms/bounds, actual corner normals within 0.001, source/helper/binary hashes, packed image bytes and decoded colour/roughness/material parity, UVs and all six measured dents. Additional tests sample the inherited neck accents, nose/body and cast-root/stud joints, open aft housing axes/recessed floors, twelve pod/body points, 48 clamp roots, eight terminal fittings and sixteen cradle endpoints. Geometric signature checks independently prove preservation of the 24 source objects in the native asset; imported topology uses the separate triangulation/seam-aware checks.

AlignmentForward is tested under four rigid root rotations. No operating animation or calibrated mounts are inferred. The standalone modelling runtime is exercised by actual native/imported Blender renders and matched-camera framing/alpha/silhouette/pixel checks. Eight populated reference headings are compared qualitatively; the full bank inspection and original crops remain ignored reference evidence. Game-client integration is unchanged.

## Deferred

Final silhouette/proportions and finish, shared-body fidelity, exact pod/end/collar forms and attachment construction, hidden mechanisms, six calibrated equipment mounts, runtime scale/orientation and required transport/damage states remain unresolved. Technical correctness is separate from final artistic acceptance. Artistic refining and construction scaffolding (#983) remain deferred.

The actual gallery and paletted-heading comparison were inspected. First-version verification passed in Blender 4.5.15 for 56 meshes/five materials, with 50 mapped meshes and exact native geometry signatures preserved for all 24 reused objects. Four new outward pod dents measured approximately 0.00385 model units each, alongside the two retained source dents. Maximum actual corner-normal vector error was 0.000636 (bound 0.001). Nine rendered views passed framing/export checks: both threshold-128 silhouettes are identical; front-quarter/detail alpha differences affect one/four edge pixels respectively, at most 4/255, within the existing tolerance. Maximum foreground mean colour difference is below 0.002/255. Cultural-source validation passed for six architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `2372b756`. No previous model was modified or regenerated.
