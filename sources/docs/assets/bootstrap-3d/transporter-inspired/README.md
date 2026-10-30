# Original-inspired transporter study

Tracked in [#941](https://github.com/ender-dev-pl/ed-openfa-game/issues/941).
This sibling variant preserves the previous generic transporter in `../models/`.
It is an original procedural mesh study, not an extracted model or texture bake.
It is not automatically substituted into the game.

## Reference evidence

The package identifies `openfa:transporter` as ship profile 05 in
`content/standard/presentation/legacy-domain.json`. Its matching catalogue entry
in `content/standard/catalogues/legacy-gameplay.json` specifies preview
`PS05.256`, surface sprites `PS5C.256`/`PS5A.256` and atmospheric variants.

Initially inspected the decoded `PS05.VID` turntable at frames 0, 10, 20, 30,
40 and 50, plus `PS5C.256` surface frame 0. A subsequent review covered all 60
inventory frames and selected frame **12** for the forward opening and frame
**35** for the exhaust arrangement (zero-based indices). Revision 2 corrects the
earlier two-main-engine interpretation to **one large central nozzle and two
small side nozzles**, and replaces the shallow forward glazing with a real
cutout, recessed floor/bulkhead and overhanging top spine.
Revision 3 replaces the smooth ellipsoid prow and rear shoulders with flat-faced
cross-section meshes, a wedge-shaped nose and narrow single-segment edge chamfers.
The corrected three-nozzle arrangement and actual forward opening are retained.
The preview export manifest records
embedded-palette decoding and source SHA-256
`310ab9c2267bba0d69a1b5eafecb3cfdb5d2b14d28aee60038d9e1c85fcfa32a`.
Local reference/contact sheets are retained under `artifacts/issue-941-transporter/`;
the original pixels are not included in this model directory.

Confirmed visible features used for the new silhouette:

- Broad compact cargo body with sloped sides and continuous red side markings.
- Separate flattened nose on a narrow forward connection.
- Raised longitudinal top structure and small dorsal aerial.
- A dark front opening below the overhanging top structure.
- Rounded broad rear engine shoulders with one large central and two smaller
  lateral orange exhausts, clearly resolved by inventory frame 35.

Exact cross sections, hidden underside, panel seams and nozzle construction are
authoring choices inferred from the views. The forward opening is modelled as
an unglazed recess; its original function is not established by these images.
Lighting and material colours are authored approximations, not sampled textures.

## Reproduce and inspect

From the repository root:

```powershell
& C:/tools/blender/openfa-blender.ps1 -Background `
  -PythonScript tools/blender/build_transporter_inspired.py
& C:/tools/blender/openfa-blender.ps1 -Background `
  -PythonScript tools/blender/verify_transporter_inspired.py
```

`transporter.blend` retains named editable parts, bevels, materials, camera,
lighting and a marked asset collection. `transporter.glb` contains model geometry
and materials. Six transparent 768x768 Cycles CPU renders show front/rear quarter,
side, front, rear and top views. `manifest.json` records the generator and render
parameters; `preview.jpg` is a review contact sheet derived from these renders.
The verifier checks nozzle count, centring, relative size and bilateral placement,
and ray-casts through the hull opening to reject a merely painted surface.

The generator overwrites only this study's known deliverables. Save manual edits
to another filename before regenerating. Directional game sprites, animation,
damage/construction stages and final in-game proportions still require separate
artwork integration and runtime review.
