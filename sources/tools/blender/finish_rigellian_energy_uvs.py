"""Restore the established local planar UV law after RI14 casing simplification."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import uuid
import bpy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
from refine_rigellian_missiles import uv
from remaster_rigellian_static import fit_camera, strip_png


def main():
    folder = ROOT/'sources/objects/rigellian/energy-gatherer'
    media = ROOT/'gallery/media/objects/rigellian/energy-gatherer'
    meta = json.loads((folder/'model.json').read_bytes())
    for kind, expected in meta['binaries'].items():
        assert hashlib.sha256((folder/('model.'+kind)).read_bytes()).hexdigest() == expected
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'), load_ui=False, use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    names = []
    for obj in meshes:
        if 'refined casing' in obj.name:
            uv(obj)
            names.append(obj.name)
    assert len(names) == 8
    bpy.ops.object.select_all(action='DESELECT')
    root = bpy.data.objects['PlacementRoot']
    for obj in meshes+[root]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    temporary_root = ROOT/'artifacts/rigellian-remaster-temp'
    temporary_root.mkdir(parents=True, exist_ok=True)
    original = tempfile.mkdtemp

    def workspace_temp(suffix=None, prefix=None, dir=None):
        parent = Path(dir).resolve() if dir else temporary_root
        assert parent.is_relative_to(ROOT.resolve())
        path = parent/((prefix or 'ri14-uv-')+uuid.uuid4().hex+(suffix or ''))
        path.mkdir()
        return str(path)

    tempfile.mkdtemp = workspace_temp
    try:
        bpy.ops.export_scene.gltf(filepath=str(folder/'model.glb'), export_format='GLB',
                                 use_selection=True, export_apply=True, export_extras=True,
                                 export_animations=False)
    finally:
        tempfile.mkdtemp = original
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'model.blend'), compress=True)
    sys.path.insert(0, str(ROOT/'tools'))
    from publication_support import clean_blend
    path = folder/'model.blend'
    path.write_bytes(clean_blend(path.read_bytes())[0])
    for view, direction in [('front-quarter',(6,-13,8)), ('front',(0,-16,4)), ('rear-quarter',(-7,12,7))]:
        fit_camera(direction, meshes)
        path = media/(view+'.png')
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
    meta['binaries'] = {kind: hashlib.sha256((folder/('model.'+kind)).read_bytes()).hexdigest()
                        for kind in ['blend','glb']}
    meta['casing_uv_finish'] = dict(
        tool=Path(__file__).relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        parts=sorted(names),
        contract='Recompute existing dominant-axis local planar projection after decimation; source maps and protected radial UVs unchanged.')
    (folder/'model.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
    print('RI14_CASING_UV_FINISHED',len(names),flush=True)


if __name__ == '__main__':
    main()
