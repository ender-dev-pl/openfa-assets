# Braccatian five-ship review (#190)

The scope is all five registered ship definitions, not only the three changed
models. All 130 source descriptor records were reviewed: Rattlesnake, WidowMaker
and Morning Glory have 32 populated headings each; HeartsBlood has sixteen
populated even descriptors and sixteen empty odd descriptors; SkyMech has two
fixed states. There are 114 populated images. Palette/source identities are
bound by the immutable Braccatian baseline. Original pixels stay private.

The complete culture entry and its cross-culture mentions were read in the
programme's CDB evidence pass. Architecture/display lore provides context, not
proof of ship alloys, clan emblems or internal mechanisms. The exact mapped
functional text at offsets 95539/95551/95562/95574/95588 was reread and hash
checked: it supplies the five names, without recovered descriptive narratives.
The user identifies BR4C as an orbital station and its second fixed frame as
the construction version, densely covered in scaffolds and temporary shields.
The Sci-Tek subject audit does not bind a film directly to any of these five BR
entries. The two fixed frames do not recover exact construction-motion timing.

## Changed models

WidowMaker retains its gold tapered pressure hull, rose nose, four real aft
openings, grey armour/strakes and alignment helper. The earlier eight hairline
neck accents are replaced by broad conformal rose fields. The larger coloured
regions are visible in multiple original headings; exact cross-sections and
hidden repetition remain authored. HeartsBlood receives the same forward-field
correction while preserving its own complete gold body, four rose radial pods
with three bands each, nose, four aft openings and alignment helper. Empty odd
descriptors do not justify adding a second geometric state or animation.

SkyMech initially received additional equipment on the existing thin truss. The
user correctly pointed out that the main central body itself was too narrow.
That draft was replaced before registration. The refined station now has a
broad two-chamber axial body, wider equatorial collar, sixteen casing rails,
three broad bands, eight substantial axial housings with coloured faces/end
collars, four broad radial service casings, a wider upper window, two dome
castings and concentric module rims. Radial casings extend nearly to the inner
faces of the peripheral hemispheres. Caps, hemispherical modules, aerials,
radial arm cores and alignment axis remain preserved. Equipment identities,
exact profiles, dimensions, hidden construction and alloy labels are authored;
the larger central volume and densely equipped character follow source/user
evidence. New parts have independently authored material-appropriate wear.

The original body files remain unchanged and separately selectable. Named
replacements are explicit in metadata. Retained meshes keep their geometry,
topology, UV layers, corner normals, parents and materials. No calibrated
hardpoint mounts are invented; the original declared-slot metadata is retained.
No operating clips are added to these static models.

## Models retained after focused review

Rattlesnake's current curved rose body, pale-gold prow and broadened/raised aft
end already reproduce the visible major form across its tiny 5-19 pixel-wide
headings. Its existing fitted service fields are sufficient; these sprites do
not establish another missing major component. Morning Glory's narrow gold
spindle, broad rose terminal, short axial projection and grey opposite tip
correspond to its 9-18 pixel-wide headings. Exact transverse shape and hidden
surfaces remain uncertain. Neither model receives invented machinery or a
microdetail-only revision. Both are retained with fresh native/GLB construction,
material, UV, alignment-helper and render checks; they are not counted as newly
refined models. Their review media are separate from the unchanged old sources.

## Validation

Actual native reopen and independent GLB import passed for all five current
normal-appearance models: 33/48/56/40/112 positive closed consistently wound
meshes (Rattlesnake/WidowMaker/HeartsBlood/Morning Glory/SkyMech respectively).
The original per-ship construction/UV/material/alignment contracts were freshly
run against every baseline. Unchanged models also passed them after independent
import. All 188 retained meshes preserve exact geometry, topology, UV layers,
corner normals, hierarchy and materials. Constant-material hardware does not
require invented UV layers; mapped parts retain their actual UV contracts.

The three refined models check all 8/8/85 new attachment intersections, including
reverse containment where a substantial service casing surrounds its arm.
Actual radial rays measure SkyMech core radii ~0.852/0.880/0.633 at lower/middle/
upper sections versus ~0.327/0.340/0.356 previously. Actual core volume increases
from ~1.130 to ~5.332; the middle diameter is ~2.59 times the old model's.
The radial casings stop ~0.0025 model units from the hemispherical modules'
inner faces. These are measurements of both real meshes, not just constants.

Independent GLB position error is below 1.476e-6. Effective packed material
channels match across native/imported formats, including the inherited 1024px
maps and new independent 256px maps. Alignment helpers and original declared
slot metadata remain unchanged. Twenty actual native/imported whole/rear/side/
detail pairs pass: nineteen have silhouette IoU 1.0 and one Morning Glory edge
differs by one thresholded pixel (IoU >0.999989). Maximum foreground RGB mean
difference is below 0.0047/255 (below 0.0033/255 for the three refined cases). Actual paired and
source/before/after views were inspected. No clip is present in these five
finished-state models, consistent with their previous exports.

## Construction-state follow-up

This normal-appearance milestone does not complete the newly requested station
pair requirement. Issue #192 covers separate refined construction models for
all seven cultures, using the second fixed source frames as scaffolded versions
with temporary covers and gentle authored work activity. BR4C is first. Its
construction variant must use this expanded central body, receive its own
native/GLB/animation/gallery validation and be handed to the authorized main
integration chat when ready. The original Braccatian programme still requires
ten missile decisions and the final all-model audit; its ship-state requirement
also remains open until the BR4C construction model is verified.

## Completed follow-up

All seven station pairs, including the expanded BR4C construction model, were subsequently delivered and audited in #192. All ten Braccatian missile decisions are complete. `braccatian-refining-completion.md` and its JSON provide the final full-scope proof; the follow-up requirements above describe this earlier ship milestone. Canonical ship display names are repaired without changing any model or runtime report.
