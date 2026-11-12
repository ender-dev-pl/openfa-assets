"""Seeded paint wear for the authored extension missiles, no legacy inputs."""
from pathlib import Path
import random
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'sources/materials/extensions/munitions';out.mkdir(parents=True,exist_ok=True)
    palette=[(22,55,99),(221,168,19),(165,170,174),(40,44,48),(25,91,143)]
    rng=np.random.default_rng(240);size=1024;tile=256;colour=np.zeros((size,size,3));orm=np.zeros_like(colour)
    for n in range(16):
        x,y=n%4*tile,n//4*tile;yy,xx=np.indices((tile,tile));edge=np.minimum.reduce([xx,yy,255-xx,255-yy])
        noise=rng.normal(0,2.4,(tile,tile));field=Image.fromarray(rng.integers(0,255,(12,12),dtype=np.uint8)).resize((tile,tile),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(5))
        weather=(np.asarray(field).astype(float)-128)/15;dirt=np.exp(-edge/12)*.25
        for c,v in enumerate(palette[n%5]):colour[y:y+tile,x:x+tile,c]=v*(1-dirt)+noise+weather
        orm[y:y+tile,x:x+tile,0]=255-dirt*100;orm[y:y+tile,x:x+tile,1]=110+noise*2+weather*3+dirt*120;orm[y:y+tile,x:x+tile,2]=200 if n%5!=3 else 175
    im=Image.fromarray(np.uint8(np.clip(colour,0,255)));d=ImageDraw.Draw(im);r=random.Random(240)
    for _ in range(700):
        x=r.randrange(size);y=r.randrange(size);d.line((x,y,x+r.randrange(2,8),y+r.choice([-1,0,1])),fill=r.choice([(92,99,104),(65,72,80),(139,142,137)]),width=1)
    im.save(out/'base-colour.png');Image.fromarray(np.uint8(np.clip(orm,0,255))).save(out/'orm.png')


if __name__=='__main__':main()
