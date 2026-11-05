import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops
out=Path(sys.argv[1]);im=Image.open(out/'solid.png').convert('RGBA');assert im.size==(576,640)
im.save(out/'tile-4x.png');native=im.resize((144,160),Image.Resampling.LANCZOS);native.save(out/'tile-native.png')
disabled=ImageOps.grayscale(native).convert('RGBA');disabled.putalpha(native.getchannel('A'));disabled.save(out/'tile-disabled.png');assert disabled.getchannel('A').tobytes()==native.getchannel('A').tobytes()
b=native.getchannel('A').getbbox();assert b==(0,0,144,160),b
rgb=native.tobytes();assert sum(rgb[i+2]>70 and rgb[i+2]>rgb[i+1]*1.5 and rgb[i+2]>rgb[i]*1.5 and rgb[i+3]>127 for i in range(0,len(rgb),4))>100,'Solid preview must show blue fields'
poses=out.parent/'armour-preview-poses';inputs=json.loads((poses/'inputs.json').read_text());assert inputs['blend_sha256']==hashlib.sha256((out/'building-armour.blend').read_bytes()).hexdigest();assert inputs['glb_sha256']==hashlib.sha256((out/'building-armour.glb').read_bytes()).hexdigest()
ious={}
for frame in [16,31,46]:
 a=Image.open(poses/f'native-{frame:02}.png').getchannel('A').point(lambda x:255 if x>127 else 0);b=Image.open(poses/f'imported-{frame:02}.png').getchannel('A').point(lambda x:255 if x>127 else 0);intersection=sum(x>0 for x in ImageChops.darker(a,b).tobytes());union=sum(x>0 for x in ImageChops.lighter(a,b).tobytes());ious[str(frame)]=intersection/union;assert intersection/union>.98,(frame,intersection/union)
assert len({hashlib.sha256((poses/f'native-{f:02}.png').read_bytes()).hexdigest() for f in [16,31,46]})==3
(out/'registration-and-rotation-proof.json').write_text(json.dumps(dict(legacy_canvas=[144,160],legacy_bbox=[0,0,144,160],native_bbox=[0,0,144,160],registration='Fixed 4x frame; no recrop or stretching',imported_rotation_pose_iou=ious,preview_pose_inputs=inputs,derived_sha256={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['tile-native.png','tile-disabled.png','tile-4x.png']}),indent=2)+'\n',newline='\n');print('ARMOUR_RASTERS_VERIFIED')
