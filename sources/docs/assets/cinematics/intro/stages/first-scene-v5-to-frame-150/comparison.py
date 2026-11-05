from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).resolve().parent;refs=p.parent.parent/'reference/intro-gdv-remaster/continuation-to-150/frames';out=Image.new('RGB',(640,1200));d=ImageDraw.Draw(out)
for row,n in enumerate([100,110,120,150]):
 for col,f in enumerate([refs/f'frame-{n:06d}.png',p/'rendered-frames'/f'frame-{2*n:06d}.png']):
  out.paste(Image.open(f).convert('RGB').resize((320,280)),(col*320,row*300+20))
 d.text((5,row*300+3),f'Original frame {n} / {n/12:.3f}s             LEGACY | BLENDER',fill='white')
out.save(p/'continuation-comparison.jpg',quality=94)
