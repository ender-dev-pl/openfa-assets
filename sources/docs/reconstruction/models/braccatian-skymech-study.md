# Braccatian SkyMech — first authored iteration (#1011)

`openfa:ship/braccatian/skymech`, global type 19, Braccatian local type 4, role class 7. The gameplay catalogue supplies the orbital-shipyard tag and zero speed. The authoritative inventory had no registered source study. This creates a missing first source and preserves previous reconstructions/refinements; artistic refining remains deferred.

## Source evidence

BR4C.256 contains two correctly paletted fixed-state sprites, 91×96 and 107×131 pixels. They are not a heading bank or independent cameras. State 0 shows a ribbed axial column, rounded gold upper cap, gold lower taper/rose rim, lateral rose/gold disc-like modules, thin axial projections and warm red/amber inset features. State 1 has a larger wireframe-like presentation whose meaning is unresolved. It does not establish an opaque pyramid, deployment mechanism, construction scaffolding or animation timing. No catalogue video is located; BR4A is absent.

The functional text index maps the name but no narrative. Five equipment slots have no recovered mount coordinates; metadata binds the catalogue hash and records five declared slots / zero calibrated 3D mounts. Neither the four authored radial modules nor AlignmentAxis are assigned to those slots. The helper's local +Z axis is authored and uncalibrated. The shipyard tag does not establish the mechanism or function of individual visible panels/modules.

The original ENGLISH.CDB Braccatian Architecture article, record 47 at 0x2142, supports decorated building surfaces as contextual guidance. Its use for this orbital structure's gold/rose banding and framed service treatment does not prove geometry, heraldry or hidden machinery. No clan insignia is invented. Correctly paletted original pixels remain reference-only and are absent from all mesh/texture inputs. Metadata binds cultural/reference indexes, catalogue, generators and helpers.

## Independent assembly

`docs/assets/reconstruction/ships/braccatian/skymech/` contains editable Blend/GLB, four independent gold/rose colour and roughness maps, provenance, actual render gallery and technical reports. The 74 closed meshes/five materials comprise a dark axial core, gold upper dome/lower cone, two rose cap rims, a rose equatorial collar, three gold core bands, sixteen separate column ribs, four rose radial modules with gold faces/rims and small fittings, four radial arms with housings/insets/twelve amber tiles, a curved upper panel with five amber tiles, two aerials and a crown hatch.

Four radial modules and eight ribs per column half are authored interpretations of partially obscured fixed-state geometry, not recovered counts or mounting transforms. Dark recessed core surfaces sit behind actual ribs; the structure is not an empty wireframe or solid replacement pyramid. Separate annular bands wrap the core/ribs, and the lateral modules have independently authored hidden backs and arm connections. Amber tiles use solid rough materials, without invented operating-light animation.

Two shallow cap dents and four local module dents, analytic stains, grain and seeded scratches supply new-object wear. Two packed image materials cover 44 meshes; oxidized service alloy, carbon-dark recesses and amber inserts use rough authored solid materials. Bevels precede local box UV assignment. Explicit corner normals preserve native/imported shading. All components remain separately editable under PlacementRoot; no previous model is regenerated.

## Verification scope

The verifier reopens native Blender and independently imports GLB. It checks closed positive geometry, exact geometric vertex counts after diagnostic-only 1e-6-unit imported seam welding, actual corner normals within 0.001, transforms/bounds, source/helper/binary hashes, packed image bytes and decoded colour/roughness/material parity, local box UVs and six measured dents.

Contact checks use actual odd/even shell-crossing containment, including concave annular voids, rather than a near/far bounding envelope. Explicit void witnesses keep all annular axes clear. Other checks cover cap/core overlap, cap rims/equatorial collar/core bands, 56 rib/core/cap/band samples, arm/core/collar/module links, module face/rim/fitting joints, housings/insets/tiles, 54 curved upper-panel samples and aerial/hatch attachments. These are scoped samples, not exhaustive structural proof. Four root orientations include pitch/roll as well as yaw, so the axial helper's position/direction genuinely changes; no source animation is claimed.

Actual native/imported Blender renders exercise the standalone modelling runtime. Whole-object framing, intentional detail crops and matched-camera alpha/silhouette/pixel checks remain separate from artistic acceptance. Both original fixed-state crops are retained in ignored reference comparison evidence, with explicit fixed-state labels. Game-client integration is unchanged.

## Deferred

Final proportions/finish, module/rib count and spatial arrangement, hidden backs and mechanisms, exact panel meanings, the second fixed state's presentation, five calibrated equipment mounts, runtime scale/orientation and required operational/damage states remain unresolved. Technical correctness does not accept final art or state completeness. Artistic refining and construction scaffolding (#983) remain deferred.

The actual gallery and both fixed-state references were inspected. First-version verification passed in Blender 4.5.15 for 74 meshes/five materials, including 44 mapped meshes. Major cap dents measured approximately 0.00574/0.00588 model units; four module dents measured about 0.00294 each. Maximum actual corner-normal vector error was 0.000565 (bound 0.001). Nine rendered views passed framing/export checks: both threshold-128 silhouettes are identical; front-quarter/detail alpha differences affect three/one edge pixels respectively, maximum 4/255, within existing tolerances. Maximum foreground mean colour difference is below 0.004/255. Cultural-source validation passed for six architecture articles; inventory verification passed for 303 definitions / 1444 reference occurrences. Required changed-code quality verification passed against milestone base `9d44df18`. All five Braccatian ship definitions now have registered first source studies; this is not final artistic, attachment or variant acceptance. Existing models were not regenerated or refined.
