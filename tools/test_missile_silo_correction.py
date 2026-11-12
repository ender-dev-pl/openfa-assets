"""Regression checks for the source-bound silo mechanism and gallery contract."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import numpy as np
from PIL import Image
from gallery_animation_assets import glb_clips
from canonical_assets import preview_renderer

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
    assert report['drive_generator_sha256'] == sha(ROOT/'sources/tools/blender/missile_silo_drive.py')
    assert report['verifier_sha256'] == sha(ROOT/'sources/tools/blender/verify_missile_silo_correction.py')
    assert max(report['position_errors'].values()) < 1e-4
    assert report['decoy_fixture']['overlaps'] == 0
    for kind in ['native_fixed_clearance', 'imported_fixed_clearance']:
        assert report[kind]['overlaps'] > 0 and 'retained' in report[kind]['acceptance']
    assert report['native_fixed_clearance']['contacts_by_obstacle'] == report['imported_fixed_clearance']['contacts_by_obstacle']
    assert report['decoy_fixture']['radial_margin'] > .10
    assert report['imported_bore']['continuous_shaft_radius_tested'] == .33
    assert report['imported_bore']['nominal_mouth_radius'] == .87
    payload = (BASE/'model.glb').read_bytes()
    gltf = json.loads(payload[20:20+struct.unpack_from('<I', payload, 12)[0]])
    mesh_count = sum('mesh' in n for n in gltf['nodes'])
    assert report['decoy_fixture']['loaded_payload_collision_tests'] == 33*4*mesh_count
    assert report['decoy_fixture']['launch_collision_tests'] == 11*4*mesh_count
    for kind in ['native_fixed_clearance', 'imported_fixed_clearance']:
        assert report[kind]['moving_vs_fixed_tests'] == 33*8*(mesh_count-8-1)
    nodes = {n['name']: n for n in gltf['nodes']}
    assert nodes['SiloPlacementRoot']['extras']['preserve_ground_origin']
    assert 'LaunchPayloadHoldPoint' in nodes
    assert len(gltf['animations']) == 1
    clip = glb_clips(BASE/'model.glb')[0]
    assert clip['start'] == 0 and clip['end'] == 2
    animated = {gltf['nodes'][c['target']['node']]['name'] for c in gltf['animations'][0]['channels']}
    assert len(animated) == 8 and all(name.startswith('Iris curved leaf') for name in animated)
    assert {c['target']['path'] for c in gltf['animations'][0]['channels']} == {'rotation', 'translation'}
    planar = json.loads((BASE/'diaphragm-verification.json').read_text())
    assert planar['binaries'] == report['binaries']
    assert sha(ROOT/planar['detail_render']['path']) == planar['detail_render']['sha256']
    assert planar['verifier_sha256'] == sha(ROOT/'sources/tools/blender/verify_silo_diaphragm.py')
    for kind in ['native', 'imported']:
        proof = planar[kind]
        assert proof['blades'] == 8 and proof['frames'] == 33
        assert proof['original_shape_error'] < 1e-6
        assert abs(proof['drop']-.20) < 1e-6
        assert proof['maximum_original_pose_error'] < 1e-6
        assert proof['floor_black'] and proof['floor_below_payload']
        assert proof['turn_degrees'] == 50 and proof['radial_travel'] == 0
        assert not proof['folding'] and not proof['scaling']
        opened = proof['opening_samples']
        assert opened[0]['clear'] == 0 and opened[-1]['clear'] == opened[-1]['samples']
        assert all(a['clear'] <= b['clear'] for a, b in zip(opened, opened[1:]))
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
