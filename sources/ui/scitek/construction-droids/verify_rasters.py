import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
out=Path(sys.argv[1]);im=Image.open(out/'solid.png').convert('RGBA');bbox=im.getchannel('A').getbbox();ratio=(bbox[2]-bbox[0])/(bbox[3]-bbox[1]);assert abs(ratio/(119/120)-1)<.04,(bbox,ratio)
def tile(scale):
 canvas=Image.new('RGBA',(144*scale,160*scale));art=ImageOps.contain(im.crop(bbox),(119*scale,120*scale),Image.Resampling.LANCZOS);canvas.alpha_composite(art,(3*scale+(119*scale-art.width)//2,14*scale+(120*scale-art.height)//2));return canvas
native=tile(1);native.save(out/'tile-native.png');tile(4).save(out/'tile-4x.png');disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(out/'tile-disabled.png')
b=native.getchannel('A').getbbox();assert abs(b[0]-3)<=2 and abs(b[2]-122)<=2 and abs(b[1]-14)<=2 and abs(b[3]-134)<=2,b
poses=out.parent/'droid-preview-poses';proof=json.loads((poses/'inputs.json').read_text());assert proof['blend_sha256']==hashlib.sha256((out/'construction-droids.blend').read_bytes()).hexdigest();assert proof['glb_sha256']==hashlib.sha256((out/'construction-droids.glb').read_bytes()).hexdigest()
ious={}
for frame in proof['frames']:
 a=Image.open(poses/f'native-{frame:03}.png').getchannel('A').point(lambda x:255 if x>127 else 0);b=Image.open(poses/f'imported-{frame:03}.png').getchannel('A').point(lambda x:255 if x>127 else 0);inter=sum(v>0 for v in ImageChops.darker(a,b).tobytes());union=sum(v>0 for v in ImageChops.lighter(a,b).tobytes());ious[str(frame)]=inter/union;assert inter/union>.98,(frame,inter/union)
assert len({hashlib.sha256((poses/f'native-{frame:03}.png').read_bytes()).hexdigest() for frame in proof['frames']})>=6
spark_pixels={}
for kind in ['native','imported']:
 image=Image.open(poses/f'{kind}-061.png').convert('RGB');spark_pixels[kind]=sum(r>90 and g>55 and b<120 and g>b*1.4 for r,g,b in image.crop((0,260,288,320)).get_flattened_data());assert spark_pixels[kind]>=8,('Welding burst must be visible at its onset',kind,spark_pixels[kind])
(out/'registration-and-articulation-proof.json').write_text(json.dumps(dict(legacy_bbox=[3,14,122,134],native_bbox=list(native.getchannel('A').getbbox()),native_studio_aspect=ratio,relative_aspect_error=abs(ratio/(119/120)-1),imported_articulated_pose_iou=ious,preview_pose_inputs=proof,burst_onset_gold_pixels=spark_pixels,derived_sha256={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']}),indent=2)+'\n',newline='\n');print('DROID_RASTERS_VERIFIED')
