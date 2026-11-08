"""Issue 234: independently authored portable paint/alloy wear, no legacy pixels."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'sources/materials/achaean/dedicated-ore-transporter'
PALETTE=['954C2C','7C2C27','A1A29A','242B2D','B7B7A9','AF8A36','71381F','A65E36',
         '652521','6E7472','444C4B','C3C0AE','895436','354140','B96A40','8E3430']


def main():
    OUT.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(234)
    colour=np.zeros((2048,2048,3),dtype=np.uint8);orm=np.zeros_like(colour)
    yy,xx=np.mgrid[:512,:512]/511
    for tile,hexvalue in enumerate(PALETTE):
        base=np.array(tuple(bytes.fromhex(hexvalue)),dtype=float)
        edge=np.minimum.reduce([xx,yy,1-xx,1-yy]);value=.96-.10*np.exp(-edge*45)+rng.normal(0,.012,xx.shape)
        for _ in range(19):
            cx,cy=rng.random(2);sx,sy=rng.uniform(.02,.09,2)
            value-=rng.uniform(.015,.075)*np.exp(-((xx-cx)/sx)**2-((yy-cy)/sy)**2)
        for _ in range(125):
            x,y=rng.integers(10,490,2);length=rng.integers(2,14)
            value[y,x:x+length]+=rng.uniform(.04,.14)
            value[y+1,x:x+length]-=.025
        rgb=np.clip(value[:,:,None]*base,0,255).astype(np.uint8)
        row,col=divmod(tile,4);sl=(slice(row*512,(row+1)*512),slice(col*512,(col+1)*512))
        colour[sl]=rgb
        metal=210 if tile in (2,4,9,11) else 115 if tile not in (3,10,13) else 155
        rough=98 if tile in (2,4,11) else 155 if tile in (3,10,13) else 137
        orm[sl+(0,)]=255;orm[sl+(1,)]=np.clip(rough+(1-value)*95,50,235).astype(np.uint8);orm[sl+(2,)]=metal
    Image.fromarray(colour).save(OUT/'base-colour.png',optimize=True)
    Image.fromarray(orm).save(OUT/'occlusion-roughness-metallic.png',optimize=True)
    print('ACHAEAN_WORN_MAPS_READY',OUT.name)


if __name__=='__main__':main()
