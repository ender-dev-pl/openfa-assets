"""Authored RIS2 grease, oxidation and handling wear; no source image input."""
import hashlib,json,math,random
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/scaffolds/rigellian/size-2-refined'
ROOT.mkdir(parents=True,exist_ok=True)
for kind,base in [('green',(.065,.18,.12)),('copper',(.23,.105,.045))]:
    rng=random.Random(983);colour=Image.new('RGB',(256,256));rough=Image.new('L',(256,256));pixels=[];values=[]
    for y in range(256):
        for x in range(256):
            stain=.32*(.5+.5*math.sin(x*.07+math.cos(y*.05)))*(.5+.5*math.sin(y*.04))
            dirt=.24*math.exp(-((y-18)/14)**2)+stain
            noise=rng.uniform(-.012,.012)
            linear=[max(0,min(1,c*(1-dirt)+.025*dirt+noise)) for c in base]
            pixels.append(tuple(round(255*(12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055)) for c in linear))
            values.append(round(255*min(.9,.52+dirt+noise)))
    colour.putdata(pixels);rough.putdata(values);draw=ImageDraw.Draw(colour)
    for _ in range(85):
        x=rng.randrange(256);y=rng.randrange(256);draw.line((x,y,min(255,x+rng.randrange(2,8)),min(255,y+1)),fill=(137,147,138) if kind=='green' else (160,135,92),width=1)
    # Oxide gathers along the exposed section edges; bright short handling
    # scratches remain sparse enough to preserve the culture colours.
    for edge in [2,3,252,253]:
        draw.line((edge,0,edge,255),fill=(37,72,49) if kind=='green' else (55,69,48))
    colour.save(ROOT/f'{kind}-colour.png');rough.save(ROOT/f'{kind}-roughness.png')
images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('*.png')) if p.name.startswith(('green-','copper-'))}
(ROOT/'authored-wear.json').write_text(json.dumps(dict(generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),method='Analytic oxidation/grease and deterministic scuffs, no legacy image input',images=images),indent=2)+'\n')
print('RIS2_WEAR_OK')
