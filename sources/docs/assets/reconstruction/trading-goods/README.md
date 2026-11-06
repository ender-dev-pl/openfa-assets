# Coloured trading goods — complete first reconstruction pass

TI001–TI101 contain **101 editable coloured Blender models** and matching static GLBs. Each folder contains its native, GLB, source-bound runtime report and reference-observation metadata. The thirteen Terran missile folders also record the original native SHA256 and preserved local-geometry fingerprint. TI078–TI081 copy the completed TI001 cask geometry because their recovered references reuse that packaging; other related goods share construction functions while retaining separate saved sources.

Final compact monochrome and colour item images are deferred by the user. No production images, original game pixels or reference caches are included. Local technical renders were used to inspect the models. These are first reconstructions, with some hidden geometry, small motifs and physical arrangements inferred; further artistic refinement and real-time game integration remain separate work.

The native sources retain named editable parts and procedural material wear. Static GLBs retain base colours; procedural texture baking is not claimed. Every item was reopened in Blender 4.5 LTS, rendered for inspection, independently imported from GLB, checked for geometry coverage/world bounds, and checked for Principled base-colour round-trip preservation.

Use `sources/tools/trading-goods/build_model.py --item N --out WORK_DIRECTORY` in Blender to author a model from its recipe. For TI088–TI100, optionally pass `--inherited-native ORIGINAL_NATIVE`; otherwise the original Terran native source is resolved relative to this repository. Published standalone models do not require the original installation or inherited source to open or render. `verify_model.py` performs native/import inspection; `audit_catalogue.py --repo REPO` audits the full registered catalogue without Blender or private reference media.

See `docs/trading-goods/README.md`, `coverage.json`, `COMPLETION.md` and origin issue #214 for scope and continuity. Final image generation must not start automatically while its status is deferred.
