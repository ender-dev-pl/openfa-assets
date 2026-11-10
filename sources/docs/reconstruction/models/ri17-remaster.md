# RI17 Arms Unit: canonical open annular factory

Tracking: openfa-assets #253 and per-building #50. Preserve ID `openfa:building/legacy/056`, definition class 7, footprint 3x3 and construction updates 30. Original function record 917 identifies a weapons factory and describes Rigellian reluctance toward aggression; culture record 18 supports elegant ergonomic architecture. Neither description establishes visible operating machinery.

## Actual references and concept feedback

Correctly paletted surface and catalogue phases 0/10/20/30/40 show a low grey annular casing with an open recess, green interior element, red inner-wall detail, underside ribs and green mast with bronze crown. The enlarged surface crop cuts off the top; the complete catalogue colour frame was therefore also used. Reveal/highlight is not rotation or mechanical motion. Current directional selector excludes ID056. Shared RIS3 construction remains separate; no hangar, silo or closing lid is inferred.

Two actual built-in ImageGen requests were used within the limit of three. Attempt 1 returned no image after output moderation. Attempt 2 produced `gallery/media/concepts/rigellian/ri17-review-2.png`; exact prompts and failed-attempt identity are retained. It preserves the main anatomy but enlarges the recess, changes the interior cap and adds mast collars/panel hardware. Those departures are rejected in favor of the current source-guided proportions. Original pixels remain private and are not model textures or mesh inputs.

## Preserve the newer crown

The base is the latest crown-refinement study, not the older single bulb/spike model. Six protected body/crown components retain exact evaluated geometry: annular casing, mast, interior unit, two broad tapered lateral arms and central stem. The arms retain a broad middle, narrowing tips, open intervals beside the central stem and shallow authored shaping. Three original body dents, assembly floor, twelve underside ribs, roof fitting and red panel remain. Exact arm thickness, hidden sections and rear engineering are interpretations. Existing wear is subtler than the concept, without a dense panel grid.

There is no geometry reduction in this milestone. Current budget is 43,692 triangles, 23 editable physical components, eight used materials and ten embedded images. Old bronze-head textures are not required by the exported current crown; the current crown uses its own authored colour/roughness maps. This cost does not establish batching or Android frame rate.

## Actual saved-native and independent GLB checks

Blender 4.5.15 reopened the saved native file and independently imported GLB. All 23 welded meshes are closed and positive. Unrelated prior body checks remain: three radial/casing dents, open recess and low floor, interior/floor contact, mast/casing placement, twelve underside-rib roots, red panel/frame/wall contacts, 32 roof-fitting flange-root samples and embedded face. A connected sampled contact graph supplements local rays without claiming exhaustive intersections.

The removed bronze-head dent/UV/overlap assertions are replaced specifically by the current tapered-crown form contract, mast/central-stem overlap and two additional arm/central-stem root rays. Full original green/grey colour/roughness pixels, cylindrical/planar UVs and six remaining planar ends pass. Both current crown colour/roughness maps are decoded and compared; the imported packed roughness green channel is compared with the native scalar channel. Protected geometry error is zero; native/import surface deviation is below 0.000000067 source units.

Three actual view pairs were inspected. The case-specific verifier expands whole-object framing by eight percent, leaving shared tools already bound by previous deliveries unchanged. All alpha and threshold silhouettes agree exactly; margins are at least 42 pixels and foreground RGB means below 0.397/255. This preserves the earlier whole-object framing contract without reducing it. Detailed metrics remain in `visual-review.json`; RGB is not claimed identical.

Actual GLB retains the newer crown, source-guided recess and current interior element rather than the concept's added collars and hardware. Hidden engineering, exact proportions, damage/operational variants, client calibration/state integration, performance and final user artistic approval remain separate. Unfinished mobile-ship programme #248 is not completed here.

## One current payload, reproduction and disk

Use `sources/objects/rigellian/arms-unit/model.blend` and `model.glb` across gameplay, build menu and SciTek. Earlier bootstrap, initial reference study and crown study remain historical, outside the single current selection. Identity `PlacementRoot`, Blender -Y forward, +Z dorsal, ground Z0. Bounds approximately [-1.02, -1.019065, 0] to [1.02, 1.02, 2.32]. Nominal footprint does not calibrate game placement. Export is static with no clips.

Run `remaster_rigellian_static.py` with Python exit code 1 and `-- --recipe sources/objects/rigellian/arms-unit/recipe.json`; verify through `verify_remastered_rigellian_arms.py` with the same recipe to retain wider framing. This wrapper runs the unchanged shared saved-native/imported verifier. Review renders, register the canonical selection, rebuild galleries and run repository checks. Reports bind binaries, recipe, actual imported helpers/wrapper, concept/prompt and render bytes. Reuse the existing checkout without another build/archive/worktree; remove only verified task-owned temporary output after use.
