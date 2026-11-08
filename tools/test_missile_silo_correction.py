"""Regression checks for the source-bound silo mechanism and gallery contract."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import numpy as np
from PIL import Image
from gallery_animation_assets import glb_clips, preview_renderer

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'sources/docs/assets/bootstrap-3d/terran-refined/pb14'
MEDIA = ROOT / 'gallery/media/docs/assets/bootstrap-3d/terran-refined/pb14'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = json.loads((BASE/'correction-runtime-verification.json').read_text())
    for kind, digest in report['binaries'].items():
        assert sha(BASE/('model.'+kind)) == digest
    for filename, digest in report['renders'].items():
        assert sha(MEDIA/filename) == digest
    assert report['patcher_sha256'] == sha(ROOT/'sources/tools/blender/correct_missile_silo.py')
    assert report['verifier_sha256'] == sha(ROOT/'sources/tools/blender/verify_missile_silo_correction.py')
    assert max(report['position_errors'].values()) < 1e-4
    for kind in ['native_fixed_clearance', 'imported_fixed_clearance', 'decoy_fixture']:
        assert report[kind]['overlaps'] == 0
    assert report['decoy_fixture']['loaded_payload_collision_tests'] > 9000
    assert report['decoy_fixture']['radial_margin'] > .5
    assert report['imported_bore']['continuous_shaft_radius_tested'] == .82
    payload = (BASE/'model.glb').read_bytes()
    gltf = json.loads(payload[20:20+struct.unpack_from('<I', payload, 12)[0]])
    nodes = {n['name']: n for n in gltf['nodes']}
    assert nodes['SiloPlacementRoot']['extras']['preserve_ground_origin']
    assert 'LaunchPayloadHoldPoint' in nodes
    assert len(gltf['animations']) == 1
    clip = glb_clips(BASE/'model.glb')[0]
    assert clip['start'] == 0 and clip['end'] == 2
    animated = {gltf['nodes'][c['target']['node']]['name'] for c in gltf['animations'][0]['channels']}
    assert len(animated) == 8 and all('Iris curved leaf' in name for name in animated)
    for side in ['Left', 'Right']:
        for mode in ['Hybrid', 'AttackOnly', 'DefenceOnly']:
            node = nodes['StatusLamp'+side+mode]
            assert 'mesh' in node
            assert node.get('scale', [1, 1, 1]) == ([1, 1, 1] if mode == 'Hybrid' else [0, 0, 0])
    for name in ['../outside.py', '/absolute.py', 'tools/build_gallery.py', 'sources/tools/blender/missing.py']:
        try:
            preview_renderer(dict(renderer_path=name))
        except AssertionError:
            pass
        else:
            raise AssertionError(name)
    assert preview_renderer({}).name == 'render_gallery_animations.py'
    assert preview_renderer(dict(renderer_path='sources/tools/blender/verify_missile_silo_correction.py')).is_file()
    native = np.asarray(Image.open(MEDIA/'verified-native.png').convert('RGBA')).astype(float)
    imported = np.asarray(Image.open(MEDIA/'verified-imported.png').convert('RGBA')).astype(float)
    a = native[:, :, 3] > 128
    b = imported[:, :, 3] > 128
    iou = float((a & b).sum()/(a | b).sum())
    rgb = float(abs(native[:, :, :3]-imported[:, :, :3])[a & b].mean())
    assert iou > .995 and rgb < 5, (iou, rgb)
    assert Image.open(MEDIA/'iris.gif').n_frames == 32
    video = MEDIA/'animation-00.webm'
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames,r_frame_rate,width,height', '-of', 'json', str(video)]))['streams'][0]
    assert probe == dict(width=512, height=512, r_frame_rate='24/1', nb_read_frames='48')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'], check=True)
    review = dict(alpha_iou=iou, mean_rgb_error_255=rgb, binaries=report['binaries'], gif_sha256=sha(MEDIA/'iris.gif'), runtime='Blender native and imported GLB; final game integration not tested')
    (BASE/'delivery-review.json').write_text(json.dumps(review, indent=2)+'\n')
    print('SILO_DELIVERY_OK', review)


if __name__ == '__main__':
    main()
