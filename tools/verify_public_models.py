"""Run inside Blender: reopen every sanitized source and independently import GLBs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'project/publication-runtime.json')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--exports-only', action='store_true', help='Complete independent imports using an existing native checkpoint')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    paths = sorted((ROOT / 'sources').rglob('*.blend'))
    if args.limit:
        paths = paths[args.start:args.start + args.limit]
    else:
        paths = paths[args.start:]
    records = []
    if args.exports_only:
        records = json.loads(args.output.read_text())['records']
        paths = []
    for index, path in enumerate(paths):
        relative = path.relative_to(ROOT).as_posix()
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
        assert len(bpy.data.scenes), relative
        native_meshes = len(bpy.data.meshes)
        native_objects = len(bpy.data.objects)
        # Ensure external image dependencies remain available after rebasing.
        missing = []
        for image in bpy.data.images:
            if image.source == 'FILE' and image.filepath and not image.packed_file and not image.packed_files:
                dependency = Path(bpy.path.abspath(image.filepath))
                if not dependency.is_file():
                    missing.append(image.name)
        assert not missing, (relative, 'Missing image dependencies', missing)
        record = {'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                  'native_objects': native_objects, 'native_meshes': native_meshes,
                  'external_images_resolved': True}
        exported = path.with_suffix('.glb')
        if exported.is_file():
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str(exported))
            assert len(bpy.data.objects), relative
            record.update(glb=exported.relative_to(ROOT).as_posix(),
                          glb_sha256=hashlib.sha256(exported.read_bytes()).hexdigest(),
                          imported_objects=len(bpy.data.objects), imported_meshes=len(bpy.data.meshes))
        records.append(record)
        if index % 10 == 0:
            print('PUBLIC_MODEL_RUNTIME', index + 1, '/', len(paths), relative, flush=True)
        # A checkpoint outside tracked inputs permits resuming a long audit.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({'blender_version': bpy.app.version_string,
                                          'scope': 'Native reopen, external image resolution and independent GLB import; metadata-only geometry proof is separate.',
                                          'records': records}, indent=2) + '\n')
    covered = {record['glb'] for record in records if 'glb' in record}
    additional = []
    for path in sorted((ROOT / 'sources').rglob('*.glb')):
        relative = path.relative_to(ROOT).as_posix()
        if relative in covered:
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path))
        assert len(bpy.data.objects), relative
        additional.append({'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'imported_objects': len(bpy.data.objects), 'imported_meshes': len(bpy.data.meshes)})
    args.output.write_text(json.dumps({'blender_version': bpy.app.version_string,
                                      'scope': 'All native sources reopened, external images resolved and all GLB exports independently imported; metadata-only geometry proof is separate.',
                                      'records': records, 'additional_exports': additional}, indent=2) + '\n')
    print('PUBLIC_MODELS_VERIFIED', len(records), 'native sources;', len(covered) + len(additional), 'independent GLB imports', flush=True)


if __name__ == '__main__':
    main()
