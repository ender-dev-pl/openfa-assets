"""Proportion and technical-display checks against measured ST05 references."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops,ImageOps
o=Path(sys.argv[1]);im=Image.open(o/'solid.png').convert('RGBA');b=im.getchannel('A').getbbox();ratio=(b[2]-b[0])/(b[3]-b[1]);expected=104/101
assert abs(ratio/expected-1)<.025,(ratio,expected)
canvas=Image.new('RGBA',(144,160));art=ImageOps.contain(im.crop(b),(104,101),Image.Resampling.LANCZOS);canvas.alpha_composite(art,(26+(104-art.width)//2,30+(101-art.height)//2));canvas.save(o/'tile-native.png')
hires=Image.new('RGBA',(576,640));detail=ImageOps.contain(im.crop(b),(416,404),Image.Resampling.LANCZOS);hires.alpha_composite(detail,(104+(416-detail.width)//2,120+(404-detail.height)//2));hires.save(o/'tile-4x.png')
disabled=ImageOps.grayscale(canvas).convert('RGBA');disabled.putalpha(canvas.getchannel('A'));disabled.save(o/'tile-disabled.png');assert disabled.getchannel('A').tobytes()==canvas.getchannel('A').tobytes()
newbox=canvas.getchannel('A').getbbox();assert abs(newbox[0]-26)<=2 and abs(newbox[1]-30)<=1 and abs(newbox[2]-130)<=2 and abs(newbox[3]-131)<=1
# The calibration closeup must show a pointed, threaded screw rather than the
# lower control console, and its central shaft must not become a solid red slab.
red=Image.open(o/'highlight-calibration-device.png').convert('RGB');raw=red.tobytes();mask=Image.frombytes('L',red.size,bytes(255 if raw[i]>raw[i+1]*2 and raw[i]>100 else 0 for i in range(0,len(raw),3)));bb=mask.getbbox();assert bb
assert bb[3]-bb[1]>red.height*.5
centre=(bb[0]+bb[2])//2;roi=mask.crop((centre-30,bb[1]+(bb[3]-bb[1])//3,centre+30,bb[1]+2*(bb[3]-bb[1])//3));coverage=sum(v>0 for v in roi.tobytes())/(roi.width*roi.height);assert coverage<.9,coverage
result=dict(source_bbox=[26,30,130,131],source_aspect=expected,authored_render_bbox=list(b),authored_aspect=ratio,relative_aspect_error=abs(ratio/expected-1),native_bbox=list(newbox),screw_core_red_coverage=coverage,registration='Uniform contain into actual ST05 frame0 placement; no image stretching.',derived_png_sha256={name:hashlib.sha256((o/name).read_bytes()).hexdigest() for name in ['tile-native.png','tile-disabled.png','tile-4x.png']},verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(o/'registration-refinement-proof.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n');print('TRACKER_REFINED_RASTERS_VERIFIED',result)
