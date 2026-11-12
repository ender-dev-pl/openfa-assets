"""Author deterministic worn-metal PBR maps for the Terran Ship Yard (#225)."""
from pathlib import Path
import random
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
COLOURS=[(126,62,40),(72,82,87),(23,28,31),(188,137,35),(79,78,69),(20,47,60),(225,187,115),(35,40,41),(139,149,148),(96,43,29),(173,124,32),(43,55,57),(102,104,92),(93,69,50),(194,54,17),(120,143,152)]

def build():
    out=ROOT/'sources/materials/terran-shipyard-highdetail';out.mkdir(parents=True,exist_ok=True)
    size=1024;tile=256;rng=random.Random(225)
    colour=Image.new('RGB',(size,size));orm=Image.new('RGB',(size,size));emission=Image.new('RGB',(size,size))
    cd=ImageDraw.Draw(colour);od=ImageDraw.Draw(orm);ed=ImageDraw.Draw(emission)
    for k,base in enumerate(COLOURS):
        x=(k%4)*tile;y=(k//4)*tile
        rough,metal=(140,205) if k in [0,1,8,9,12,13] else (170,95)
        if k==5:rough,metal=60,140
        if k in [6,14]:rough,metal=100,20
        cd.rectangle((x,y,x+255,y+255),fill=base);od.rectangle((x,y,x+255,y+255),fill=(255,rough,metal))
        # Authored micro grain, localized chipped paint and fine scratches. No reference pixels.
        for _ in range(12000):
            u=rng.randrange(3,253);v=rng.randrange(3,253);f=rng.uniform(.82,1.15)
            cd.point((x+u,y+v),fill=tuple(int(min(255,c*f)) for c in base))
        if k not in [5,6,14]:
            for _ in range(180):
                u=rng.randrange(5,249);v=rng.randrange(5,249);length=rng.randrange(1,15)
                col=tuple(int(c*.55) for c in base) if rng.random()<.7 else (121,125,116)
                cd.line((x+u,y+v,x+min(250,u+length),y+v+rng.randrange(-2,3)),fill=col,width=1)
            # Grime near seams and a restrained worn edge, without turning every surface into a grid.
            for inset in range(2,9):
                f=.45+inset*.055
                cd.rectangle((x+inset,y+inset,x+255-inset,y+255-inset),outline=tuple(int(c*f) for c in base))
            for _ in range(24):
                u=rng.randrange(5,250);v=rng.choice([rng.randrange(5,18),rng.randrange(237,250)])
                cd.ellipse((x+u,y+v,x+u+3,y+v+1),fill=(117,116,100))
        if k==10:
            for u in range(-256,512,54):cd.polygon([(x+max(3,min(252,u)),y+3),(x+max(3,min(252,u+23)),y+3),(x+max(3,min(252,u+279)),y+252),(x+max(3,min(252,u+256)),y+252)],fill=(28,30,28))
        if k in [6,14]:ed.rectangle((x+2,y+2,x+253,y+253),fill=(210,162,80) if k==6 else (245,34,5))
    for name,im in [('albedo',colour),('orm',orm),('emission',emission)]:im.save(out/(name+'.png'),optimize=True)
    print('SHIPYARD_SURFACE_MAPS_AUTHORED',out)

if __name__=='__main__':build()
