import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
o=Path(sys.argv[1]);poses=o.parent/'anti-virus-preview-poses';im=Image.open(o/'solid.png').convert('RGBA');b=im.getchannel('A').getbbox();ratio=(b[2]-b[0])/(b[3]-b[1]);assert abs(ratio/(30/131)-1)<.03
def tile(scale):
 canvas=Image.new('RGBA',(80*scale,160*scale));art=ImageOps.contain(im.crop(b),(30*scale,131*scale),Image.Resampling.LANCZOS)
 canvas.alpha_composite(art,(25*scale+(30*scale-art.width)//2,16*scale+(131*scale-art.height)//2));return canvas
native=tile(1);native.save(o/'tile-native.png');tile(4).save(o/'tile-4x.png');disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(o/'tile-disabled.png')
bb=native.getchannel('A').getbbox();assert all(abs(a-c)<=2 for a,c in zip(bb,[25,16,55,147])),bb
inputs=json.loads((poses/'inputs.json').read_text());ious={}
for key,suffix in [('blend_sha256','.blend'),('glb_sha256','.glb')]:assert inputs[key]==hashlib.sha256((o/('anti-virus-missile'+suffix)).read_bytes()).hexdigest()
for f in [16,31,46]:
 x=Image.open(poses/f'native-{f:02}.png').getchannel('A');y=Image.open(poses/f'imported-{f:02}.png').getchannel('A');box=x.getbbox();assert box and min(box)>0 and box[2]<160 and box[3]<320
 a=x.point(lambda v:255 if v>127 else 0);bb=y.point(lambda v:255 if v>127 else 0);intersection=sum(v>0 for v in ImageChops.darker(a,bb).tobytes());union=sum(v>0 for v in ImageChops.lighter(a,bb).tobytes());ious[str(f)]=intersection/union;assert intersection/union>.98
assert len({hashlib.sha256((poses/f'native-{f:02}.png').read_bytes()).hexdigest() for f in [16,31,46]})==3
proof=dict(legacy_canvas=[80,160],legacy_bbox=[25,16,55,147],legacy_aspect=30/131,authored_aspect=ratio,relative_aspect_error=abs(ratio/(30/131)-1),native_bbox=list(native.getchannel('A').getbbox()),root_scale=[.83,.83,1],imported_rotation_pose_iou=ious,preview_pose_inputs=inputs,derived_sha256={n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']})
(o/'registration-and-rotation-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('ANTI_VIRUS_RASTERS_VERIFIED',ratio,ious)
