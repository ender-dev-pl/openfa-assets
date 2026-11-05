"""Encode the rendered sequence and package the editable reconstruction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--source-intro', type=Path, help='Optional original GDV for its first 8 seconds of audio')
args = parser.parse_args()
root = Path(__file__).resolve().parent
source = args.source_intro
if source is None:
    candidate = Path(os.environ.get('FA_LEGACY', 'legacy')) / '_INTRO/INTRO.GDV'
    source = candidate if candidate.is_file() else None
if source is not None and not source.is_file():
    parser.error('The requested original intro does not exist')
for number in range(96):
    path = root / 'rendered-frames' / f'frame-{number:06d}.png'
    if path.stat().st_mtime < (root / 'opening-reconstruction.blend').stat().st_mtime:
        raise RuntimeError('Stale frame from an older scene revision: ' + str(path))
    with path.open('rb') as stream:
        header = stream.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (640,560):
        raise RuntimeError('Missing or unexpected rendered frame: ' + str(path))
command = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', '12',
           '-start_number', '0', '-i', str(root / 'rendered-frames/frame-%06d.png')]
if source is not None:
    command += ['-i', str(source), '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '128k']
command += ['-t', '8', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(root / 'opening-preview.mp4')]
subprocess.run(command, check=True)
probe = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-show_entries',
    'format=duration:stream=codec_name,codec_type,width,height,nb_frames,r_frame_rate',
    '-of', 'json', str(root / 'opening-preview.mp4'),
], text=True))
video = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
assert (video['width'],video['height']) == (640,560)
assert video['r_frame_rate'] == '12/1' and int(video['nb_frames']) == 96
assert abs(float(probe['format']['duration']) - 8) < 0.15
(root / 'video-verification.json').write_text(json.dumps(probe, indent=2) + '\n')
files = ['opening-reconstruction.blend', 'hero-frame-036.png', 'opening-preview.mp4',
         'build_scene.py', 'render_scene.py', 'finish_scene.py', 'scene-manifest.json',
         'render-result.json', 'video-verification.json', 'README.txt']
comparison = root / 'comparison.jpg'
if (root / 'scene-inspection.json').is_file():
    files.append('scene-inspection.json')
if comparison.is_file() and comparison.stat().st_mtime >= (root / 'opening-reconstruction.blend').stat().st_mtime:
    files.append('comparison.jpg')
checksums = []
for name in files:
    with (root / name).open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    checksums.append(digest + '  ' + name)
(root / 'CHECKSUMS.sha256').write_text('\n'.join(checksums) + '\n')
files.append('CHECKSUMS.sha256')
archive = root / 'opening-reconstruction-v1.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
    for name in files:
        bundle.write(root / name, name)
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
print('INTRO_PREVIEW_VERIFIED frames=96 fps=12 duration=8 audio=' + str(source is not None))
print('EDITABLE_SCENE_PACKAGE', archive, archive.stat().st_size, 'bytes')
