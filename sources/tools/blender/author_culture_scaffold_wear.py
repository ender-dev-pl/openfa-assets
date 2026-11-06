"""Original deterministic wear maps; no legacy pixels are copied into materials."""
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from PIL import Image,ImageDraw

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/scaffolds/culture-kits'
# Keep palette definitions importable outside Blender.
COLOURS={
    'terran':[(.22,.28,.32),(.58,.36,.055)],'rigellian':[(.065,.18,.12),(.23,.105,.045)],
    'braccatian':[(.40,.29,.13),(.16,.095,.045)],'mikotaj':[(.27,.34,.36),(.075,.18,.10)],
    'artemian':[(.24,.39,.29),(.13,.22,.17)],'mauna':[(.17,.21,.235),(.45,.11,.035)],
    'achaean':[(.40,.31,.12),(.13,.075,.028)]}


def main():
    records={}
    for culture,colours in COLOURS.items():
        folder=ROOT/'textures'/culture
        folder.mkdir(parents=True,exist_ok=True)
        for kind,base in zip(['main','trim'],colours):
            rng=random.Random(culture+kind+'188')
            image=Image.new('RGB',(256,256));rough=Image.new('L',(256,256))
            pixels=[];values=[]
            for y in range(256):
                for x in range(256):
                    seam=math.exp(-min(x,255-x,y,255-y)/9)
                    grime=.28*seam+.22*(.5+.5*math.sin(x*.08+math.cos(y*.047)))*(.5+.5*math.sin(y*.06))
                    noise=rng.uniform(-.032,.032) if culture=='braccatian' else rng.uniform(-.014,.014)
                    if culture=='achaean':noise+=.025*math.sin(x*.85+math.sin(y*.012))
                    if culture=='mikotaj':noise+=.025*math.sin(x*.07)*math.sin(y*.05)
                    linear=[max(0,min(1,c*(1-grime)+.018*grime+noise)) for c in base]
                    pixels.append(tuple(round(255*(12.92*c if c<.0031308 else 1.055*c**(1/2.4)-.055)) for c in linear))
                    baseline=.58 if culture=='artemian' else (.78 if culture=='braccatian' else .56)
                    values.append(round(255*min(.95,baseline+grime+noise)))
            image.putdata(pixels);rough.putdata(values)
            draw=ImageDraw.Draw(image)
            for i in range(90):
                x=rng.randrange(256);y=rng.randrange(256)
                draw.line((x,y,min(255,x+rng.randrange(2,11)),min(255,y+1)),fill=(125,132,124),width=1)
            for suffix,im in [('colour',image),('roughness',rough)]:
                target=folder/f'{kind}-{suffix}.png';im.save(target)
                records[str(target.relative_to(ROOT))]=hashlib.sha256(target.read_bytes()).hexdigest()
    (ROOT/'authored-wear.json').write_text(json.dumps(dict(issue=188,generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),method='Authored grease, seam grime, oxidation stains and handling chips; geometric corner dents in parts',images=records),indent=2)+'\n')
    print('CULTURE_SCAFFOLD_WEAR_OK',len(records))


if __name__=='__main__': main()
