"""Independent worn alloy atlas; broad legacy colours, no legacy pixels or plate grid."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sources/materials/mauna/mobile-ships'
COLOURS=[(119,126,132),(65,76,84),(102,131,148),(149,179,191),(17,22,27),(142,88,66),(156,66,59),(151,114,65)]


def main():
    OUT.mkdir(parents=True,exist_ok=True);size=512;rng=np.random.default_rng(251)
    maps={k:Image.new('RGB',(size*4,size*2)) for k in ['colour','orm','normal']}
    for tile,base in enumerate(COLOURS):
        coarse=Image.fromarray(rng.integers(0,255,(24,24),dtype=np.uint8)).resize((size,size),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(9))
        noise=(np.asarray(coarse,dtype=float)/255-.5)*.16+rng.normal(0,.011,(size,size))
        image=Image.fromarray(np.clip(np.asarray(base)[None,None,:]*(1+noise[:,:,None]),0,255).astype('uint8'))
        height=Image.new('L',(size,size),128);h=ImageDraw.Draw(height);d=ImageDraw.Draw(image)
        for _ in range(170):
            x,y=map(int,rng.integers(8,size-28,2));length=int(rng.integers(3,22));shade=tuple(int(v*.66) for v in base)
            end=(x+length,y+int(rng.integers(-3,4)));d.line((x,y,*end),fill=shade,width=1);h.line((x,y,*end),fill=99,width=1)
        for _ in range(36):
            x,y=map(int,rng.integers(8,size-8,2));r=int(rng.integers(1,4));d.ellipse((x-r,y-r,x+r,y+r),fill=tuple(int(v*.55) for v in base));h.ellipse((x-r,y-r,x+r,y+r),fill=116)
        field=np.asarray(height.filter(ImageFilter.GaussianBlur(.5)),dtype=float)/255;gy,gx=np.gradient(field)
        normal=np.stack((-gx*1.6,-gy*1.6,np.ones_like(field)),axis=-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
        normal=Image.fromarray(np.clip((normal*.5+.5)*255,0,255).astype('uint8'))
        rough=np.clip((.60+noise*1.3+(128-np.asarray(height,dtype=float))*.003)*255,65,235).astype('uint8')
        metal=np.full((size,size),int((.74 if tile not in [2,3,4] else .10 if tile==4 else .55)*255),dtype='uint8');orm=Image.fromarray(np.stack((np.full_like(rough,255),rough,metal),axis=-1))
        xy=(tile%4*size,tile//4*size)
        for key,data in [('colour',image),('orm',orm),('normal',normal)]:maps[key].paste(data,xy)
    for key,im in maps.items():im.save(OUT/(key+'.png'),optimize=True)
    report=dict(seed=251,size=[2048,1024],tiles=['grey-structural-alloy','oxidized-alloy','subdued-blue-grey','pale-blue-grey','carbon-recess','warm-oxide','muted-red','brown-bronze'],original_pixels=False,dense_panel_grid=False,sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')})
    (OUT/'authored-maps.json').write_text(json.dumps(report,indent=2)+'\n');print('MAUNA_MAPS_OK',flush=True)


if __name__=='__main__':main()
