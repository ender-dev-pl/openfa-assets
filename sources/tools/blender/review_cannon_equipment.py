"""Validate cannon render framing/alpha and create reference-only comparison evidence."""
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
    references=json.loads((REPO/'docs/reconstruction/models/hardpoint-reference-index.json').read_text())['hardpoints']
    for name in ['photon-cannon','plasma-cannon']:
        root=ROOT/name
        metadata=json.loads((root/'model.json').read_text())
        gallery=Image.new('RGB',(1536,1536),(20,25,34))
        draw=ImageDraw.Draw(gallery)
        hashes={}
        for i,view in enumerate(metadata['views']):
            path=root/(view+'.png')
            with Image.open(path) as image:
                assert image.size==(768,768) and image.mode=='RGBA'
                assert image.getextrema()[3]==(0,255)
                box=image.getbbox()
                assert box and min(box[0],box[1],768-box[2],768-box[3])>=20,path
            hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
            x,y=i%3*512,i//3*512
            gallery.paste(tile(path,(512,480)),(x,y+24))
            draw.text((x+10,y+6),view,fill='white')
        gallery.save(root/'gallery.png')
        ref=next(row for row in references if row['id']==metadata['id'])
        sheet=Image.new('RGB',(1600,650),(20,25,34))
        draw=ImageDraw.Draw(sheet)
        for i,frame in enumerate(ref['frames'][:4]):
            sheet.paste(tile(REPO/frame['png'],(400,290)),(i*400,24))
            draw.text((i*400+8,6),f'Legacy {ref["source_entry"]} frame {frame["index"]}',fill='white')
        for i,view in enumerate(['front-quarter','rear-quarter','top','side']):
            sheet.paste(tile(root/(view+'.png'),(400,290)),(i*400,350))
            draw.text((i*400+8,326),f'Authored / {view}',fill='white')
        sheet.save(REPO/'artifacts/hardpoint-reference-study'/f'{name}-comparison.png')
        (root/'render-review.json').write_text(json.dumps(dict(issue=957,blend_sha256=metadata['blend_sha256'],
            render_count=len(hashes),transparent=True,minimum_margin_pixels=20,png_sha256=hashes),indent=2)+'\n')
        print('CANNON_RENDER_REVIEW_OK',name,len(hashes),flush=True)


if __name__=='__main__':
    main()
