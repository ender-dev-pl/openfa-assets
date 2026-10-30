# Artemian Hardcore — first authored iteration (#1021)

`openfa:ship/artemian/hardcore`, global type 29 / Artemian local type 4, role class 5. Catalogue tags establish an ore/missile transporter with armour 90 and AI construction cost 45. No registered source study existed. This adds a missing first source while preserving previous reconstructions/refinements. Artistic refining remains deferred.

## Source evidence

AR4C.256 contains 16 populated even headings and 16 empty odd headings, consistent with runtime even-heading selection. All populated frames were inspected with their embedded original palette, including enlarged 0/4/12/28 crops. Sprites range approximately 66–124×20–29 pixels. They support two gold/brown rounded bodies, a silver connecting assembly, small lateral elements, a rear plane and blue-grey details. Eight headings appear in ignored comparison evidence. No catalogue video or mapped functional narrative is located.

The first source interprets the bodies as inline pressure volumes joined by a silver bridge and edge rails, with four lateral modules on short arms, a tail plane, a blue-grey forward interface and two thin aft projections. Exact body sections/spacing, bridge construction, lateral count/geometry, hidden backs and projection calibration remain unresolved. The observed bright areas do not establish operating lights or windows. Five equipment slots lack recovered mount coordinates and default equipment. Visible modules/interfaces are not assigned to those slots or labelled weapons/engines. AlignmentForward is an authored local -Y helper, not a recovered heading or 3D equipment mount.

ENGLISH.CDB Artemian Architecture record 105 at 0x5734 supplies contextual metal/alloy and shell guidance. It does not prove vehicle geometry or require the rounded source bodies to become angular. No insignia or interior architecture is invented. Cultural, functional, reference and gameplay indexes plus authoring helpers are hash-bound. Original pixels remain reference-only and never enter geometry or texture generation.

## Independent assembly

`docs/assets/reconstruction/ships/artemian/hardcore/` contains editable Blend/GLB, four independent colour/roughness maps, metadata, nine native/imported views, gallery and technical reports. The 48 closed meshes/four materials comprise two main pressure bodies, two annular silver trims, a silver bridge/two gold edge rails, four lateral modules/arms, a closed tail plane, fitted fore bezel/blue-grey interface, two aft projections and four service covers/eight slots/sixteen fasteners.

Independent radial profiles define the main/lateral bodies and physical dents; translated vertices retain separate editable meshes. Silver trims are closed annuli with clear axes. Bridge, edge rails and lateral arms overlap their real supporting bodies. The tail uses a closed subdivided planform grid and intersects the aft body. The forward bezel has a ray-fitted embedded root with targeted submicron bevel cleanup. Twelve overlays follow their curved owner profiles, including nested slots, and fasteners align with normals sampled from actual meshes. All parts remain separately editable beneath PlacementRoot.

Six physical dents, independent analytic grime/stains, grain and issue-seeded scratches supply new-object wear. Two packed image materials cover 21 meshes; blue-grey details and carbon-dark seams use rough authored solids. Applied modifiers precede local box UV assignment and explicit corner-normal capture. Existing model sources and shared helpers remain unchanged.

## Verification scope

Blender 4.5.15 reopens native Blend and independently imports GLB. Checks cover closed positive topology, exact geometric vertex counts after diagnostic-only 1e-6-unit seam welding, actual corner normals within 0.001, hierarchy/transforms/bounds, source/helper/binary hashes, packed bytes/decoded texture pixels, box UVs, material parity and measured dents. Main-body dents measure approximately 0.00579 model units each; four module dents measure approximately 0.001985 each. Maximum corner-normal error is approximately 0.000657.

Odd/even mesh containment checks six bridge/body joins, six rail/body/bridge samples, eight lateral arm attachment samples, nine tail/body contacts, 32 trim roots with two clear annular-axis witnesses, 32 fore-bezel roots, a fore interface join, two aft projection roots, 108 fitted-overlay contacts and sixteen fasteners. These scoped contact samples do not establish exhaustive structural or mechanical correctness. AlignmentForward is checked under four rigid root rotations without equipment-mount, source-heading or animation timing claims.

The actual gallery and eight-heading comparison were inspected. Nine rendered views passed framing/export checks: both matched alpha channels and threshold-128 silhouettes are identical; maximum foreground mean RGB difference is below 0.004/255. Actual native/imported rendering exercises the standalone modelling runtime; game-client integration is unchanged. Original crops/comparison remain ignored in `artifacts/issue-1021-hardcore/`; tracked gallery images contain only authored models. Required changed-code quality verification uses milestone base `68d6b66f`.

## Deferred

Final body spacing/proportions, bridge and tail geometry, lateral module count/layout/function, surface/highlight treatment, hidden construction, five calibrated mounts, runtime orientation/scale and required operational/damage variants remain unresolved. Technical validity does not accept final art. Artistic refining and construction scaffolding (#983) remain deferred.
