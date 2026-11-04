"""Decode original UI evidence; keep all original pixels in a local workspace."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--legacy-root',type=Path,required=True)
p.add_argument('--decoder',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
spec=importlib.util.spec_from_file_location('legacy_decoder',a.decoder)
dec=importlib.util.module_from_spec(spec);sys.modules[spec.name]=dec;spec.loader.exec_module(dec)
dest=a.output.resolve();dest.mkdir(parents=True,exist_ok=True)
sources=['ICONS','FE_ICONS','CICONS','SCROLL','BUTTONS','FE_BUTTO']
report={'decoder_sha256':hashlib.sha256(a.decoder.read_bytes()).hexdigest(),'sources':{}}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for name in sources:
    source=a.legacy_root/'_MS'/(name+'.256')
    dec.export_sprites(source,dest)
    meta=json.loads((dest/(name+'.json')).read_text())
    report['sources'][name]={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frames':len(meta['frames']),'palette':meta['palette']}
    count=len(meta['frames']);cols=8;w=160;h=140
    canvas=Image.new('RGBA',(cols*w,((count+cols-1)//cols)*h),(15,18,27,255));d=ImageDraw.Draw(canvas)
    for i,frame in enumerate(meta['frames']):
        im=Image.open(dest/frame['png']).convert('RGBA')
        box=im.getbbox()
        if box:im=im.crop(box)
        im.thumbnail((132,98),Image.Resampling.NEAREST)
        if max(im.size)<80:im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
        x=(i%cols)*w;y=(i//cols)*h
        canvas.alpha_composite(im,(x+(w-im.width)//2,y+8))
        d.text((x+8,y+110),f'{name}/{i:03}',font=font,fill='white')
    canvas.convert('RGB').save(dest/(name+'-contact.png'))
for name in ['BLUE','GREEN','ORANGE','RED','YELLOW','GREY']:
    source=a.legacy_root/'_MS'/(name+'.256')
    report['sources'][name]={'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
(dest/'provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print('DECODED_ORIGINAL_UI', {n:report['sources'][n]['frames'] for n in sources})
