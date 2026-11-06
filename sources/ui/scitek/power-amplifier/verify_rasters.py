import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
o=Path(sys.argv[1]);im=Image.open(o/'solid.png').convert('RGBA');b=im.getchannel('A').getbbox();ratio=(b[2]-b[0])/(b[3]-b[1]);assert abs(ratio/(50/146)-1)<.03
def tile(scale):
    canvas=Image.new('RGBA',(144*scale,160*scale));art=ImageOps.contain(im.crop(b),(50*scale,146*scale),Image.Resampling.LANCZOS);canvas.alpha_composite(art,(47*scale+(50*scale-art.width)//2,7*scale+(146*scale-art.height)//2));return canvas
native=tile(1);native.save(o/'tile-native.png');tile(4).save(o/'tile-4x.png');disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(o/'tile-disabled.png')
bb=native.getchannel('A').getbbox();assert abs(bb[0]-47)<=2 and abs(bb[2]-97)<=2 and abs(bb[1]-7)<=2 and abs(bb[3]-153)<=2
ious={}
poses=o.parent/'amplifier-preview-poses'
inputs=json.loads((poses/'inputs.json').read_text());assert inputs['blend_sha256']==hashlib.sha256((o/'power-amplifier.blend').read_bytes()).hexdigest();assert inputs['glb_sha256']==hashlib.sha256((o/'power-amplifier.glb').read_bytes()).hexdigest()
for f in [16,31,46]:
    x=Image.open(poses/f'native-{f:02}.png').getchannel('A').point(lambda v:255 if v>127 else 0);y=Image.open(poses/f'imported-{f:02}.png').getchannel('A').point(lambda v:255 if v>127 else 0)
    inter=sum(v>0 for v in ImageChops.darker(x,y).tobytes());union=sum(v>0 for v in ImageChops.lighter(x,y).tobytes());ious[str(f)]=inter/union;assert inter/union>.98,(f,inter/union)
assert len({hashlib.sha256((poses/f'native-{f:02}.png').read_bytes()).hexdigest() for f in [16,31,46]})==3
result=dict(legacy_bbox=[47,7,97,153],legacy_aspect=50/146,authored_aspect=ratio,relative_aspect_error=abs(ratio/(50/146)-1),native_bbox=list(bb),imported_rotation_pose_iou=ious,preview_pose_inputs=json.loads((poses/'inputs.json').read_text()),derived_sha256={n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']})
(o/'registration-and-rotation-proof.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n');print('AMPLIFIER_RASTERS_AND_ROTATION_VERIFIED',result)
