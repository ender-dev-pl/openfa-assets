"""Verify actual worker outputs, encode a silent review proxy and probe the resulting video."""
from pathlib import Path
import argparse,json,hashlib,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--frames',type=Path,required=True);ap.add_argument('--native',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args();sha=hashlib.sha256(a.native.read_bytes()).hexdigest();done={}
for p in sorted(a.frames.glob('worker-*.json')):
 d=json.loads(p.read_text());assert d['native_sha256']==sha;assert not set(done).intersection(d['completed']);done.update(d['completed'])
assert set(done)=={str(i) for i in range(937)}
for i in range(937):assert hashlib.sha256((a.frames/f'frame-{i:04d}.png').read_bytes()).hexdigest()==done[str(i)],i
plan=json.loads((Path(__file__).resolve().parent/'shot-plan.json').read_text());black_samples=sorted({f for shot in plan['scenes'] for f in shot['black_samples'] if f%2==0})
def decoded(index):
 return subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(a.frames/f'frame-{index:04d}.png'),'-f','rawvideo','-pix_fmt','rgb24','-'])
for f in black_samples:assert max(decoded(f//2))<=2,('expected black sample',f)
assert max(decoded(936))>50,'ending must hold a visible emblem'
a.output.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','6','-i',str(a.frames/'frame-%04d.png'),'-frames:v','937','-an','-vf','setsar=1','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(a.output)],text=True));assert len(probe['streams'])==1;s=probe['streams'][0];assert (s['codec_type'],s['width'],s['height'],s['r_frame_rate'],s['nb_frames'])==('video',320,240,'6/1','937');assert abs(float(probe['format']['duration'])-3748/24)<.002
report=dict(native_sha256=sha,video_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),frames_verified=937,decoded_black_source_samples_verified=black_samples,final_emblem_sample_nonblack=True,output_fps=6,canonical_fps=24,resolution=[320,240],native_frames_sampled='1,5,...,3745',audio=False,ffprobe=probe,quality='low-resolution basic review proxy; refining deferred');a.report.write_text(json.dumps(report,indent=2)+'\n');print('ANIMATIC_VERIFIED',937)
