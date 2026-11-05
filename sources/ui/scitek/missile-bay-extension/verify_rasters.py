import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
o=Path(sys.argv[1]);im=Image.open(o/'solid.png').convert('RGBA');b=im.getchannel('A').getbbox();ratio=(b[2]-b[0])/(b[3]-b[1]);assert abs(ratio/(100/160)-1)<.04,(b,ratio)
def tile(scale):
 canvas=Image.new('RGBA',(144*scale,160*scale));art=ImageOps.contain(im.crop(b),(100*scale,160*scale),Image.Resampling.LANCZOS);canvas.alpha_composite(art,(22*scale+(100*scale-art.width)//2,(160*scale-art.height)//2));return canvas
native=tile(1);native.save(o/'tile-native.png');tile(4).save(o/'tile-4x.png');disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(o/'tile-disabled.png')
bb=native.getchannel('A').getbbox();assert abs(bb[0]-22)<=2 and abs(bb[2]-122)<=2 and abs(bb[1])<=2 and abs(bb[3]-160)<=2,bb
poses=o.parent/'bay-preview-poses-ready';proof=json.loads((poses/'inputs.json').read_text());assert proof['blend_sha256']==hashlib.sha256((o/'missile-bay-extension.blend').read_bytes()).hexdigest();assert proof['glb_sha256']==hashlib.sha256((o/'missile-bay-extension.glb').read_bytes()).hexdigest()
ious={}
for f in proof['frames']:
 a=Image.open(poses/f'native-{f:03}.png').getchannel('A').point(lambda v:255 if v>127 else 0);b=Image.open(poses/f'imported-{f:03}.png').getchannel('A').point(lambda v:255 if v>127 else 0);inter=sum(v>0 for v in ImageChops.darker(a,b).tobytes());union=sum(v>0 for v in ImageChops.lighter(a,b).tobytes());ious[str(f)]=inter/union;assert inter/union>.98,(f,inter/union)
assert len({hashlib.sha256((poses/f'native-{f:03}.png').read_bytes()).hexdigest() for f in proof['frames']})>=4
(o/'registration-and-articulation-proof.json').write_text(json.dumps(dict(legacy_bbox=[22,0,122,160],native_bbox=list(bb),native_studio_aspect=ratio,relative_aspect_error=abs(ratio/(100/160)-1),imported_articulated_pose_iou=ious,preview_pose_inputs=proof,derived_sha256={n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']}),indent=2)+'\n');print('MISSILE_BAY_RASTERS_VERIFIED')
