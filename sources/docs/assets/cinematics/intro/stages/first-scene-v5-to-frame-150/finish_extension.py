"""Verify all frames, encode the complete sequence and package the self-contained scene."""
from pathlib import Path
import json,hashlib,struct,subprocess,zipfile
p=Path(__file__).resolve().parent;state=json.loads((p/'render-state.json').read_text());assert len(state['completed'])==302
assert state['scene_sha256']==hashlib.sha256((p/'opening-to-frame-150.blend').read_bytes()).hexdigest()
for i in range(302):
 f=p/'rendered-frames'/f'frame-{i:06d}.png';b=f.read_bytes();assert struct.unpack('>II',b[16:24])==(640,560);assert hashlib.sha256(b).hexdigest()==state['completed'][str(i)]
duration=302/24;audio=p/'opening-audio.m4a'
if not audio.exists():subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(Path(__import__('os').environ.get('FA_LEGACY','legacy'))/'_INTRO'/'INTRO.GDV'),'-map','0:a:0','-t',str(duration),'-vn','-c:a','aac','-b:a','128k',str(audio)],check=True)
video=p/'opening-to-frame-150.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-start_number','0','-i',str(p/'rendered-frames/frame-%06d.png'),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height,nb_frames,r_frame_rate','-of','json',str(video)],text=True));v=next(s for s in probe['streams'] if s['codec_type']=='video');assert v['r_frame_rate']=='24/1' and int(v['nb_frames'])==302;assert abs(float(probe['format']['duration'])-duration)<.1
(p/'video-verification.json').write_text(json.dumps(probe,indent=2)+'\n')
def audio_hash(path):return subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
assert audio_hash(audio)==audio_hash(video)
(p/'audio-verification.json').write_text(json.dumps(dict(audio_packets_identical_to_prepared_soundtrack=True,legacy_source_codec="gremlin_dpcm",preview_codec="aac",preview_bitrate=128000,sha256=audio_hash(video)),indent=2)+'\n')
files=['opening-to-frame-150.blend','opening-to-frame-150.mp4','opening-audio.m4a','prepare_extension.py','extend_scene.py','render_extension.py','verify_extension.py','finish_extension.py','comparison.py','base-ship-fit.json','extension-poses.json','extension-verification.json','render-state.json','render-result.json','video-verification.json','audio-verification.json','continuation-comparison.jpg','README.txt']
checks='\n'.join(hashlib.sha256((p/f).read_bytes()).hexdigest()+'  '+f for f in files)+'\n';(p/'CHECKSUMS.sha256').write_text(checks);files.append('CHECKSUMS.sha256')
with zipfile.ZipFile(p/'opening-to-frame-150.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(p/f,f)
with zipfile.ZipFile(p/'opening-to-frame-150.zip') as z:assert z.testzip() is None
print('VERIFIED: 302 frames, 24 fps,',duration,'seconds; prepared AAC soundtrack packets unchanged; ZIP CRC passed')
