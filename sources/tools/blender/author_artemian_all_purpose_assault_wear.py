"""Independent planar wear textures; no legacy pixels read."""
import hashlib,json,math,random,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from author_filtration_wear import srgb
ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/ships/artemian/all-purpose-assault'


def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    for style,base in [('hull',(.27,.29,.30)),('green',(.10,.28,.12))]:
        size=1024;colour=Image.new('RGB',(size,size));rough=Image.new('L',(size,size));pixels=[];values=[]
        for y in range(size):
            v=(y+.5)/size
            for x in range(size):
                u=(x+.5)/size;grain=math.sin(u*731+math.sin(v*89))*math.cos(v*1103)
                grime=.12+.18*math.exp(-((u-.18)/.16)**2-((v-.71)/.22)**2)+.22*math.exp(-((u-.78)/.12)**2-((v-.25)/.13)**2)
                pixels.append(tuple(srgb(c*(1-grime)+d*grime+grain*.002) for c,d in zip(base,(.025,.024,.021))))
                values.append(round(255*(.48+grime*.6+grain*.012)))
        colour.putdata(pixels);rough.putdata(values);mask=Image.new('L',(size,size));draw=ImageDraw.Draw(mask);rng=random.Random(1018)
        for i in range(260):
            x=rng.randrange(size);y=rng.randrange(size);draw.line((x,y,x+rng.randrange(1,9),y+rng.randrange(-2,3)),fill=rng.randrange(35,150),width=1)
        mask=mask.filter(ImageFilter.GaussianBlur(.35));colour=Image.composite(Image.new('RGB',(size,size),tuple(srgb(c) for c in (.28,.27,.28))),colour,mask);rough=Image.composite(Image.new('L',(size,size),105),rough,mask)
        colour.save(ROOT/f'authored-{style}-colour.png');rough.save(ROOT/f'authored-{style}-roughness.png')
    report=dict(issue=1018,generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),authoring='Independent analytic stains, grain and seeded scratches; no original image input',images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('authored-*.png'))})
    (ROOT/'authored-wear.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ARTEMIAN_ALL_PURPOSE_ASSAULT_AUTHORED_WEAR_OK',flush=True)


if __name__=='__main__': main()
