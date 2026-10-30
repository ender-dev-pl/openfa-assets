"""Verify render framing/alpha and assemble missile reference comparison sheets."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/terran'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids',default='explosive,area-explosive')
    names=parser.parse_args().ids.split(',')
    refs=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']
    for name in names:
        root=ROOT/name;meta=json.loads((root/'model.json').read_text())
        gallery=Image.new('RGB',(1536,1024),(20,25,34));draw=ImageDraw.Draw(gallery)
        hashes={}
        for i,view in enumerate(meta['views']):
            path=root/(view+'.png')
            with Image.open(path) as im:
                assert im.mode=='RGBA' and im.size==(768,768)
                assert im.getextrema()[3]==(0,255)
                x0,y0,x1,y1=im.getchannel('A').getbbox()
                assert min(x0,y0,768-x1,768-y1)>=20,'Clipped missile '+view
            gallery.paste(tile(path,(512,480)),(i%3*512,i//3*512+24))
            draw.text((i%3*512+12,i//3*512+6),view,fill='white')
            hashes[view]=hashlib.sha256(path.read_bytes()).hexdigest()
        gallery.save(root/'gallery.png')
        ref=next(r for r in refs if r['id']==meta['id'])
        sheet=Image.new('RGB',(1800,1000),(20,25,34));draw=ImageDraw.Draw(sheet)
        if ref['management_preview'] is not None:
            sheet.paste(tile(REPO/ref['management_preview']['frames'][0]['png'],(360,850)),(0,40))
            draw.text((10,10),'Legacy management preview (reference only)',fill='white')
        else:
            sheet.paste(tile(REPO/ref['surface']['frames'][9]['png'],(360,850)),(0,40))
            draw.text((10,10),'Legacy launch frame 9; no management preview',fill='white')
        for i,index in enumerate([0,3,6,9]):
            path=REPO/ref['surface']['frames'][index]['png']
            sheet.paste(tile(path,(350,350)),(380+i*350,40))
            draw.text((390+i*350,10),f'Legacy runtime frame {index}',fill='white')
        for i,view in enumerate(['front','front-quarter','rear-quarter','nozzle']):
            sheet.paste(tile(root/(view+'.png'),(350,540)),(380+i*350,440))
            draw.text((390+i*350,410),'Authored '+view,fill='white')
        sheet.save(REPO/'artifacts/missile-reference-study'/f'{name}-comparison.png')
        report=dict(issue=meta['issue'],blend_sha256=meta['blend_sha256'],view_hashes=hashes,
                    transparency=True,minimum_margin=20,final_visual_acceptance=False)
        (root/'render-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('TERRAN_MISSILE_RENDER_REVIEW_OK',name,len(hashes))
    family={'explosive,area-explosive':'explosive-family.png','virus,anti-virus':'virus-family.png','bug-hunter,meat-eater':'special-missile-family.png'}.get(','.join(names))
    if family is None:
        return
    pair=Image.new('RGB',(1000,800),(20,25,34));draw=ImageDraw.Draw(pair)
    for i,name in enumerate(names):
        pair.paste(tile(ROOT/name/'front-quarter.png',(500,760)),(i*500,35))
        draw.text((i*500+16,12),name,fill='white')
    pair.save(ROOT/family)


if __name__=='__main__': main()
