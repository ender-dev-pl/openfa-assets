# Canonical small-ship construction assets

Issue [#227](https://github.com/ender-dev-pl/openfa-assets/issues/227).
PR #228 replaces the preceding ship and yard payloads; it does not add a parallel
construction-only model catalogue.

| Catalogue id | Single current GLB |
| --- | --- |
| `openfa:assault-fighter` | `sources/objects/terran/assault-fighter/model.glb` |
| `openfa:combat-eagle` | `sources/objects/terran/combat-eagle/model.glb` |
| `openfa:scoutship` | `sources/objects/terran/scoutship/model.glb` |
| `terran:ship-yard` | `sources/objects/terran/ship-yard/model.glb` |

Each GLB has one editable `model.blend` and `model.json` beside it. Neither the
ship `construction/` folders nor yard `hangar/` and `refined/` folders contain
separate model payloads. The old bootstrap yard models and the old exterior-only
ship models were removed too. Render media and old technical reports are retained
as historical evidence, available through Git history and their media directories;
they are not additional live model selections.

The inventory and generated gallery publish one study for each of these four ids.
The gallery keeps construction views and movies on that same model card.
`tools/verify_project.py` rejects duplicate studies, models restored at retired
paths, nested model copies, changed canonical hashes and stale showcase inputs.
The machine-readable relocation contract is
`sources/docs/reconstruction/models/shipyard-canonical-assets.json`.

The ship models are the same bytes as the reviewed five-layer versions. In flight,
draw `HullPartial` and `HullFinal`, and skip the three `Build*` groups. During
construction, enable cumulative groups from `model.json` using actual production
progress. The yard contains attachment nodes rather than copies of any ship.

Fresh Blender checks reopen native sources, independently import the canonical
GLBs, test the preserved hull fingerprint/triangle totals, evaluate the full yard
clearance sequence and all 480 controller frames for all three payloads, and render
current-path construction, transport and native flight probes. The original movies
are reused because every model byte is unchanged. Their original generation reports
retain historical paths and recipe hashes honestly; the live gallery binds them
through the relocation contract and fresh runtime audit. This is not a new render
or a claim that historical scripts generated the relocated files.

The ship generator can rebuild interiors using the current model's complementary
skin groups. It reconnects skin partitions into physical solids before ray tests;
it no longer needs a second distributed exterior-only GLB. Earlier generators and
reports under the former reconstruction folders describe superseded iterations;
use the current recipes listed in the yard documentation for new work.

Game packaging must pin the final assets commit and use the four paths above in
every consumer. Changes to the game package and client progress/event/visibility,
payload rig and terrain-cutout bindings are separate game integration work. The
smooth component arrival shown in movies remains an offline preview controller;
the rigid yard transport clip is embedded in the yard GLB. Space Dock construction
remains in orbit via Command Center and is outside this small-yard scope.
