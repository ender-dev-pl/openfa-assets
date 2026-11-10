# Light-ship inputs for the remaining remaster protocol

Programme openfa-assets #248. This is a read-only GLB/metadata audit to prepare the remaining Assault Fighter, Combat Eagle and Scoutship concept/render work while disk headroom is insufficient for generation. It does not replace those missing stages or claim new Blender/client/artistic validation.

`python tools/audit_light_ship_protocol_inputs.py` reads current files in memory. It verifies canonical native/export hashes, the complete scene tree and root catalogue identity, five disjoint layer subtrees, indexed triangle counts, decoded world-space POSITION bounds and stage metadata. GLB matrices/TRS are applied before converting Y-up coordinates to the source Blender axes. Source/export/metadata hashes remain unchanged. The deterministic [report](light-ship-protocol-inputs.json) binds the auditor and exact inputs.

| Ship | Flight meshes | Flight triangles | All construction layers, triangles |
| --- | ---: | ---: | ---: |
| Assault Fighter | 14 | 47,198 | 64,338 |
| Combat Eagle | 13 | 29,192 | 43,348 |
| Scoutship | 14 | 31,344 | 54,300 |

Flight must show **both** `HullPartial` and `HullFinal`, while hiding `Build01_BaseFrame`, `Build02_ExpandedFrame` and `Build03_Systems`. The two hull groups are complementary partitions of the exterior; `HullFinal` alone is not the complete ship. The audit verifies their current distinct subtrees, counts and combined bounds. It does not reconstruct historical exterior equality or prove that no triangles overlap geometrically.

Construction remains five cumulative stages starting at progress 0, 0.16, 0.38, 0.65 and 0.88. The GLBs contain no baked animation clip: visibility follows real client build progress. Keep the same canonical payload for flight, building, ship menus and SciTek. Keep original construction stages and lifting sockets during future protocol review; no duplicate standalone-flight model is needed.

A metadata caveat is recorded: the three internal geometry leaves in each model inherit helper `catalogue_id=terran:ship-yard`, although each authoritative `ShipAssembly` root correctly identifies its ship. Treat the root as the object identity. This audit exposes the stale helper tags without silently rewriting native/export bytes; their normalization needs a separate source-bound asset validation milestone when generation can safely resume.

Next visual work must use correctly paletted original references and compare actual native/imported **flight-only** renders with legacy and the selected concept. Existing construction review explicitly does not certify legacy fidelity. None of the three remaining protocol items is marked complete by this audit. Ordinary Transporter and Spy Satellite also remain pending. No new image, model, checkout, build or archive is generated here.
