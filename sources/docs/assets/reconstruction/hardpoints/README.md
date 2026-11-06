# Shield equipment reconstruction studies

Issue #956 within #950 / #946. Shield x10–x50 have independently authored editable
Blend sources, standalone GLB exports, six transparent review views and galleries.
Original PH11–PH15 pixels remain reference-only in ignored artifacts. The exact
reference sources and palettes are indexed in the reconstruction reference ledger.

The variants have separate thick-wall shells: asymmetric petals (x10), opposed
lobes (x20), layered closed front and side opening (x30), circular dark front and
rectangular side window (x40), and continuous enclosed front/body (x50). They are
not scaled copies. The connector, collars and visible internal gold component
follow observed forms; exact dimensions, cut angles, fasteners and hidden
conductor/insulator arrangement are authored interpretation.

Actual render iterations corrected smoothed cut faces, added small machined
chamfers, narrowed oversized side windows, preserved window openings through
reinforcing bands, and replaced separate front plugs with continuous hollow
rounded caps. Comparison sheets with original pixels are retained under
`artifacts/hardpoint-reference-study/shield-x<tier>-comparison.png`.

The native/GLB verifier checks topology, positive closed-shell volumes, real
measured wall thickness, actual side-window/closed-wall distinctions, materials,
bounds and absence of external images. Per-model technical reports bind these
checks to exact source/export hashes. Render reports check alpha and unclipped
framing for all thirty views. Runtime: Blender 4.5.15 LTS.

These remain studies. Matched-camera proportions, petal angles, cap/collar profile,
close-up artistic detail and cultural variants require further review. No model
is finally accepted. No shell articulation or gameplay mounting transform is
invented: inventory presentation rotation is not evidence of aiming or hinges.
Required mounted directional exports and projection/scale integration remain
open. No gameplay registration changed; programme acceptance gates stay open.

Reproduce with `build_shield_equipment.py`, `verify_shield_equipment.py` in Blender
and `review_shield_equipment.py` with Pillow. Each builder run is independent of
legacy pixels/meshes; only the review tool reads ignored legacy reference frames.
