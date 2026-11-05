from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent;refs=p.parent.parent/'reference/intro-gdv-remaster';out=Image.new('RGB',(640,1040));d=ImageDraw.Draw(out)
for row,n in enumerate([150,176,308,400]):
 folder=refs/('first-scene' if n<96 else 'continuation-to-150' if n<=150 else 'continuation-to-412')/'frames';raw=Image.open(folder/f'frame-{n:06d}.png').convert('RGB').resize((640,262),Image.Resampling.LANCZOS);legacy=Image.new('RGB',(640,480));legacy.paste(raw,(0,109));render=Image.open(p/'rendered-frames'/f'frame-{n*2:06d}.png').convert('RGB')
 out.paste(legacy.resize((320,240)),(0,row*260+20));out.paste(render.resize((320,240)),(320,row*260+20));d.text((5,row*260+3),f'Original frame {n} / {n/12:.3f}s                 LEGACY | BLENDER',fill='white')
out.save(p/'sequence-comparison.jpg',quality=94)
