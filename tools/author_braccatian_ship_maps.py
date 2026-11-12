"""Deterministic authored PBR wear, without original-game pixels or panel grids."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sources/materials/braccatian/mobile-ships'
COLOURS=[(192,154,85),(158,84,73),(93,106,116),(29,34,39),(116,86,49),(147,155,159),(13,17,20),(109,67,59)]


def main():
    OUT.mkdir(parents=True,exist_ok=True);size=512;rng=np.random.default_rng(244)
    maps={k:Image.new('RGB',(size*4,size*2)) for k in ['colour','orm','normal']}
    for tile,colour in enumerate(COLOURS):
        coarse=Image.fromarray(rng.integers(0,255,(24,24),dtype=np.uint8)).resize((size,size),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(10))
        noise=(np.asarray(coarse,dtype=float)/255-.5)*.13+rng.normal(0,.012,(size,size))
        base=np.clip(np.asarray(colour)[None,None,:]*(1+noise[:,:,None]),0,255).astype('uint8');image=Image.fromarray(base)
        height=Image.new('L',(size,size),128);hd=ImageDraw.Draw(height);d=ImageDraw.Draw(image)
        # Isolated scuffs, little stains and machining scratches; no tiled plates.
        for i in range(190):
            x,y=map(int,rng.integers(10,size-10,2));length=int(rng.integers(2,21));shade=tuple(int(v*.65) for v in colour)
            d.line((x,y,x+length,y+int(rng.integers(-2,3))),fill=shade,width=1);hd.line((x,y,x+length,y+1),fill=95,width=1)
        for i in range(45):
            x,y=map(int,rng.integers(4,size-12,2));r=int(rng.integers(1,4));shade=tuple(int(v*.52) for v in colour)
            d.ellipse((x-r,y-r,x+r,y+r),fill=shade);hd.ellipse((x-r,y-r,x+r,y+r),fill=116)
        h=np.asarray(height.filter(ImageFilter.GaussianBlur(.45)),dtype=float)/255
        gy,gx=np.gradient(h);n=np.stack((-gx*1.6,-gy*1.6,np.ones_like(h)),axis=-1);n/=np.linalg.norm(n,axis=-1)[:,:,None]
        normal=Image.fromarray(np.clip((n*.5+.5)*255,0,255).astype('uint8'))
        # Concept/GLB feedback: broad polished highlights masked the used alloy.
        rough=np.clip((.57+noise*1.35+(128-np.asarray(height,dtype=float))*.003)*255,70,235).astype('uint8')
        metal=np.full((size,size),int((.80 if tile not in [3,6] else .15)*255),dtype='uint8')
        orm=Image.fromarray(np.stack((np.full_like(rough,255),rough,metal),axis=-1))
        xy=(tile%4*size,tile//4*size)
        for key,im in [('colour',image),('orm',orm),('normal',normal)]:maps[key].paste(im,xy)
    for key,im in maps.items():im.save(OUT/(key+'.png'),optimize=True)
    report=dict(seed=244,size=[2048,1024],tiles=['ochre-gold','rose-copper','slate-armour','dark-metal','tarnished-brass','silver-alloy','recess','copper-trim'],original_pixels=False,dense_panel_grid=False,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')})
    (OUT/'authored-maps.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_MAPS',report)


if __name__=='__main__':main()
