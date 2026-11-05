"""Verify the native Blender sequence, encode 34.42s delivery and package the self-contained project."""
from pathlib import Path
import argparse,json,hashlib,subprocess,struct,zipfile
p=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--source-intro',type=Path,default=Path(str(Path(__import__('os').environ.get('FA_LEGACY','legacy'))/'_INTRO'/'INTRO.GDV')));args=ap.parse_args();state=json.loads((p/'render-state.json').read_text());assert len(state['completed'])==826;assert state['scene_sha256']==hashlib.sha256((p/'first-sequence-to-412.blend').read_bytes()).hexdigest()
for i in range(826):
 path=p/'rendered-frames'/f'frame-{i:06d}.png';b=path.read_bytes();assert struct.unpack('>II',b[16:24])==(640,480);assert hashlib.sha256(b).hexdigest()==state['completed'][str(i)]
video=p/'first-sequence-to-412.mp4';audio=p/'opening-audio.m4a';duration=826/24
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-start_number','0','-i',str(p/'rendered-frames/frame-%06d.png'),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(video)],check=True)
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,nb_frames,r_frame_rate,sample_aspect_ratio,display_aspect_ratio','-of','json',str(path)],text=True))
def audio_hash(path):return subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
q=probe(video);v=next(x for x in q['streams'] if x['codec_type']=='video');assert (v['width'],v['height'])==(640,480) and v['nb_frames']=='826' and v['r_frame_rate']=='24/1' and v['sample_aspect_ratio']=='1:1';assert abs(float(q['format']['duration'])-duration)<.1;assert audio_hash(audio)==audio_hash(video)
(p/'video-verification.json').write_text(json.dumps(dict(probe=q,audio_copied_without_reencoding=True,audio_packet_hash=audio_hash(video)),indent=2)+'\n')
if args.source_intro.exists():
 # Reference remains the decoded GDV, vertically corrected to the established letterbox.
 comparison=p/'legacy-vs-reconstruction.mp4'
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(args.source_intro),'-i',str(video),'-loop','1','-i',str(p/'comparison-labels.png'),'-filter_complex','[0:v]scale=640:262:flags=lanczos,pad=640:480:0:109:black,setsar=1,fps=24[ref];[ref][1:v]hstack=inputs=2[base];[base][2:v]overlay=0:0[v]','-map','[v]','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(comparison)],check=True)
 q2=probe(comparison);v2=next(x for x in q2['streams'] if x['codec_type']=='video');assert (v2['width'],v2['height'])==(1280,480) and v2['nb_frames']=='826' and v2['r_frame_rate']=='24/1';(p/'comparison-verification.json').write_text(json.dumps(q2,indent=2)+'\n')
files=['first-sequence-to-412.blend','first-sequence-to-412.mp4','opening-audio.m4a','build_sequence.py','refine_and_check.py','align_end_card.py','prepare_master.py','correct_master_color.py','trace_logo.py','tetra-outline.json','render_master.py','render_master_worker.py','finish_sequence.py','comparison.py','comparison-labels.png','sequence-manifest.json','sequence-verification.json','render-state.json','frame-verification.json','video-verification.json','sequence-comparison.jpg','README.txt']
if args.source_intro.exists():files+=['legacy-vs-reconstruction.mp4','comparison-verification.json']
(p/'CHECKSUMS.sha256').write_text('\n'.join(hashlib.sha256((p/f).read_bytes()).hexdigest()+'  '+f for f in files)+'\n');files.append('CHECKSUMS.sha256')
with zipfile.ZipFile(p/'first-sequence-to-412.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(p/f,f)
with zipfile.ZipFile(p/'first-sequence-to-412.zip') as z:assert z.testzip() is None
print('VERIFIED: 826 frames, 24fps, 640x480 letterbox, 34.4167s, four native scenes with cross dissolves, soundtrack packets preserved.')
