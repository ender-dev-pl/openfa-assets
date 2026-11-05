from pathlib import Path
import json,hashlib,subprocess,struct,zipfile
p=Path(__file__).resolve().parent;state=json.loads((p/'render-state.json').read_text());assert len(state['completed'])==302;assert state['scene_sha256']==hashlib.sha256((p/'opening-steady-flight.blend').read_bytes()).hexdigest()
for i in range(302):
 f=p/'rendered-frames'/f'frame-{i:06d}.png';b=f.read_bytes();assert struct.unpack('>II',b[16:24])==(640,480);assert hashlib.sha256(b).hexdigest()==state['completed'][str(i)]
video=p/'opening-steady-flight.mp4';audio=p/'opening-audio.m4a';duration=302/24
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-start_number','0','-i',str(p/'rendered-frames/frame-%06d.png'),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(video)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,nb_frames,r_frame_rate,sample_aspect_ratio,display_aspect_ratio','-of','json',str(video)],text=True));v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'])==(640,480) and v['nb_frames']=='302' and v['r_frame_rate']=='24/1' and v['sample_aspect_ratio']=='1:1';assert abs(float(probe['format']['duration'])-duration)<.1
hashes=[subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(f),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip() for f in [audio,video]];assert hashes[0]==hashes[1]
(p/'video-verification.json').write_text(json.dumps(dict(probe=probe,audio_packets_unchanged=True,audio_hash=hashes[0]),indent=2)+'\n')
old=p.parent/'first-scene-v6-letterbox/opening-letterbox.mp4'
if old.exists():
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(old),'-i',str(video),'-loop','1','-i',str(p/'comparison-labels.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2[base];[base][2:v]overlay=0:0[v]','-map','[v]','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(p/'motion-before-after.mp4')],check=True)
if (p/'motion-before-after.mp4').exists():
 ab=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',str(p/'motion-before-after.mp4')],text=True));v=ab['streams'][0];assert (v['width'],v['height'])==(1280,480) and v['nb_frames']=='302' and v['r_frame_rate']=='24/1';(p/'comparison-verification.json').write_text(json.dumps(ab,indent=2)+'\n')
files=['opening-steady-flight.blend','opening-steady-flight.mp4','opening-audio.m4a','smooth_motion.py','input-poses.json','render_worker.py','render_parallel.py','apply_steady_motion.py','render_steady.py','verify_scene.py','finish_steady.py','steady-poses.json','motion-verification.json','scene-verification.json','aspect-verification.json','cache-verification.json','render-state.json','video-verification.json','comparison-labels.png','README.txt']
if (p/'motion-before-after.mp4').exists():files.extend(['motion-before-after.mp4','comparison-verification.json'])
(p/'CHECKSUMS.sha256').write_text('\n'.join(hashlib.sha256((p/f).read_bytes()).hexdigest()+'  '+f for f in files)+'\n');files.append('CHECKSUMS.sha256')
with zipfile.ZipFile(p/'opening-steady-flight.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(p/f,f)
with zipfile.ZipFile(p/'opening-steady-flight.zip') as z:assert z.testzip() is None
print('VERIFIED steady flight: 302 frames, 24fps, 640x480 letterbox, AAC packets unchanged; ZIP CRC passed')
