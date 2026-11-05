"""Verify/encode the 24fps sequence and package the editable Blender scene."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--audio',type=Path,help='Optional soundtrack source; defaults to the packaged audio')
args = parser.parse_args()
root = Path(__file__).resolve().parent
scene = root/'opening-reconstruction-24fps.blend'
state = json.loads((root/'render-state.json').read_text())
assert state['scene_sha256'] == hashlib.sha256(scene.read_bytes()).hexdigest()
assert len(state['completed']) == 192
for index in range(192):
    frame = root/'rendered-frames'/f'frame-{index:06d}.png'
    with frame.open('rb') as stream:
        header = stream.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24]) == (640,560)
    assert hashlib.sha256(frame.read_bytes()).hexdigest() == state['completed'][str(index)]
audio = args.audio or root/'opening-audio.m4a'
old_video = root.parent/'first-scene-v1/opening-preview.mp4'
if not audio.exists() and args.audio is None and old_video.exists():
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(old_video),
                    '-map','0:a:0','-vn','-c:a','copy',str(audio)],check=True)
if args.audio is not None and not audio.exists():
    parser.error('Audio source does not exist')
command = ['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-start_number','0',
           '-i',str(root/'rendered-frames/frame-%06d.png')]
if audio.exists():
    command += ['-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:a','copy']
command += ['-t','8','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
            '-movflags','+faststart',str(root/'opening-preview-24fps.mp4')]
subprocess.run(command,check=True)
probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries',
    'format=duration:stream=codec_name,codec_type,width,height,nb_frames,r_frame_rate',
    '-of','json',str(root/'opening-preview-24fps.mp4')],text=True))
video = next(s for s in probe['streams'] if s['codec_type']=='video')
assert video['r_frame_rate']=='24/1' and int(video['nb_frames'])==192
assert abs(float(probe['format']['duration'])-8)<0.15
(root/'video-verification.json').write_text(json.dumps(probe,indent=2)+'\n')
if old_video.exists() and audio.exists():
    def audio_packets(path):
        return subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(path),
            '-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
    old_audio_hash = audio_packets(old_video)
    new_audio_hash = audio_packets(root/'opening-preview-24fps.mp4')
    assert old_audio_hash == new_audio_hash, 'Audio packets changed'
    (root/'audio-verification.json').write_text(json.dumps({
        'original_audio_packet_hash':old_audio_hash,'output_audio_packet_hash':new_audio_hash,
        'audio_packets_identical':True},indent=2)+'\n')
files = ['opening-reconstruction-24fps.blend','opening-preview-24fps.mp4','hero-24fps.png',
         'retime_24fps.py','render_24fps.py','finish_24fps.py','retiming-validation.json',
         'render-state.json','render-result.json','video-verification.json','README.txt']
if audio.exists() and audio.parent.resolve()==root:
    files.append(audio.name)
if (root/'audio-verification.json').exists():
    files.append('audio-verification.json')
digests = [hashlib.sha256((root/name).read_bytes()).hexdigest()+'  '+name for name in files]
(root/'CHECKSUMS.sha256').write_text('\n'.join(digests)+'\n')
files.append('CHECKSUMS.sha256')
archive = root/'opening-reconstruction-24fps.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
    for name in files:
        bundle.write(root/name,name)
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
print('VIDEO_VERIFIED fps=24 frames=192 duration=8')
print('PROJECT_PACKAGE',archive,archive.stat().st_size,'bytes')
