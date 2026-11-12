# PS7C detailed shared Space Dock (#216)

Authoritative new shared finished source for `openfa:space-dock`. The matching
`../construction/model.blend` and GLB contain this same refined core plus the
scaffold and its restrained service-carriage animation. Earlier #60/#192 studies
remain unchanged for provenance; they are not additional runtime model variants.

Reference: actual `_S/PS7C.256`, embedded VGA palette, two state descriptors:
finished 113×178 and construction 117×162 on their original 320×200 canvas.
`reference-evidence.json` binds source, palette and indexed-pixel hashes. The
second descriptor is the construction state, as previously identified by the
user; it is not a separate camera view. No source pixels are used as model maps.

Confirmed larger forms: broad faceted shallow roof, red roof fields, axial
antenna group, pointed tapered lower body, substantial pale diagonal supports,
dark lower face fields, bright projecting front service equipment, lateral
equipment and dense construction framework. The existing function/CDB audit
identifies a Terran orbital ship-production facility and does not establish a
specific alloy, hidden berth count or internal machinery layout.

The user-provided detailed station artwork guides panel density, roof markings,
lit openings and equipment detailing. Hidden sides, rear repetition, exact panel
seams, lamps, the service fork's internal mechanics and wear remain authored
interpretations. This image is not asserted to be a second original game view.

Refinement changes the actual geometry, keeping `PlacementRoot` at unit scale:
the former over-wide cross-section is narrowed to 0.78 of the earlier source;
the roof height above z=0.08 is reduced to 0.64; the antenna group and crown socket
follow the lower roof by -0.3492. Other socket translations follow the narrower
cross-section. The previous speculative front/rear berth assemblies are removed
because the front berth obscured the source-visible service assembly. Two
lateral berths remain. Historical source geometry is preserved in its old files.

New closed segmented plates, structural ribs, maintenance grilles, docking rims,
service fork/hydraulics, antenna collars and inspection lights improve the
readability of the same station. Six worn material families have portable colour,
metallic/roughness and tangent-normal maps, all packed into the Blend and GLB.
Material wear includes seam dirt, scratched paint, uneven roughness, staining,
rubbed edges and the original small hull dents. No Blender-only procedural node
is required in the client.

The construction framework is resized consistently with the core; its upper
height follows the lower roof/masts. The existing authored six-second carriage
cycle remains local equipment movement, with its horizontal span rescaled to
0.2184. It is not recovered legacy animation or a whole-station rotation.

Reproduce from the asset repository, using a Blender runtime:

```text
python tools/inspect_ps7c_reference.py --legacy-root ORIGINAL_INSTALLATION
blender --background --python-exit-code 1 --python sources/tools/blender/refine_ps7c_details.py -- --root . --variant refined
python tools/prepare_ps7c_publication.py --variant refined
blender --background --python-exit-code 1 --python sources/tools/blender/verify_ps7c_details.py -- --root . --variant refined
blender --background --python-exit-code 1 --python sources/tools/blender/refine_ps7c_details.py -- --root . --variant construction
python tools/prepare_ps7c_publication.py --variant construction
blender --background --python-exit-code 1 --python sources/tools/blender/verify_ps7c_details.py -- --root . --variant construction
blender --background --python-exit-code 1 --python sources/tools/blender/render_ps7c_activity.py -- --root .
python tools/review_ps7c_pixels.py
python tools/register_ps7c_details.py
python tools/build_gallery.py
python tools/verify_project.py
```

Fresh native/independent-import reports verify closed meshes, intended source
shape edits, exact shared core in construction, four equipment sockets, portable
material connections and sampled local construction movement. Actual multi-view
renders and an imported-GLB WebM preview are in the gallery. Pixel reports state
native/import differences separately and do not claim a measured legacy-fidelity
percentage.

Use these sources for every Space Dock presentation, not a research-only copy.
The client must recalibrate the changed silhouette, crown socket and scale using
real runtime views; do not reuse the old width compensation. Root placement and
actual simulation scheduling remain the client's responsibility. Equipment
socket orientation and hidden structure remain authored, not recovered 3D data.
