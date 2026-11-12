"""Decode the new actual imported-GLB preview; check complete frames and timing."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT/'sources/objects/terran/space-dock/construction'
    media = ROOT/'gallery/media/objects/terran/space-dock/construction'
    manifest = json.loads((media/'animation-previews.json').read_text())
    clip = manifest['clips'][0]
    path = ROOT/clip['video']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == clip['sha256']
    result = subprocess.run([shutil.which('ffprobe'), '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                             '-show_entries', 'stream=codec_name,width,height,nb_read_frames:format=duration',
                             '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    stream = data['streams'][0]
    assert stream['codec_name'] == 'vp9' and stream['width'] == stream['height'] == 384
    assert int(stream['nb_read_frames']) == clip['frames'] == 144
    assert abs(float(data['format']['duration'])-6) < .05
    assert clip['distinct_pose_count'] > 1
    subprocess.run([shutil.which('ffmpeg'), '-v', 'error', '-i', str(path), '-f', 'null', '-'],
                   capture_output=True, check=True)
    report = dict(issue=216, glb_sha256=manifest['glb_sha256'], blend_sha256=manifest['blend_sha256'],
                  video_sha256=clip['sha256'], distinct_imported_poses=clip['distinct_pose_count'],
                  fully_decoded=True, probe=data)
    (folder/'preview-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PS7C_PREVIEW_DECODE_OK', clip['frames'], 'frames', clip['duration'], 'seconds', clip['distinct_pose_count'], 'poses')


if __name__ == '__main__':
    main()
