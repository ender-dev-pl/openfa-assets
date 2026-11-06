"""Verify all authored turntable frames are source-bound, visible and unclipped."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image
folder=Path(sys.argv[1]);source=Path(sys.argv[2]);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=json.loads((folder/'proof.json').read_text());assert proof['source_sha256']==sha(source)
frames=sorted(folder.glob('*.png'));assert len(frames)==proof['frames']==60;rows=[]
for p in frames:
    im=Image.open(p).convert('RGB');mask=Image.new('L',im.size);mask.putdata([255 if max(px)>20 else 0 for px in im.getdata()]);box=mask.getbbox();assert box
    margin=min(box[0],box[1],im.width-box[2],im.height-box[3]);assert margin>=2,(p.name,box,margin)
    rows.append(dict(frame=p.name,box=list(box),margin=margin,sha256=sha(p)))
(folder/'bounds-verification.json').write_text(json.dumps(dict(source_sha256=sha(source),preview_renderer_sha256=proof['renderer_sha256'],verifier_sha256=sha(__file__),frame_count=60,minimum_foreground_margin=min(r['margin'] for r in rows),brightness_threshold=20,all_frames_unclipped=True,frames=rows),indent=2)+'\n')
print('X40_PREVIEW_BOUNDS_VERIFIED',min(r['margin'] for r in rows))
