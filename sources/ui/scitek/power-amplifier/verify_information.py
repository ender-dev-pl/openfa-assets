import json,hashlib,subprocess,sys
from pathlib import Path
from PIL import Image,ImageChops
o=Path(sys.argv[1]);d=json.loads((o/'information-timeline.json').read_text());assert d['frame_count']==423 and len(d['timeline'])==423
frames=sorted((o/'frames').glob('*.png'));assert [p.name for p in frames]==[f'{i:03}.png' for i in range(423)]
ious={}
for i in [0,87,228,369,422]:
    x=Image.open(o/f'frames/{i:03}.png').convert('RGB');y=Image.open(o/f'imported-{i:03}.png').convert('RGB')
    def mask(im):
        raw=im.tobytes();return bytes(max(raw[j:j+3])>40 for j in range(0,len(raw),3))
    a,b=mask(x),mask(y);union=sum(v or w for v,w in zip(a,b));inter=sum(v and w for v,w in zip(a,b));ious[str(i)]=inter/union;assert inter/union>.94,(i,inter/union)
    if i not in [0,422]:
        raw=x.tobytes();assert sum(raw[j]>raw[j+1]*2 and raw[j]>70 for j in range(0,len(raw),3))>20
for phase in d['phases']:
    for i in range(phase['first_legacy_frame'],phase['last_legacy_frame']+1):assert d['timeline'][i]['highlight_component']==phase['component']
assert len(d['phases'])==3 and sum(x['highlight_component'] is not None for x in d['timeline'])==333
expected={tuple(round(v,5) for v in f['rotation_euler']+f['camera_position']+[f['ortho_scale']])+(f['highlight_component'],) for f in d['timeline']};assert len(expected)>150
assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in frames})>=len(expected)*.8
assert ImageChops.difference(Image.open(o/'frames/087.png'),Image.open(o/'reload-0088.png')).getbbox(alpha_only=False) is None
subprocess.run(['ffmpeg','-y','-v','error','-framerate','15','-i',str(o/'frames/%03d.png'),'-c:v','libvpx-vp9','-crf','18','-b:v','0','-pix_fmt','yuv420p',str(o/'information.webm')],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(o/'information.webm'),'-f','null','-'],check=True)
decoded=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(o/'information.webm')]))['streams'][0];assert int(decoded['nb_read_frames'])==423
(o/'verification.json').write_text(json.dumps(dict(frame_count=423,fps=15,caption_highlight_frames=333,source_sha256=d['source_sha256'],import_iou=ious,video_sha256=hashlib.sha256((o/'information.webm').read_bytes()).hexdigest()),indent=2)+'\n',newline='\n');print('AMPLIFIER_INFORMATION_VERIFIED')
