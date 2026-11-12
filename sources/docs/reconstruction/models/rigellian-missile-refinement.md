# Rigellian missile visible-section refinement

Part of [#185](https://github.com/ender-dev-pl/openfa-assets/issues/185).
Coverage is all seven registered Rigellian missile definitions: Detonator,
Multi-det, Flamejell, Maxi-det, Flare, Viral Repair and Temporal Stasis.
Previous first studies remain unchanged and selectable.

## Source review and cultural constraints

All 98 paletted RIM1..RIM7 frames were inspected, including opposed diagonal
flight views, narrow vertical views and the remaining launch/effect states.
The actual BUTTONS palette binding is recorded in `missile-reference-index.json`.
Private local `artifacts/issue-185/missile-all-states.png` retains the complete
contact sheet. Original pixels are never used as mesh or texture inputs.

Central blue/grey/red/pale regions are substantial body subdivisions, not the
thin small windows seen in the first 3D studies. Flare and Temporal Stasis have
gold outer fork regions. Detonator's forward purple region appears consistently
alongside the red/gold subdivisions; its old study omitted that colour. The
tiny sprites do not establish cockpit glass, exact cross-sections or detailed
internal mechanisms. Flight-view projection is not a justification for doubling
fork spread: diagonal separation must also agree with the narrow vertical views.

The complete Rigellian CDB review remains the cultural guide. Sophisticated
integrated interfaces and engineering coherence are contextual interpretations;
architectural prose does not specify missile alloys, a hidden propulsion system
or a required curved form. Names/catalogue effects establish no mapped physical
narrative. Biological/warfare lore does not justify arbitrary biohazard decoration
or changing a missile's source colours. Exhaust/effects stay outside solid bodies.

## Visible changes

The batch uses the original family-specific core profiles, nose colours and
functional identities. It restores readable sections rather than adding tiny
fasteners or generic weapon accessories:

- Detonator: wider blue-grey central field, source purple subdivision and a
  shorter, blunter gold cap.
- Multi-det: shorter, blunter gold cap and contoured fork sections; its already
  broad gold neck insert and red/purple bands are retained.
- Flamejell: wider segmented blue centre and broader fitted pale front collars.
- Maxi-det: wider blue centre sections and broader pale subdivisions, retaining
  the broad forebody and distinct coloured side tips.
- Flare: two readable blue centre groups, broader pale collars and gold outer
  edges that follow the shaped fork surfaces.
- Viral Repair: wider pale body fields and collars while retaining its red end.
- Temporal Stasis: wider red centre, broader pale collars and fitted gold fork
  edges, preserving the green body and gold end.

All forks receive gently shaped, tapered, faceted cross-sections within their
established overall extents. Their exact hidden thickness/facets remain authored
interpretation. Gold edges cover the outer part of Flare/Temporal Stasis forks;
the empty interval is preserved. The underlying independently authored wear maps
remain packed in native/GLB files. No launch articulation or speculative idle
animation is introduced. AlignmentForward helpers remain unchanged and explicitly
uncalibrated even where the visible gold cap is shortened.

## Validation and deliverables

`refine_rigellian_missiles.py` creates seven separate new studies under
`sources/docs/assets/reconstruction/rigellian-refined/missiles/<slug>/`.
`verify_refined_rigellian_missiles.py` reopens each native source and independently
imports each standalone GLB. Checks cover closed positive consistently oriented
surfaces, exact retained-component positions/material/hierarchy, actual open
fork witnesses, solid prong/core root contacts, measured angular coverage of
colour fields and actual collar widths. The marked native collection contains
the whole model; source and reference/lore hashes bind the evidence.

Fitted annuli have their face orientation recalculated before final export. The
first check of the rear Temporal Stasis collar detected an inconsistent/inverted
annulus; it was repaired rather than weakening the physical-surface contract.
All new pieces use an explicit portable triangulation and the correct first UV
set for their inherited authored materials.

Whole front-quarter, top and body-detail views are rendered from the reopened
native file and independent GLB. Every pair checks framing, thresholded
silhouette and foreground RGB difference. Actual whole-model overviews and
detail comparisons are visually inspected against the source sheets. Per-model
reports under matching `gallery/media/` paths retain exact hashes and measured
results. Source-specific artistic uncertainty is not erased by these checks.

The gallery appends all seven studies. They are static solid-body models;
existing authored animated studies and their playable previews remain intact.
This completes the technical missile-refinement batch, not the full 35-model
Rigellian programme, final artistic acceptance or calibrated game integration.

Measured batch results: 190 native meshes and 132 retained components with zero
position drift. All 21 native/imported render pairs have silhouette IoU 1.0;
maximum foreground RGB mean difference is 0.350/255 (rounded up). Maximum
world-space native/imported position difference is 1.014e-6 (rounded up).
