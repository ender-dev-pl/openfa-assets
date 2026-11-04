import json,hashlib,subprocess,sys
from pathlib import Path
from PIL import Image,ImageChops
o=Path(sys.argv[1]) if len(sys.argv)>1 else Path('artifacts/issue-208-scitek/tracker-information');d=json.loads((o/'information-timeline.json').read_text());assert len(d['timeline'])==564 and d['frame_count']==564
files=sorted((o/'frames').glob('*.png'));assert [f.name for f in files]==[f'{i:03}.png' for i in range(564)]
for i in [0,87,228,369,510,563]:
    native=Image.open(o/f'frames/{i:03}.png').convert('RGB');imported=Image.open(o/f'imported-{i:03}.png').convert('RGB')
    def mask(im):
        # Compare raster line coverage without relying on transparent backgrounds.
        return bytes(1 if max(pixel)>40 else 0 for pixel in im.getdata())
    a=mask(native);b=mask(imported);union=sum(x or y for x,y in zip(a,b));inter=sum(x and y for x,y in zip(a,b));assert inter/union>.94,(i,inter/union)
    if i not in [0,563]:
        expected=d['timeline'][i]['highlight_component'];assert expected
        red=sum(r>g*2 and r>70 for r,g,b in native.getdata());assert red>20,(i,red)
for phase in d['phases']:
    for frame in range(phase['first_legacy_frame'],phase['last_legacy_frame']+1):assert d['timeline'][frame]['highlight_component']==phase['component']
assert sum(f['highlight_component'] is not None for f in d['timeline'])==444
assert ImageChops.difference(Image.open(o/'frames/087.png'),Image.open(o/'reload-087.png')).getbbox() is None
assert min(f['ortho_scale'] for f in d['timeline'])<1.2 and max(f['ortho_scale'] for f in d['timeline'])==4
expected_poses={tuple(round(v,5) for v in (f['rotation_euler']+f['camera_position']+[f['ortho_scale']]))+(f['highlight_component'],) for f in d['timeline']}
assert len(expected_poses)>200
assert len({hashlib.sha256(f.read_bytes()).hexdigest() for f in files})>=len(expected_poses)*.8
subprocess.run(['ffmpeg','-y','-v','error','-framerate','15','-i',str(o/'frames/%03d.png'),'-c:v','libvpx-vp9','-crf','18','-b:v','0','-pix_fmt','yuv420p',str(o/'information.webm')],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(o/'information.webm'),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(o/'information.webm')]))['streams'][0];assert int(probe['nb_read_frames'])==564
(o/'verification.json').write_text(json.dumps(dict(frames=564,fps=15,caption_highlight_frames=444,import_samples=[0,87,228,369,510,563],source_sha256=d['source_sha256'],timeline_sha256=hashlib.sha256((o/'information-timeline.json').read_bytes()).hexdigest(),video_sha256=hashlib.sha256((o/'information.webm').read_bytes()).hexdigest()),indent=2)+'\n')
print('TRACKER_INFORMATION_VERIFIED',564)
