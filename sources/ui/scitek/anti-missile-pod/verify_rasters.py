import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
o=Path(sys.argv[1]);poses=Path(sys.argv[2]) if len(sys.argv)>2 else o.parent/'pod-preview-final-poses'
im=Image.open(o/'solid.png').convert('RGBA');box=im.getchannel('A').getbbox();ratio=(box[2]-box[0])/(box[3]-box[1]);assert abs(ratio/(107/87)-1)<.03
def tile(scale):
 canvas=Image.new('RGBA',(144*scale,160*scale));art=ImageOps.contain(im.crop(box),(107*scale,87*scale),Image.Resampling.LANCZOS)
 canvas.alpha_composite(art,(17*scale+(107*scale-art.width)//2,61*scale+(87*scale-art.height)//2));return canvas
native=tile(1);native.save(o/'tile-native.png');tile(4).save(o/'tile-4x.png')
disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(o/'tile-disabled.png')
b=native.getchannel('A').getbbox();assert all(abs(a-c)<=2 for a,c in zip(b,[17,61,124,148])),b
inputs=json.loads((poses/'inputs.json').read_text())
for key,suffix in [('blend_sha256','.blend'),('glb_sha256','.glb')]:assert inputs[key]==hashlib.sha256((o/('anti-missile-pod'+suffix)).read_bytes()).hexdigest()
ious={}
for f in [16,31,46]:
 x=Image.open(poses/f'native-{f:02}.png').getchannel('A');y=Image.open(poses/f'imported-{f:02}.png').getchannel('A')
 b=x.getbbox();assert b and min(b)>0 and b[2]<288 and b[3]<320
 a=x.point(lambda v:255 if v>127 else 0);b=y.point(lambda v:255 if v>127 else 0)
 intersection=sum(v>0 for v in ImageChops.darker(a,b).tobytes());union=sum(v>0 for v in ImageChops.lighter(a,b).tobytes());ious[str(f)]=intersection/union;assert intersection/union>.98
assert len({hashlib.sha256((poses/f'native-{f:02}.png').read_bytes()).hexdigest() for f in [16,31,46]})==3
proof=dict(legacy_bbox=[17,61,124,148],legacy_aspect=107/87,authored_aspect=ratio,relative_aspect_error=abs(ratio/(107/87)-1),native_bbox=list(native.getchannel('A').getbbox()),imported_rotation_pose_iou=ious,preview_pose_inputs=inputs,derived_sha256={n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']})
(o/'registration-and-rotation-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('POD_RASTERS_VERIFIED',ratio,ious)
