# Sci-Tek physical model relationships

The36 presentations split into24 explicit shared physical models and12 upgrade-device presentations. [model-relationships.json](model-relationships.json) records each of the twelve decisions, current numeric effects, actual legacy colour-media hashes and hash-bound evidence from openFA-game. This resolves the mapping gap; it does not establish final geometric or runtime acceptance.

The twelve devices are not additional colony buildings, complete ships or projectiles. For example, Mk2 Mine is a drill/slurry assembly that improves an existing mine; Improved Sensors is integrated equipment rather than the Sensor Array building; Long Range Transmitter is a console with a recovered ship-equipment effect rather than a selectable hardpoint. A shared model requirement applies when two consumers show the same physical object. Statistical influence over a different object does not make the device its replacement geometry.

All twelve current research definitions have numeric modifiers and no unlockContentIds. Actual colour sources are their own _MA/STnn.VID files, while the dedicated shapes and technical component anatomy differ from the whole affected objects. ST naming alone is not the classification rule: some shared ship models also use ST media. The recovered legacy media callback and Long Range Transmitter path are documented separately; current package semantics are not presented as proof that every legacy effect implementation has been recovered.

Integration must retain the24 shared physical source contracts and use one dedicated colour solid plus one information GLB/timeline for each upgrade device. Do not create separately simulated content or replace mine/power-store/radar/turret/ship exteriors with internal upgrade presentations. Historical solids, baked static technical variants and category composition GLBs remain authoring/gallery only. If a future in-world detail genuinely depicts one of these devices, reuse its existing source.

Outstanding work: independently audit technical/physical geometry correspondence for these twelve presentations, including any intentionally reduced technical LOD and isolated auxiliary details. Classification alone must not be used to mark that requirement complete. Actual client/GPU acceptance is handled by the integration thread.

The first independent source geometry audit is now recorded in [upgrade-geometry-audit.md](upgrade-geometry-audit.md). It identifies the specific ST14 projectile-pose discrepancy and the11 Improved Sensors display-grid lines; it does not mark final geometry acceptance.

Current source-geometry follow-ups are resolved; see [DELIVERY.md](DELIVERY.md), the updated geometry audit and Improved Sensors surface proof. Historical outstanding-work notes above describe earlier stages. Actual client integration remains separate.
