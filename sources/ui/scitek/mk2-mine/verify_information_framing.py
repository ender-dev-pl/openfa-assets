"""Compare authored framing with private original-codec ST00 anchor frames.

Usage: python verify_information_framing.py INFORMATION_OUTPUT PRIVATE_ST00_FRAMES
No reference pixels are copied into the deliverable.
"""
import sys,json,hashlib
from pathlib import Path
from PIL import Image
out,refs=map(Path,sys.argv[1:3])
def bounds(p,red=False):
 im=Image.open(p).convert('RGB');mask=Image.new('L',im.size)
 rgb=im.tobytes();mask.putdata([255 if ((r>70 and r>g*2 and r>b*2) if red else max(r,g,b)>40) else 0 for r,g,b in zip(rgb[::3],rgb[1::3],rgb[2::3])]);return mask.getbbox()
def size(b):return b[2]-b[0],b[3]-b[1]
source=refs/'003.png';native=out/'frames/000.png';a,b=bounds(source),bounds(native)
ratios=[y/x for x,y in zip(size(a),size(b))];assert all(.9<x<1.1 for x in ratios),(a,b)
result=dict(whole=dict(source_update=3,source_bbox=a,authored_frame=0,authored_bbox=b,size_ratios=ratios),closeups=[])
for component,update,frame in [('slurry-recovery-ports',34,87),('drill-assemblies',99,228),('coolant-connectors',164,369)]:
 source=refs/f'{update:03}.png';native=out/f'frames/{frame:03}.png';a,b=bounds(source,True),bounds(native,True);assert a and b
 ratios=[y/x for x,y in zip(size(a),size(b))];assert all(.65<x<1.4 for x in ratios),(component,a,b,ratios)
 result['closeups'].append(dict(component=component,source_update=update,authored_frame=frame,source_bbox=a,authored_bbox=b,size_ratios=ratios,source_frame_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),authored_frame_sha256=hashlib.sha256(native.read_bytes()).hexdigest()))
result['limitations']='Coarse occupancy/framing comparison only. Different geometry and authored transforms preclude pixel-exact fidelity claims.'
(out/'framing-verification.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n');print('MINE_INFORMATION_FRAMING_VERIFIED')
