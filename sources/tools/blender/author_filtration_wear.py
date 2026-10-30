"""Author RI02 colour/roughness maps from analytic wear fields; no source pixels."""
import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/buildings/rigellian/filtration-plant'
SIZE=1024


def srgb(value):
    return round(255*(12.92*value if value<=.0031308 else 1.055*value**(1/2.4)-.055))


def main():
    ROOT.mkdir(parents=True,exist_ok=True);colour=Image.new('RGB',(SIZE,SIZE));rough=Image.new('L',(SIZE,SIZE))
    pixels=[];roughness=[]
    fittings=[(phi,z) for phi in [-math.pi/2-.30,-math.pi/2+.30] for z in [.53,.85,1.17]]+[(-math.pi/2,1.995)]
    angular=[-math.pi+(x+.5)*math.tau/SIZE for x in range(SIZE)]
    for y in range(SIZE):
        z=(1-(y+.5)/SIZE)*2.5
        for phi in angular:
            delta=lambda angle: math.atan2(math.sin(phi-angle),math.cos(phi-angle))
            noise=(math.sin(phi*31+math.sin(z*43))*math.sin(z*83+math.cos(phi*19))+.45*math.sin(phi*73+z*117))/1.45
            grime=0
            for angle,height in fittings:
                ring=math.hypot(delta(angle)*(.34 if height>1.7 else .82),z-height)
                grime+=.48*math.exp(-((ring-.080)/.026)**2)
            seam=sum(math.exp(-((z-height)/.015)**2) for height in [.21,1.32,1.65,1.80,2.315])
            grime+=.28*seam*(.55+.45*math.sin(phi*3+.4)**2)
            stain=.35*math.exp(-(delta(-1.15)/.12)**2-((z-.48)/.30)**2)
            stain+=.24*math.exp(-(delta(1.2)/.30)**2-((z-.75)/.24)**2)
            grime=min(.75,max(0,(grime+stain)*(1+.22*noise)))
            fade=.035*math.exp(-(delta(.8)/.5)**2-((z-.8)/.35)**2)
            base=[.12,.29,.22];dirt=[.035,.052,.031]
            pixels.append(tuple(srgb(max(.001,min(1,c*(1-grime)+d*grime+fade+noise*.0015))) for c,d in zip(base,dirt)))
            roughness.append(round(255*min(.95,.49+grime*.6+noise*.012)))
    colour.putdata(pixels);rough.putdata(roughness)
    # Sparse fine handling scratches concentrated near fittings, not a global pattern.
    scratches=Image.new('L',(SIZE,SIZE));draw=ImageDraw.Draw(scratches);rng=random.Random(971)
    for _ in range(45):
        phi,z=rng.choice(fittings);u=(phi+math.pi)/math.tau
        x=round((u+rng.uniform(-.022,.022))*SIZE);y=round((1-z/2.5+rng.uniform(-.024,.024))*SIZE)
        draw.line((x,y,x+rng.randint(1,5),y+rng.randint(-2,2)),fill=rng.randint(55,145),width=1)
    scratches=scratches.filter(ImageFilter.GaussianBlur(.35))
    rubbed=Image.new('RGB',(SIZE,SIZE),tuple(srgb(c) for c in [.32,.37,.33]))
    colour=Image.composite(rubbed,colour,scratches)
    rough=Image.composite(Image.new('L',(SIZE,SIZE),87),rough,scratches)
    colour.save(ROOT/'authored-shell-colour.png');rough.save(ROOT/'authored-shell-roughness.png')
    manifest=dict(issue=971,authoring='Analytic cylindrical joint/fitting contamination, soft stains and seeded fine scratches; no imported source pixels',
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),resolution=[SIZE,SIZE],
        uv='U=(atan2(y,x)+pi)/(2*pi); V=Z/2.5; image rows run downward',
        images={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['authored-shell-colour.png','authored-shell-roughness.png']})
    (ROOT/'authored-wear.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('RI02_AUTHORED_WEAR_OK',SIZE,flush=True)


if __name__=='__main__': main()
