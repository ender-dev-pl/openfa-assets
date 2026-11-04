"""Independent RI10 wear maps, generated analytically without legacy image input."""
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_filtration_wear import srgb

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/buildings/rigellian/ground-deck'
SIZE=1024


def cap_maps():
    size=512;colour=Image.new('RGB',(size,size));rough=Image.new('L',(size,size));colours=[];values=[]
    for row in range(size):
        y=1-2*(row+.5)/size
        for column in range(size):
            x=2*(column+.5)/size-1;r=math.hypot(x,y)
            noise=math.sin(x*39+math.sin(y*23))*math.sin(y*51+math.cos(x*31))
            rim=.22*math.exp(-((r-.93)/.06)**2)
            stain=.48*math.exp(-((x-.15)/.24)**2-((y+.18)/.35)**2)
            abrasion=.06*math.exp(-((y-.17*x-.10)/.018)**2)*math.exp(-((x-.15)/.26)**2)
            dirt=min(.6,(rim+stain)*(1+.2*noise))
            colours.append(tuple(srgb(c*(1-dirt)+d*dirt+abrasion+noise*.0006) for c,d in zip([.12,.26,.19],[.025,.040,.028])))
            values.append(round(255*min(.9,max(.3,.52+dirt*.5-abrasion+noise*.01))))
    colour.putdata(colours);rough.putdata(values)
    marks=Image.new('L',(size,size));draw=ImageDraw.Draw(marks);rng=random.Random(980)
    for _ in range(110):
        x=rng.randrange(20,size-20);y=rng.randrange(20,size-20)
        if .62<math.hypot(2*x/size-1,2*y/size-1)<.97:
            draw.line((x,y,x+rng.randint(2,10),y+rng.randint(-3,3)),fill=rng.randint(55,150),width=1)
    colour=Image.composite(Image.new('RGB',(size,size),tuple(srgb(c) for c in [.35,.44,.37])),colour,marks)
    rough=Image.composite(Image.new('L',(size,size),95),rough,marks)
    colour.save(ROOT/'authored-cap-colour.png');rough.save(ROOT/'authored-cap-roughness.png')


def main():
    ROOT.mkdir(parents=True,exist_ok=True);colour=Image.new('RGB',(SIZE,SIZE));rough=Image.new('L',(SIZE,SIZE))
    colours=[];values=[]
    for y in range(SIZE):
        z=(1-(y+.5)/SIZE)*1.6
        for x in range(SIZE):
            phi=-math.pi+(x+.5)*math.tau/SIZE;delta=lambda angle:math.atan2(math.sin(phi-angle),math.cos(phi-angle))
            noise=math.sin(phi*31+math.sin(z*41))*math.sin(z*71+math.cos(phi*17))
            joint=sum(math.exp(-((z-height)/.04)**2) for height in [.06,.28,.36,1.18,1.36])
            handling=sum(math.exp(-(delta(-1.35)/.22)**2-((z-height)/.28)**2) for height in [.12,.25,.65,1.28])
            stain=.48*math.exp(-(delta(.5)/.28)**2-((z-1.25)/.40)**2)
            dirt=min(.65,(joint*.45+handling*.28+stain)*(1+.04*noise))
            colours.append(tuple(srgb(c*(1-dirt)+d*dirt+noise*.0004) for c,d in zip([.12,.26,.19],[.025,.040,.028])))
            values.append(round(255*min(.9,.50+dirt*.5+noise*.002)))
    colour.putdata(colours);rough.putdata(values);mask=Image.new('L',(SIZE,SIZE));draw=ImageDraw.Draw(mask);rng=random.Random(980)
    for _ in range(65):
        x=rng.randint(235,330);y=rng.choice([480,630,800])+rng.randint(-45,45)
        draw.line((x,y,x+rng.randint(1,5),y+rng.randint(-2,2)),fill=rng.randint(55,140),width=1)
    mask=mask.filter(ImageFilter.GaussianBlur(.35))
    colour=Image.composite(Image.new('RGB',(SIZE,SIZE),tuple(srgb(c) for c in [.31,.40,.33])),colour,mask)
    rough=Image.composite(Image.new('L',(SIZE,SIZE),90),rough,mask)
    colour.save(ROOT/'authored-shell-colour.png');rough.save(ROOT/'authored-shell-roughness.png')
    cap_maps()
    manifest=dict(issue=980,generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        authoring='Analytic local gasket contamination, handling marks, stains and deterministic scratches; no legacy image input',
        resolution=[SIZE,SIZE],cap_resolution=[512,512],uv='Shell: U=(atan2(y,x)+pi)/(2*pi), V=Z/1.6; end caps: XY plane normalized by each object XY bounds',
        images={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['authored-shell-colour.png','authored-shell-roughness.png','authored-cap-colour.png','authored-cap-roughness.png']})
    (ROOT/'authored-wear.json').write_text(json.dumps(manifest,indent=2)+'\n');print('RI10_AUTHORED_WEAR_OK',flush=True)


if __name__=='__main__': main()
