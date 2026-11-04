# Bug Hunter and Meat-Eater missile interpretation studies

Tracking: #968; relates to #951 and #946. Correctly paletted PM11/PM12 runtime frames are indexed with archive hashes in `missile-reference-index.json` (#958). Exact catalogue IDs are `openfa:missile/terran/bug-hunter` and `openfa:missile/terran/meat-eater`.

## Reference availability and scope

`audit_special_missile_references.py` records raw archive hashes, PM filename entries, bound catalogue references and filename-matched standalone sprite/video files in `special-missile-reference-audit.json`. The current `_MA` contains PM00..PM10 only; `_M` contains PM00..PM12. Neither definition has a bound management preview, and the filename search found no standalone PM11/PM12 sprite/video. This is a limited availability audit, not proof that no unidentified image elsewhere could depict them.

Flight frames 0..6 and launch frame 9 show different elongated silver/blue/red arrangements. Bug Hunter has a gold end, pale neck/yellow ring, longer silver shaft and blue region closer to the gray/red tail. Meat-Eater has a gray bulb, red neck, central blue region, pale band on the lower gray body and red lower end. Launch frame 9 supplies an authored canonical +Z alignment; runtime frame registration is not proven and the flight states are not a complete turntable.

## Explicit authored construction

Both editable models are **low-resolution interpretations**, not recovered high-resolution designs. Four thick blue sectors, windows, structural fasteners, smooth pressure shells and all hidden nozzle/support details are newly authored mechanical construction. The small pixels support silhouette/color ordering, not these exact frames, part counts, functions or dimensions. Original pixels/meshes remain reference-only, and no management image is invented. Final artistic interpretation and gameplay scale/axes/socket integration remain open.

## Actual render iteration

Revision 1 established distinct body/color layouts, open blue structures and hollow tail assemblies. Comparison of actual views with all seven flight samples and the launch presentation found Bug Hunter's blue cluster too low, an extra unsupported pale shoulder band and Meat-Eater's gray head too long.

Revision 2 raises Bug Hunter's blue region, removes that pale band, extends/rounds the gold tip and redistributes Meat-Eater's longitudinal regions to shorten its smooth gray head relative to the blue middle/lower body. All views were regenerated and compared again. The resulting manufacturing detail is intentional authored interpretation; it does not close the reference-fidelity gate.

## Deliverables and verification

`build_special_missiles.py` writes editable named meshes/asset collections, standalone GLB, six transparent views each and provenance under `docs/assets/reconstruction/missiles/terran/{bug-hunter,meat-eater}/`. `verify_special_missiles.py` reopens native files and imports GLB, checking exact IDs/provenance, nondegenerate topology/positive volumes, matching evaluated geometry/materials, four measured thick blue sectors, eight actual support contacts, real sector gaps and open nozzle axes to recessed throats. Solid-shaft crossings and hollow-ring overlaps are tested according to their actual geometry.

`review_terran_missiles.py --ids bug-hunter,meat-eater` validates twelve alpha/framing bounds, creates authored galleries/pair sheet and clearly labels the launch-frame fallback in ignored comparison sheets. Run the availability audit with `--check`, regenerate/verify inventory, compile Python and run the repository changed-code-quality gate. Blender generation/reopen/import exercises the asset target runtime; gameplay rendering/bindings are unchanged.

These two studies bring available authored Terran missile sources to all thirteen catalogue definitions. Eleven have management previews and two have only the limited reference evidence above. This is source coverage, not final acceptance of the Terran missile catalogue or of the overall reconstruction programme.
