from PIL import Image,ImageDraw
from pathlib import Path
import json,numpy as np
p=Path(__file__).resolve().parent;d=json.loads((p/'pose-fit.json').read_text());old=json.loads((p/'camera-model.json').read_text());points=np.array([[-1.35,-2.78,0,1],[1.35,-2.78,0,1]])
metrics=[]
for r in d['landmarks'][1:]:
 n=r['source_frame'];m=np.array(next(z for z in old['poses'] if z['source_frame']==n)['camera_matrix']);v=points@m.T;uv=np.c_[160+400*v[:,0]/-v[:,2],140-400*v[:,1]/-v[:,2]];target=np.array(r['target'])[:2]
 metrics.append(dict(source_frame=n,old_nozzle_rmse_pixels=float(np.sqrt(np.mean((uv-target)**2))),new_nozzle_rmse_pixels=r['nozzle_rmse']))
(p/'pose-validation.json').write_text(json.dumps(dict(note='Residuals against approximate manually annotated nozzle centres, not independent accuracy measurements.',samples=metrics),indent=2))
im=Image.new('RGB',(960,1200));dr=ImageDraw.Draw(im)
for row,n in enumerate([0,36,60,95]):
 files=[p.parent.parent/'reference/intro-gdv-remaster/first-scene/frames'/f'frame-{n:06d}.png',p.parent/'first-scene-v3-nebula/rendered-frames'/f'frame-{2*n:06d}.png',p/'preview'/f'frame-{n:03d}.png']
 for col,f in enumerate(files):im.paste(Image.open(f).resize((320,280)),(col*320,row*300+20))
 dr.text((5,row*300+3),f'{n/12:.2f}s | LEGACY                               PREVIOUS                             SHIP FIT',fill='white')
im.save(p/'pose-comparison.jpg',quality=93)
print(json.dumps(metrics))
