# Verification

Current validation and historical import comparison are separate operations:

```powershell
python tools/verify_project.py
python tools/test_asset_workspace.py
python tools/test_gallery_animations.py
python tools/verify_gallery_videos.py
node tools/test_gallery_filters.cjs
python tools/asset_workspace.py audit-import
```

`verify_project.py` checks current layout boundaries, registered native study hashes, catalogue coverage, source/export/preview links and Python syntax. It does not require code/scripts to equal their first imported revision. Model changes still require the appropriate current inventory/review evidence; editable authoring does not mean accepting stale model reports.

`test_asset_workspace.py` exercises source updates without baseline rewrites, preservation of edited/unmanaged workspaces, preflight conflicts, optional external evidence, explicit history, source-image boundaries and path containment. The gallery test runs actual generated JavaScript with a DOM/event facade for all 45 race/type combinations, search, reset, empty states and index/deep links; visual browser acceptance remains separate.

Animation previews are rendered from each registered GLB clip using its authored time range. `test_gallery_animations.py` checks clip coverage, source/renderer/video hash invalidation, static-model exclusion, imported motion and media path boundaries. Project verification independently re-reads GLB clips and validates all preview manifests. Gallery filtering pauses hidden videos. Native controls support playback, scrubbing and looping without a CDN or network connection.

Preview generation requires `ffmpeg` with the VP9 encoder on PATH. `verify_gallery_videos.py` additionally uses `ffprobe` to check encoded dimensions, complete frame counts and authored duration, and decodes every clip with ffmpeg. These codec checks do not replace observing playback in the browser.

`audit-import` is optional provenance checking. It resolves current destinations through the layout and compares them with the frozen import hashes. The present reorganization preserves 8,451 imported files exactly and explicitly retires four unused snapshots. Later legitimate source edits can fail this comparison without blocking preparation. Their current verification belongs to current asset reports.

## Runtime checks

```powershell
python tools/asset_workspace.py prepare
$blender = (Get-Command blender).Source
python tools/asset_workspace.py blender --blender "$blender" -- tools/blender/verify_assault_fighter.py
```

This checks actual native and independent GLB operation in Blender without game/legacy dependencies. For full historical catalogue/semantic evidence, first explicitly enable optional evidence and local caches:

```powershell
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

All existing acceptance gates keep their original scope. No artistic, animation/state, attachment calibration or gameplay integration acceptance is inferred from this organization change. The game repository's `Verify-ChangedCodeQuality.ps1` is also run for this maintenance milestone; no game runtime code is modified.
