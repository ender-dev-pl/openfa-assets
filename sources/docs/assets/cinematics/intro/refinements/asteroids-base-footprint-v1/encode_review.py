"""Validate current native/worker hashes and encode the 12 fps silent refining review."""
import argparse,json,hashlib,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,required=True);ap.add_argument('--frames',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args();sha=hashlib.sha256(a.native.read_bytes()).hexdigest();frames=a.frames/sha[:12];done={}
for p in sorted(frames.glob('worker-*.json')):
 d=json.loads(p.read_text());assert d['native_sha256']==sha;assert not set(done).intersection(d['completed']);done.update(d['completed'])
assert set(done)=={str(i) for i in range(269)}
for i in range(269):assert hashlib.sha256((frames/f'frame-{i:04d}.png').read_bytes()).hexdigest()==done[str(i)],i
a.out.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['ffmpeg','-v','error','-y','-framerate','12','-i',str(frames/'frame-%04d.png'),'-frames:v','269','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(a.out)],check=True)
d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(a.out)],text=True));assert len(d['streams'])==1;s=d['streams'][0];assert (s['width'],s['height'],s['r_frame_rate'],s['nb_frames'])==(640,480,'12/1','269');assert abs(float(d['format']['duration'])-269/12)<.002;raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(frames/'frame-0268.png'),'-f','rawvideo','-pix_fmt','rgb24','-']);assert max(raw)<=2
a.report.write_text(json.dumps(dict(native_sha256=sha,review_sha256=hashlib.sha256(a.out.read_bytes()).hexdigest(),source_range_inclusive=[144,412],frame_hashes_verified=269,native_fps=24,review_fps=12,final_black_verified=True,audio=False,ffprobe=d,quality='reference-guided refining pass 1; visual review separate from structural checks'),indent=2)+'\n');print('REFINED_REVIEW_VERIFIED',269)
