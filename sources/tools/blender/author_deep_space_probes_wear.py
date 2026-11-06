"""Independent RI12 wear maps, generated analytically without legacy image input."""
import hashlib
import json
import math
import random
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_filtration_wear import srgb

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/buildings/rigellian/deep-space-probes'
SIZE=1024


def cap_maps():
    size=512;colour=Image.new('RGB',(size,size));rough=Image.new('L',(size,size));colours=[];values=[]
    for row in range(size):
        y=1-2*(row+.5)/size
        for column in range(size):
            x=2*(column+.5)/size-1;r=math.hypot(x,y)
            noise=math.sin(x*39+math.sin(y*23))*math.sin(y*51+math.cos(x*31))
            rim=.22*math.exp(-((r-.93)/.06)**2)
            stain=.25*math.exp(-((x+.20)/.24)**2-((y-.15)/.35)**2)
            abrasion=.06*math.exp(-((y-.17*x-.10)/.018)**2)*math.exp(-((x+.20)/.26)**2)
            dirt=min(.6,(rim+stain)*(1+.2*noise))
            colours.append(tuple(srgb(c*(1-dirt)+d*dirt+abrasion+noise*.0015) for c,d in zip([.12,.29,.22],[.035,.052,.031])))
            values.append(round(255*min(.9,max(.3,.52+dirt*.5-abrasion+noise*.01))))
    colour.putdata(colours);rough.putdata(values)
    colour.save(ROOT/'authored-cap-colour.png');rough.save(ROOT/'authored-cap-roughness.png')


def copper_maps():
    size=512;colour=Image.new('RGB',(size,size));rough=Image.new('L',(size,size));colours=[];values=[]
    for row in range(size):
        z=2.83-(row+.5)*.80/size
        for column in range(size):
            phi=-math.pi+(column+.5)*math.tau/size
            grain=math.sin(phi*113+math.sin(z*61))*.5+math.sin(z*1860)*.5
            end_stain=sum(math.exp(-((z-height)/.045)**2) for height in [2.09,2.75])
            patch=math.exp(-(math.atan2(math.sin(phi+1.4),math.cos(phi+1.4))/.5)**2-((z-2.62)/.11)**2)
            oxide=min(.65,.35*end_stain+.42*patch)
            colours.append(tuple(srgb(c*(1-oxide)+d*oxide+grain*.004) for c,d in zip([.32,.19,.075],[.038,.095,.065])))
            values.append(round(255*min(.9,max(.3,.46+oxide*.4+grain*.035))))
    colour.putdata(colours);rough.putdata(values)
    colour.save(ROOT/'authored-copper-colour.png');rough.save(ROOT/'authored-copper-roughness.png')


def main():
    ROOT.mkdir(parents=True,exist_ok=True);colour=Image.new('RGB',(SIZE,SIZE));rough=Image.new('L',(SIZE,SIZE))
    colours=[];values=[]
    for y in range(SIZE):
        z=(1-(y+.5)/SIZE)*4.2
        for x in range(SIZE):
            phi=-math.pi+(x+.5)*math.tau/SIZE;delta=lambda angle:math.atan2(math.sin(phi-angle),math.cos(phi-angle))
            noise=math.sin(phi*31+math.sin(z*41))*math.sin(z*71+math.cos(phi*17))
            joint=sum(math.exp(-((z-height)/.008)**2) for height in [.08,.20,.86,.96,2.09,2.81,3.25,3.65])
            handling=sum(math.exp(-(delta(-1.35)/.22)**2-((z-height)/.12)**2) for height in [.22,.85,1.7,2.8])
            stain=.25*math.exp(-(delta(.5)/.28)**2-((z-1.65)/.34)**2)
            dirt=min(.65,(joint*.32+handling*.12+stain)*(1+.04*noise))
            colours.append(tuple(srgb(c*(1-dirt)+d*dirt+noise*.003) for c,d in zip([.12,.29,.22],[.035,.052,.031])))
            values.append(round(255*min(.9,.50+dirt*.5+noise*.012)))
    colour.putdata(colours);rough.putdata(values);mask=Image.new('L',(SIZE,SIZE));draw=ImageDraw.Draw(mask);rng=random.Random(984)
    for _ in range(65):
        x=rng.randint(235,330);y=rng.choice([260,570,810])+rng.randint(-45,45)
        draw.line((x,y,x+rng.randint(1,5),y+rng.randint(-2,2)),fill=rng.randint(55,140),width=1)
    mask=mask.filter(ImageFilter.GaussianBlur(.35))
    colour=Image.composite(Image.new('RGB',(SIZE,SIZE),tuple(srgb(c) for c in [.32,.37,.33])),colour,mask)
    rough=Image.composite(Image.new('L',(SIZE,SIZE),90),rough,mask)
    colour.save(ROOT/'authored-shell-colour.png');rough.save(ROOT/'authored-shell-roughness.png')
    cap_maps();copper_maps()
    manifest=dict(issue=984,generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        authoring='Analytic local gasket contamination, handling marks, stains and deterministic scratches; no legacy image input',
        resolution=[SIZE,SIZE],cap_resolution=[512,512],uv='Shell: U=(atan2(y,x)+pi)/(2*pi), V=Z/4.2; end caps: XY plane normalized by actual cap radius; copper: cylindrical U and V=(Z-2.03)/.80',
        images={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['authored-shell-colour.png','authored-shell-roughness.png','authored-cap-colour.png','authored-cap-roughness.png','authored-copper-colour.png','authored-copper-roughness.png']})
    (ROOT/'authored-wear.json').write_text(json.dumps(manifest,indent=2)+'\n');print('RI12_AUTHORED_WEAR_OK',flush=True)


if __name__=='__main__': main()
