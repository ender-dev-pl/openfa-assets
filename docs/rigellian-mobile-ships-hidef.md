# Rigellian mobile fleet: hi-def refinement

Tracked in [#232](https://github.com/ender-dev-pl/openfa-assets/issues/232).
This is a new refinement goal for Lazzaro Research, Delphini Assault,
Messier-Lukannon and Transportation. Observatory is excluded. The previous
all-culture scope review #185 remains historical evidence, not artistic approval
of this new work.

## Reference mapping and visual language

The four supplied hi-def pictures map in order to the small research saucer,
elongated assault hull, rounded heavy capsule and twin-body transport. Attachment
filenames and SHA-256 values are recorded in
`sources/objects/rigellian/fleet-style.json`; the original pictures remain local
user attachments. Paletted `RI0A`, `RI1C`, `RI2C` and `RI3C` heading samples have
also been inspected. No reference pixels become textures or traced contours.

The common palette is cool slate-jade hull paint, pale alloy structure, muted
ochre-gold identity fields, copper pod/thermal covers and graphite recesses.
Small warm windows and restrained blue engine/optical accents support readability.
Use integrated rounded structures and deliberate panel divisions, consistent with
Rigellian cultural evidence for elegant, ergonomic engineering. The CDB does not
identify a mandatory alloy. Add restrained seam dirt, scuffs, edge wear and small
surface damage to newly authored geometry/materials.

The user's subsequent quality benchmark is the refined IS0C Federal Transporter.
Use its formed surfaces, readable functional equipment, recessed joins and
portable materials as the craft standard, not its sphere/truss design language.
The user explicitly rejected the first drafts' dense regular hull grid: neither
legacy nor the supplied hi-def references supports that treatment. Use broad,
quiet formed skins and concentrate detail at service assemblies and interfaces.
Do not claim the early generated drafts are artistically accepted.

## Scale contract

| Ship | Confirmed legacy role | Authoring size recommendation |
| --- | --- | ---: |
| Lazzaro Research | class 2, scout role | 28 world units |
| Delphini Assault | class 3, Destructor analogue | 64 world units |
| Messier-Lukannon | class 4, Terminator analogue | 96 world units |
| Transportation | class 5, transport role | 180 world units |

These role mappings come from `legacy-gameplay.json`, including the Terran role
counterparts. Exact physical lengths are not recovered. The current game package
has no size override for these four ids and therefore renders them at the fallback
96 world units. The table is an explicit proposed authoring/integration contract;
it is not a claim that a changed game configuration is already implemented.
One native authoring unit corresponds to ten proposed world units. A shared-scale
comparison must use these ratios rather than individually fitting four images.

Detail also follows class: a small research cockpit and substantial equipment
on Lazzaro; reinforced integrated military assemblies on Delphini; more numerous,
smaller windows and service panels on Messier; and cargo/service fittings on the
longer twin-module transport. Generic alignment helpers are not calibrated weapon
mounts. Slot counts alone do not establish attachment positions or weapon scale.

## Delivery and acceptance

Use one canonical editable Blend and one GLB per ship under
`sources/objects/rigellian/<slug>/`. Replace prior catalogue selections and remove
superseded model payloads in the final consolidation milestone. Preserve useful
historical reports/renders. Target at most 110,000 triangles / 24 mesh batches per
ship, with a shared worn PBR atlas no larger than 2048 square. Actual measurements
and visual review determine final budgets, not object-count inflation.

Validate saved native sources and independent GLB imports in Blender, inspect
front/side/top/rear renders and a shared-scale fleet composition, then bind reports
to actual hashes. Update the interactive gallery and provide signed commit,
canonical paths, scale contract and previews to the authorized game thread.
Game attachment, renderer/GPU and runtime acceptance remain separate integration
evidence. Avoid duplicate builds, full runtime copies or large reference exports.

## Verified asset delivery

| Model | Triangles | Mesh batches | Material |
| --- | ---: | ---: | ---: |
| Lazzaro Research | 16,400 | 10 | 1 |
| Delphini Assault | 25,728 | 15 | 1 |
| Messier-Lukannon | 32,842 | 14 | 1 |
| Transportation | 52,390 | 14 | 1 |

The final saved sources were reopened in Blender 4.5.15 LTS and independently
imported from GLB. Bidirectional world-position error is zero. Native/imported
render silhouettes have alpha IoU 1.0; foreground RGB mean error is below
0.03/255 for every model. Local ray checks verify that the blue drive exits are
unobstructed in native and imported geometry. These checks caught and corrected
overlapping drive housings; file existence alone would not have exposed them.
The underside review uses mirrored studio lights to show the actual lower meshes.
Hidden-side service equipment remains authored interpretation.

`sources/objects/rigellian/canonical-assets.json` records the sixteen superseded
binary payloads retired from distribution. Each ship now has exactly one
catalogue study and one selected canonical Blend/GLB. Historical reports and
renders remain available. Each interactive catalogue card includes six individual
views and two common-camera fleet comparisons. Preview:
[fleet review](../gallery/media/objects/rigellian/fleet/review.jpg).

Reproduce from the asset repository (Python requires Pillow and NumPy):

```text
python sources/tools/rigellian_fleet_surface_maps.py
blender --background --python-exit-code 1 --python sources/tools/blender/build_rigellian_mobile_fleet.py
python tools/prepare_rigellian_mobile_publication.py
blender --background --python-exit-code 1 --python sources/tools/blender/verify_rigellian_mobile_fleet.py
python tools/register_rigellian_mobile_fleet.py
python tools/build_gallery.py
python tools/review_rigellian_mobile_fleet.py
python tools/register_rigellian_mobile_fleet.py
python tools/verify_project.py
```

Both the builder and publication preparer support `--ship <slug>` for focused
updates. Avoid regenerating unaffected models. Run native/import verification
against the same final artifacts; no game rebuild or unpacked runtime is needed
for this source-asset check. Full client lighting, scale overrides and equipment
attachment acceptance remain the game worker's responsibility.
