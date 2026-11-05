"""Encode corrected cached images, or fresh native 4:3 Blender output, preserving AAC packets."""
import json,subprocess,hashlib,shutil
from pathlib import Path
p=Path(__file__).resolve().parent;old=p.parent/'first-scene-v5-to-frame-150';frames=p/'rendered-frames';native=all((frames/f'frame-{i:06d}.png').exists() for i in range(302))
if native: vf='setsar=1'
else:
 frames=old/'rendered-frames';assert all((frames/f'frame-{i:06d}.png').exists() for i in range(302)),'Render all 302 frames with render_letterbox.py first.';vf='scale=640:262:flags=lanczos,pad=640:480:0:109:color=black,setsar=1'
audio=p/'opening-audio.m4a'
if not audio.exists():shutil.copyfile(old/'opening-audio.m4a',audio)
output=p/'opening-letterbox.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-start_number','0','-i',str(frames/'frame-%06d.png'),'-i',str(audio),'-vf',vf,'-map','0:v:0','-map','1:a:0','-t',str(302/24),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(output)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,nb_frames,r_frame_rate,sample_aspect_ratio,display_aspect_ratio','-of','json',str(output)],text=True));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert (v['width'],v['height'])==(640,480) and v['nb_frames']=='302' and v['r_frame_rate']=='24/1' and v['sample_aspect_ratio']=='1:1';assert abs(float(probe['format']['duration'])-302/24)<.1
hashes=[]
for source in [audio,output]:hashes.append(subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(source),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip())
assert hashes[0]==hashes[1]
(p/'video-verification.json').write_text(json.dumps(dict(probe=probe,audio_packets_unchanged=True,audio_hash=hashes[0],vertical_scale=262/560,active_picture=[640,262],letterbox_bars_pixels=[109,109],native_rerender=native),indent=2)+'\n')
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(frames/'frame-000120.png'),'-vf',vf,'-frames:v','1',str(p/'corrected-star.png')],check=True)
print('VERIFIED 640x480, square pixels, 302 frames at 24fps, audio unchanged')
