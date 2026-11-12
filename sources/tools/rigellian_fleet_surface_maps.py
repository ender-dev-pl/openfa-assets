"""Deterministic authored wear atlas; contains no legacy/reference pixels."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'sources/materials/rigellian-mobile-fleet'
COLOURS = ['647F78', '9AACAB', 'A86543', 'B99B43', '1F2A2B', 'FFBF68',
           '71BDD2', '15282E', '718A81', '556C68', '10191B', '829795',
           '8D563B', '8F7D43', '364548', 'C5C2A6']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(232)
    base = Image.new('RGB', (2048, 2048))
    orm = Image.new('RGB', base.size)
    glow = Image.new('RGB', base.size)
    for tile, colour in enumerate(COLOURS):
        rgb = tuple(bytes.fromhex(colour))
        image = Image.new('RGB', (512, 512)); pixels = image.load()
        for y in range(512):
            for x in range(512):
                edge = min(x, y, 511-x, 511-y)
                dirt = max(0, 1-edge/42) * .23
                noise = rng.uniform(-.028, .028)
                pixels[x, y] = tuple(max(0, min(255, round(c*(1-dirt+noise)))) for c in rgb)
        d = ImageDraw.Draw(image)
        if tile not in (5, 6, 7):
            stains=Image.new('RGB',(512,512),(255,255,255));sd=ImageDraw.Draw(stains)
            for _ in range(18):
                x,y=rng.randrange(512),rng.randrange(512)
                rx,ry=rng.randrange(8,38),rng.randrange(8,50)
                value=rng.randrange(229,248)
                sd.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(value,)*3)
            image=ImageChops.multiply(image,stains.filter(ImageFilter.GaussianBlur(14)))
            d=ImageDraw.Draw(image)
            for _ in range(75):
                x, y = rng.randrange(24, 488), rng.randrange(24, 488)
                length = rng.randrange(2, 22)
                d.line((x, y, x+length, y+rng.randrange(-3, 4)),
                       fill=tuple(min(255, int(c*.68+45)) for c in rgb), width=1)
            for _ in range(24):
                x, y = rng.randrange(512), rng.randrange(512)
                d.ellipse((x, y, x+2, y+2), fill=tuple(int(c*.62) for c in rgb))
        xy = ((tile % 4)*512, (tile//4)*512)
        base.paste(image, xy)
        # R=occlusion, G=roughness, B=metallic. Glass is opaque coated glazing.
        rough = 42 if tile == 7 else 95 if tile in (5, 6) else 114 if tile in (1,11,15) else 132
        orm.paste((255, rough, 210 if tile not in (5, 6, 7) else 55), (*xy, xy[0]+512, xy[1]+512))
        if tile in (5, 6):
            glow.paste(Image.new('RGB', (512, 512), rgb), xy)
    for name, image in [('base-colour', base), ('occlusion-roughness-metallic', orm), ('emission', glow)]:
        image.save(OUT / (name+'.png'), optimize=True)


if __name__ == '__main__':
    main()
