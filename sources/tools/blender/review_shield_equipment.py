"""Review transparent shield renders and assemble per-variant comparison galleries."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/hardpoints'


def main():
    refs=json.loads((REPO/'docs/reconstruction/models/hardpoint-reference-index.json').read_text())['hardpoints']
    family=Image.new('RGB',(2000,820),(20,25,34))
    draw_family=ImageDraw.Draw(family)
    for column,tier in enumerate([10,20,30,40,50]):
        root=ROOT/f'shield-x{tier}'
        metadata=json.loads((root/'model.json').read_text())
        gallery=Image.new('RGB',(1536,1024),(20,25,34))
        draw=ImageDraw.Draw(gallery)
        hashes={}
        for i,view in enumerate(metadata['views']):
            path=root/(view+'.png')
            with Image.open(path) as image:
                assert image.mode=='RGBA' and image.size==(768,768)
                assert image.getextrema()[3]==(0,255)
                box=image.getbbox()
                assert box and min(box[0],box[1],768-box[2],768-box[3])>=20,path
            hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            x,y=i%3*512,i//3*512
            gallery.paste(tile(path,(512,480)),(x,y+24))
            draw.text((x+10,y+6),f'Shield x{tier} / {view}',fill='white')
        gallery.save(root/'gallery.png')
        family.paste(tile(root/'front-quarter.png',(400,380)),(column*400,28))
        family.paste(tile(root/'front.png',(400,380)),(column*400,430))
        draw_family.text((column*400+8,6),f'Shield x{tier}',fill='white')
        sheet=Image.new('RGB',(1600,650),(20,25,34))
        draw=ImageDraw.Draw(sheet)
        ref=next(ref for ref in refs if ref['id']==metadata['id'])
        for i,frame in enumerate(ref['frames'][:4]):
            sheet.paste(tile(REPO/frame['png'],(400,290)),(i*400,24))
            draw.text((i*400+8,6),f'Legacy {ref["source_entry"]} / frame {frame["index"]}',fill='white')
        for i,view in enumerate(['front-quarter','rear-quarter','side','front']):
            sheet.paste(tile(root/(view+'.png'),(400,290)),(i*400,350))
            draw.text((i*400+8,326),f'Authored / {view}',fill='white')
        sheet.save(REPO/'artifacts/hardpoint-reference-study'/f'shield-x{tier}-comparison.png')
        report=dict(issue=956,blend_sha256=metadata['blend_sha256'],render_count=6,
                    transparent=True,minimum_margin_pixels=20,png_sha256=hashes)
        (root/'render-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('SHIELD_RENDER_REVIEW_OK',tier,flush=True)
    family.save(ROOT/'shield-family.png')


if __name__=='__main__':
    main()
