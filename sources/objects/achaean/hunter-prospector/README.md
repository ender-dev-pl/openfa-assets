# Achaean Hunter/Prospector remaster

Canonical identity `openfa:ship/achaean/hunter-prospector`, global37/local0, issue [#238](https://github.com/ender-dev-pl/openfa-assets/issues/238), PR [#239](https://github.com/ender-dev-pl/openfa-assets/pull/239). Use the current Blend/GLB consistently in gameplay, build menus and SciTek. The completed first source remains unchanged under `sources/docs/assets/reconstruction/ships/achaean/hunter-prospector/`, historical and excluded from current packaging selection. The rejected horizontal-fork remaster remains recoverable in commit de66138148d53a6549d24b161dd9e85cf78dd38b; it is not a competing current model.

## Corrected construction

The user's three-view construction sketch supersedes the earlier generated concept: two thin upright crescent wings, one on each side of the continuous green central hull, both opening aft. The side view reveals a complete C profile; the top view shows two narrow rails alongside the hull. Short lateral links connect wings and body. The previously inferred ochre third trailing spar was incorrect and has been removed. Warm colour fields are interpreted as hull/fitting accents rather than a separate structure. The user's sketch supplies architectural direction, not exact dimensions or recovered mechanical detail.

All32 correctly paletted `_S/_S:AC0A.256` headings were reviewed again against this interpretation. AC0C is absent from current bindings. The tiny9–21-pixel source supports broad colour placement and silhouettes but leaves exact thickness, nose sections, spacing, hidden structures and source-heading calibration unresolved. No part is labelled as a proven weapon, mining device or engine. The source archive member hash and frame hashes remain in `reference-evidence.json`; original pixels are reference-only and never model textures or published authored media.

The full `_MA` directory/archive survey found PB, PH, PM, PS and ST families and91 preview members. No Hunter/Prospector video or object-specific narrative is mapped by the ship-reference bindings. Achaean Architecture, ENGLISH.CDB record166 at0x9d65, supplies curved-form cultural context, not proof of vehicle domes or mechanisms. Two equipment slots remain uncalibrated.

The supplied sketch is now the gallery concept. No additional ImageGen iteration was needed; both prior generated concepts are historical rejected interpretations. Exact sections, small covers, plate seams, links and physical/material wear remain authored. Broad red crescent surfaces, silver edges and green worn metal retain quiet surfaces and restrained service detail rather than a dense grid. The crescent edge colours belong to the same watertight topology as each wing, avoiding overlapping rim surfaces and tip intersections. The fighter/transporter models and shared maps/helper are unchanged.

## Budget and verification

The corrected source has25,806 triangles,12 mesh batches,2 materials and4 packed maps: two unchanged shared2048-square maps and two own1024-square green maps. Approximate decoded RGBA texels total40MiB before mipmaps/compression; actual client GPU cost remains to be checked. Current reports supply the exact measured export counts and hashes.

Local forward-Y/up+Z, native maximum extent18. Proposed client world size40 remains an authored small-scout relationship to fighter96/transporter180, not recovered metres or an applied override; current generic fallback96 needs separate integration review. There are no calibrated sockets or operational animations.

Verification reopens the cleaned saved Blend and independently imports/renders the actual GLB in Blender4.5.15. It checks closed nonzero core geometry, source/import coordinate and triangle equivalence, packed maps, eight empty aft-mouth and eight occupied crescent samples in each representation, absence of a separate trailing spar, and a height/thickness ratio demonstrating upright thin plates. Matching imported geometry supplies technical wireframe and heading previews. Native/import pixel equivalence and framing are checked separately. Exact view calibration and artistic fidelity are not inferred from technical tests.

Both galleries select this single current source/export pair with corrected previews and the supplied construction sketch. Final user artistic review and actual game-client scale, orientation, lighting, attachments and performance acceptance remain separate.
