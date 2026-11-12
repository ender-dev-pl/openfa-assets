# Rigellian refining pass — complete scope review (#185)

The requested pass covers all 35 registered Rigellian definitions: 23 buildings,
five ships and seven missiles. Twenty-two received separate refinement studies;
thirteen existing building studies were retained after focused legacy review
and fresh source-specific Blender/GLB verification. Retained models are not
counted as new refinements. All 59 earlier model pairs remain byte-identical
to the audit baseline and selectable in the gallery.

The work prioritizes visible missing equipment, body divisions, silhouette and
material regions. The full relevant Colony Database entry and functional
narratives informed the decisions. Correctly paletted graphics establish the
visible forms/colours; CDB does not name exact alloys or establish hidden
mechanisms. Original reference pixels remain private in ignored artifacts.

| New studies | Visible result |
| --- | --- |
| RI01, RI04, RI05, RI06, RI17 | Broad tapered gold crown arms; RI17 gains its missing lateral arms. |
| RI03 | Broad pale service housings, cavities, upright equipment and continuous spine. |
| RI08 | Perforated upper casing with actual blind cavities and recessed backings. |
| RI14 | Broad upper horizontal/lower vertical casing divisions; pale conduit and open crown retained. |
| RI20 | Stepped extractor casing, side pod, mechanism ribs/contacts and recessed slots. |
| RI23 | Tapered segmented bronze base and horizontal relief; paired-lance rig retained. |
| Observatory | Substantial equipment belt, bays, chamber equipment and axial terminals. |
| Transportation | Rounded inline bodies, broader colour fields and integrated shoulder masses. |
| Lazzaro Research | Rounded broader centre, full lateral shells and brown extremities. |
| Delphini Assault | Conformal gold flank fields, full lower shell and rounded copper lower bodies. |
| Messier-Lukannon | Annular copper termination, actual dark recess and curved hull transitions. |
| All seven missiles | Broad central fields/collars, shaped forks and distinct source-supported end treatments. |

Detailed observed/inferred decisions, retained geometry and measured results
are in `rigellian-crown-refinement.md`, `rigellian-structural-refinement.md` and
`rigellian-missile-refinement.md`. The remaining thirteen decisions are documented
in `rigellian-retained-review.md/json`. Sci-Tek subject bindings, exact sampling
and limits are recorded separately in `rigellian-scitek-review.json`.

## Verification and gallery

Every latest model has source-bound evidence from actual native Blender reopen
and independent GLB import. The final audit rechecks current model/report/render,
generator/verifier/dependency hashes and preservation of earlier studies; it does
not substitute hash checks for the runtime work. New refinement render pairs
total 61: all thresholded silhouettes have IoU 1.0, maximum native/imported
position difference is below 1.565e-6 and largest foreground RGB mean difference
is below 0.403/255. Source comparisons and resulting renders were inspected.

RI10 and RI18 keep their authored animations and actual GLB-derived gallery
previews. The final audit checks their latest clip bindings. All 43 authored
gallery clips across all cultures were fully decoded with ffmpeg and checked
for frame count, dimensions and authored timing. New static studies have no
invented operating clips; directional yaw rigs remain rigs. Gallery generation,
filter/player contracts, project verification and the provide-models contract
pass. The gallery contains 303 definitions and 406 studies. Browser manual
inspection of this isolated checkout was not performed; runtime evidence here
uses Blender, video decoding and the gallery behavior contracts.

`rigellian-refining-completion-audit.json` lists all 35 exact model pairs and
their validation reports, plus current inventory/gallery and evidence-ledger
hashes. Rerun with `python tools/audit_rigellian_refining_completion.py`.

This completes the requested evidence-led asset pass. Final artistic acceptance
belongs to user review; hidden construction, gameplay scale/direction calibration,
construction scaffolds and damage states remain separate work. Assets are
published on the isolated issue branch/PR; the active game checkout is unchanged.
