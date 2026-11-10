"""Seeded green-shell wear atlas; no original pixels used as texture inputs."""
from pathlib import Path
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'sources/materials/achaean/hunter-prospector';out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(238);size=1024;tile=256
    noise=rng.normal(0,1.4,(size,size));coarse=Image.fromarray(rng.integers(0,255,(32,32),dtype=np.uint8)).resize((size,size),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    yy,xx=np.indices((size,size));edge=np.minimum.reduce([xx%tile,yy%tile,tile-1-xx%tile,tile-1-yy%tile])
    dirt=np.exp(-edge/10)*.22;variation=(np.asarray(coarse).astype(float)-128)/22+noise
    base=np.zeros((size,size,3),dtype=np.uint8)
    for i,c in enumerate([76,112,66]):base[:,:,i]=np.clip(c*(1-dirt)+variation,0,255)
    im=Image.fromarray(base);draw=ImageDraw.Draw(im);r=random.Random(238)
    for _ in range(650):
        x=r.randrange(size);y=r.randrange(size);dx=r.randrange(2,17);dy=r.choice([-1,0,1,2])
        draw.line((x,y,x+dx,y+dy),fill=r.choice([(104,122,83),(66,84,51),(119,126,101)]),width=1)
    im.save(out/'green-base-colour.png')
    orm=np.zeros_like(base);orm[:,:,0]=np.clip(255-dirt*100,0,255);orm[:,:,1]=np.clip(152+variation*2+dirt*100,70,230);orm[:,:,2]=165
    Image.fromarray(orm).save(out/'green-occlusion-roughness-metallic.png')


if __name__=='__main__':main()
