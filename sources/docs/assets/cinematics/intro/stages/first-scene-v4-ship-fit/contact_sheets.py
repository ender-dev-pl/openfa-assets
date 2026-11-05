from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).resolve().parent;reference=p.parent.parent/'reference/intro-gdv-remaster/first-scene/frames';out=p/'legacy-vs-render';out.mkdir(exist_ok=True)
for page in range(3):
 im=Image.new('RGB',(640,1200));dr=ImageDraw.Draw(im)
 for row in range(4):
  n=(page*4+row)*8
  for col,f in enumerate([reference/f'frame-{n:06d}.png',p/'rendered-frames'/f'frame-{2*n:06d}.png']):
   im.paste(Image.open(f).resize((320,280)),(col*320,row*300+20))
  dr.text((5,row*300+3),f'{n/12:.3f}s / legacy {n} / render {n*2}      LEGACY | SHIP FIT',fill='white')
 im.save(out/f'comparison-{page+1:02d}.jpg',quality=93)
