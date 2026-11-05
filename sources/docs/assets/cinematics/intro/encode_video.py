"""Encode the 826-frame reconstruction; original audio is optional and user-supplied."""
from pathlib import Path
import argparse,json,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--frames',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--audio',type=Path);ap.add_argument('--start-number',type=int,default=0);args=ap.parse_args()
for i in range(args.start_number,args.start_number+826):assert (args.frames/f'frame-{i:06d}.png').is_file(),i
cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate','24','-start_number',str(args.start_number),'-i',str(args.frames/'frame-%06d.png')]
if args.audio:assert args.audio.is_file();cmd+=['-i',str(args.audio),'-map','0:v:0','-map','1:a:0','-c:a','copy']
else:cmd+=['-an']
cmd+=['-t',str(826/24),'-vf','setsar=1','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(args.output)];subprocess.run(cmd,check=True)
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',str(args.output)],text=True));s=info['streams'][0];assert (s['width'],s['height'],s['r_frame_rate'],s['nb_frames'])==(640,480,'24/1','826');print('INTRO_VIDEO_VERIFIED',info)
