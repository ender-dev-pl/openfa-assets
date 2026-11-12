# Shared refined Fleet Battleship

Authoritative openfa:fleet-battleship for gameplay, ship catalogue and research09. All35 original source mesh/UV/material/local-transform signatures and packed wear maps retained. Ten previously research-only field-sensor/wingtip additions now belong to the shared45-mesh ship. Physical GLB is unchanged from that research solid, so its existing wear and authored artistic approximations are preserved.

BattleshipResearchRoot unit scale, front -Y, gameplay frame1 identity; disable presentation rotation. Client/GPU, scale and mounts remain pending. Corrected technical curves use28,764 actual evaluated physical edges; old pre-modifier wire mismatch is fixed. Runtime uses this one shared coloured GLB plus sources/ui/scitek/fleet-battleship/fleet-battleship-information.glb and timeline. Historical research solid and baked wire/highlight GLBs are authoring/gallery only.

Rebuild the original research source with build_battleship.py, then run refine_shared_wires.py -- INITIAL_OUTPUT REFINED_OUTPUT before technical exports. verify_shared_geometry.py -- ASSET_ROOT PROOF_OUTPUT REFINED_OUTPUT verifies preserved source and all61 imported poses/diagram edges. Further commands and known artistic limitations: sources/ui/scitek/fleet-battleship/README.md.
