"""Analytic RI13 painted-metal wear without any legacy image input."""
import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_filtration_wear import srgb
ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/buildings/rigellian/gravitic-converter'


def create_set(prefix,base):
    for cap,size in [(False,1024),(True,512)]:
        colour=Image.new('RGB',(size,size));rough=Image.new('L',(size,size));colours=[];values=[]
        for row in range(size):
            z=4.2*(1-(row+.5)/size)
            for column in range(size):
                phi=-math.pi+(column+.5)*math.tau/size
                grain=math.sin(phi*47+math.sin(z*33))*math.sin(z*109+math.cos(phi*21))
                if cap:
                    x=2*(column+.5)/size-1;y=1-2*(row+.5)/size
                    dirt=.25*math.exp(-((math.hypot(x,y)-.92)/.07)**2)+.15*math.exp(-((x+.2)/.3)**2-((y-.1)/.4)**2)
                else:
                    joint=sum(math.exp(-((z-h)/.012)**2) for h in [.20,.76,1.045,1.61,2.25,2.95,3.54,3.70,3.88])
                    angle=math.atan2(math.sin(phi+1.5),math.cos(phi+1.5))
                    handling=.15*math.exp(-(angle/.32)**2-((z-2.35)/.25)**2)
                    dirt=min(.65,.3*joint+handling)
                colours.append(tuple(srgb(c*(1-dirt)+d*dirt+grain*.0025) for c,d in zip(base,[.025,.044,.032])))
                values.append(round(255*min(.9,.51+dirt*.42+grain*.015)))
        colour.putdata(colours);rough.putdata(values)
        mask=Image.new('L',(size,size));draw=ImageDraw.Draw(mask);rng=random.Random(985+int(cap))
        for _ in range(90):
            x=rng.randint(0,size-1);y=rng.randint(0,size-1)
            draw.line((x,y,x+rng.randint(1,4),y+rng.randint(-2,2)),fill=rng.randint(45,125),width=1)
        mask=mask.filter(ImageFilter.GaussianBlur(.3))
        colour=Image.composite(Image.new('RGB',(size,size),tuple(srgb(c) for c in [.31,.36,.34])),colour,mask)
        rough=Image.composite(Image.new('L',(size,size),95),rough,mask)
        suffix='cap' if cap else 'shell'
        colour.save(ROOT/f'authored-{prefix}-{suffix}-colour.png');rough.save(ROOT/f'authored-{prefix}-{suffix}-roughness.png')


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    for name,base in [('green',[.10,.23,.16]),('grey',[.26,.32,.34])]: create_set(name,base)
    report=dict(issue=985,generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        authoring='Independent analytic joint contamination, handling marks, grain and seeded scuffs; no legacy image input',
        uv='Local XY cylinder angle U, global Z/4.2 V; local planar end caps normalized by actual radius',
        images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('authored-*.png'))})
    (ROOT/'authored-wear.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('RI13_AUTHORED_WEAR_OK',flush=True)


if __name__=='__main__': main()
