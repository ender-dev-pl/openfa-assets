# Verification

The migration verifier checks every imported file against its exact byte length and SHA-256. It rejects misplaced finished image/video output under `sources/`. The gallery is generated from the authoritative existing inventory; all 303 definitions must have an available study and a preserved preview.

```powershell
python tools/verify_project.py
python tools/build_gallery.py
python tools/asset_workspace.py prepare
python tools/asset_workspace.py references
python tools/asset_workspace.py python -- tools/blender/verify_reconstruction_inventory.py
python tools/asset_workspace.py python -- tools/blender/audit_first_source_coverage.py --check
python tools/asset_workspace.py python -- tools/blender/check_catalogue_topology_evidence.py
python tools/asset_workspace.py python -- tools/blender/check_catalogue_texture_uv_evidence.py
python tools/asset_workspace.py python -- tools/blender/check_catalogue_hierarchy_evidence.py
python tools/asset_workspace.py python -- tools/blender/check_material_input_channels.py
python tools/asset_workspace.py python -- tools/blender/check_boundary_coverage_evidence.py
python tools/asset_workspace.py python -- tools/blender/check_attachment_readiness.py
```

Run native/imported tests through the Blender command documented in the workflow. Reports generated in `.workspace/` must be reviewed before publication. The existing ten scoped native/imported runtime gates remain unchanged; no artistic, state completeness, attachment calibration or game integration gate is promoted by this migration.

Baseline immutability and current asset validation are separate. After an intentional future source edit, the import comparison will correctly report a changed file; retain the original manifest as provenance and verify the changed asset with current evidence. Dependencies for archived GPU upscaling research are documented separately in `sources/tools/hq-sprite-authoring/README.md` and are not required for gallery browsing or Blender modelling.

The game repository's required `tools/Verify-ChangedCodeQuality.ps1` is run against the pre-migration game commit before completion. No application code is copied here as an executable game, and no new client runtime is invented for this asset-only project.

Gallery interaction logic can be checked with Node.js (no extra packages): `node tools/test_gallery_filters.cjs`. It executes the generated page script against a DOM/event facade for all 45 race/type combinations, text search, empty/reset states and index/deep links. This test does not replace a visual browser check.
