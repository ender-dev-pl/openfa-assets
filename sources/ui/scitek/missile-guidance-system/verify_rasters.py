import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
o=Path(sys.argv[1]);im=Image.open(o/'solid.png').convert('RGBA');b=im.getchannel('A').getbbox();ratio=(b[2]-b[0])/(b[3]-b[1]);assert abs(ratio/(129/156)-1)<.03
def tile(scale):
    canvas=Image.new('RGBA',(144*scale,160*scale));art=ImageOps.contain(im.crop(b),(129*scale,156*scale),Image.Resampling.LANCZOS);canvas.alpha_composite(art,(8*scale+(129*scale-art.width)//2,1*scale+(156*scale-art.height)//2));return canvas
native=tile(1);native.save(o/'tile-native.png');tile(4).save(o/'tile-4x.png');disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(o/'tile-disabled.png')
bb=native.getchannel('A').getbbox();assert abs(bb[0]-8)<=2 and abs(bb[2]-137)<=2 and bb[1]==1 and bb[3]==157
ious={}
poses=o.parent/'guidance-preview-symmetric-poses'
inputs=json.loads((poses/'inputs.json').read_text());assert inputs['blend_sha256']==hashlib.sha256((o/'missile-guidance-system.blend').read_bytes()).hexdigest();assert inputs['glb_sha256']==hashlib.sha256((o/'missile-guidance-system.glb').read_bytes()).hexdigest()
for f in [16,31,46]:
    x=Image.open(poses/f'native-{f:02}.png').getchannel('A').point(lambda v:255 if v>127 else 0);y=Image.open(poses/f'imported-{f:02}.png').getchannel('A').point(lambda v:255 if v>127 else 0)
    inter=sum(v>0 for v in ImageChops.darker(x,y).tobytes());union=sum(v>0 for v in ImageChops.lighter(x,y).tobytes());ious[str(f)]=inter/union;assert inter/union>.98,(f,inter/union)
assert len({hashlib.sha256((poses/f'native-{f:02}.png').read_bytes()).hexdigest() for f in [16,31,46]})==3
result=dict(legacy_bbox=[8,1,137,157],legacy_aspect=129/156,authored_aspect=ratio,relative_aspect_error=abs(ratio/(129/156)-1),native_bbox=list(bb),imported_rotation_pose_iou=ious,preview_pose_inputs=json.loads((poses/'inputs.json').read_text()),derived_sha256={n:hashlib.sha256((o/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']})
(o/'registration-and-rotation-proof.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n');print('GUIDANCE_RASTERS_AND_ROTATION_VERIFIED',result)
