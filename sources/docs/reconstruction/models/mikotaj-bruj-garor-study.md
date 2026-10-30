# Mikotaj Bruj-Garor — first low-resolution interpretation (#1068)

`openfa:missile/mikotaj/bruj-garor`, global type 38/local Mikotaj type 8. Catalogue flaming-ruin behaviour, ore units 2, budget cost 50 and production investment/updates 35 are established data, not a visible mechanism. Functional text establishes the name only; no mapped detailed missile narrative is established. Relates to #951 and #946. Existing sources/refinements are unchanged.

## Reference evidence versus interpretation

All fourteen correctly BUTTONS-paletted MKM9.256 flight/launch states were inspected. Flight crop 3 is 8×32 pixels. No management preview is bound; these states are not 3D turntable views. They show a green centre, broad grey end sections, separate grey rails and long copper side details. Exhaust-bearing states provisionally establish a forward end opposite the plume; flight/launch presentation differs and does not calibrate launcher registration. Exhaust/effect pixels are excluded from solids.

The independently authored source interprets these as five profiled bodies: green centre/axial terminals, two grey end sections and two grey rails. Four transverse bridges join the real end sections/body/rails while keeping central side gaps. One finite dark central band and eight fitted pale/green/copper castings interpret the surface details. One service cover/two slots/four fasteners provide authored maintenance detail. Exact sections, rail/bridge counts, relative proportions, colour-field-versus-component interpretation, functions and hidden construction remain uncertain. Flaming-ruin behaviour does not establish visible operating machinery, so none is invented.

The source-anchored Mikotaj ENGLISH.CDB Architecture guidance provides contextual heavy metallic mining-colony direction, distinct from crystalline home-world structures. It does not recover missile geometry, materials or mechanisms. Cultural index hashes are bound in metadata. Actual reference frames guide colour placement and silhouette. Original pixels remain reference-only and absent from geometry/texture-generation inputs.

## Editable assembly and wear

Deliverables: editable Blend/GLB, eight independently authored 1024-square colour/roughness maps, metadata, nine actual views, gallery and technical/render reports. There are 25 closed meshes, six materials, four image materials and eighteen mapped meshes. Five primary bodies contain physical dents. Four actual bridges join the real assembly; one dark annulus has finite walls, and eleven conformal castings/cover/slots follow their owners. Four fasteners align with sampled mesh normals. Copper details also receive independent image-based wear. Primary UVs account for origins/orientations before angular/axial projection; details use local box projection. Applied modifiers/triangulation precede explicit corner-normal capture. Independent periodic grime, stains, grain and issue-seeded scratches provide wear.

AlignmentForward is an uncalibrated local -Y helper, not a recovered launcher socket. This static first source supplies no flight/launch articulation or exhaust asset.

## Scoped runtime and actual review

Blender 4.5.15 native reopen and independent GLB import/render passed in the standalone modelling runtime. Checks cover positive closed topology, exact geometric vertices after diagnostic-only 1e-6 imported seam welding, corner normals, source/helper hashes, packed bytes/decoded pixels, origin-aware primary UVs/detail UVs, materials, hierarchy/transforms/bounds, five measured dents and helper rotation under yaw/pitch/roll. Actual odd/even containment passed 26 assembly contacts, 99 fitted samples, four fasteners, fourteen rail/terminal clearance witnesses, three occupied-body samples, eight exposed-casting samples and two exposed-band samples. Scoped probes do not establish exhaustive mechanical correctness or calibrated attachments.

Measured dents: approximately 0.001957 / 0.001905 / 0.001905 / 0.000800 / 0.000800. Maximum corner-normal export error: 0.0003356. Nine actual views passed framing. Both matched alpha channels and threshold-128 silhouettes are identical; maximum mean foreground RGB difference is below 0.001/255. Actual gallery/source comparison was inspected. Rounded/full grey end sections, elongated green body versus segmented source fields, bridge placement, copper strip placement/extent, relative proportions and flight/launch presentation remain provisional. These are explicit deferred artistic gaps. Original comparisons remain ignored in `artifacts/issue-1068-bruj-garor/`; tracked renders contain independently authored geometry only.

Complete reference proof passed 69 definitions / 966 rebound frames / 11 independent Terran previews, including archive/frame/palette hashes. Cultural index passed six source-anchored sections. Required changed-code quality base: `d851fee1`. Game-client integration is unchanged.

## Culture sheet and deferred acceptance

The existing `review_missile_culture.py --culture mikotaj` tool generated `docs/assets/reconstruction/missiles/mikotaj/catalogue-studies.png` and its hash-bound JSON report from real inventory. All nine sources were present, Blend hashes matched metadata and the actual sheet was inspected. The report's issue 968 identifies the pre-existing sheet-tool origin; this modelling milestone is #1068. Existing models were reused without regeneration. This completes Mikotaj first-source coverage only, not final artistic acceptance.

Final proportions/sections, end-shell/frame/copper-strip geometry, colour/state separation, detail counts/functions, hidden surfaces, propulsion/payload mechanisms, launcher registration, runtime scale/orientation, required flight/launch/damage states and final artistic acceptance remain unresolved. Technical validity does not accept final art. Refining and construction scaffolding remain deferred by user direction.
