"""Validate transparent render sets and assemble authored/reference review sheets."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/ships/terran'


def main():
    references=json.loads((REPO/'docs/reconstruction/models/ship-reference-index.json').read_text())['ships']
    for name in ['combat-eagle','scoutship']:
        root=ROOT/name
        metadata=json.loads((root/'model.json').read_text())
        directions=json.loads((root/'directions.json').read_text())
        assert directions['blend_sha256']==metadata['blend_sha256']
        paths=[root/(view+'.png') for view in metadata['views']]
        paths += [root/'directions'/f'{i:02}.png' for i in range(32)]
        for path in paths:
            with Image.open(path) as image:
                assert image.mode=='RGBA' and image.size==(768,768)
                assert image.getextrema()[3]==(0,255),path
                box=image.getbbox()
                assert box and min(box[0],box[1],768-box[2],768-box[3])>=20,path
        gallery=Image.new('RGB',(1536,1024),(20,25,34))
        draw=ImageDraw.Draw(gallery)
        for i,view in enumerate(metadata['views']):
            x,y=i%3*512,i//3*512
            gallery.paste(tile(root/(view+'.png'),(512,480)),(x,y+24))
            draw.text((x+12,y+6),view,fill='white')
        gallery.save(root/'gallery.png')
        sheet=Image.new('RGB',(1600,650),(20,25,34))
        draw=ImageDraw.Draw(sheet)
        reference=next(record for record in references if record['id']==metadata['id'])
        for i,frame in enumerate(reference['videos'][0]['frames'][:4]):
            sheet.paste(tile(REPO/frame['png'],(400,280)),(i*400,24))
            draw.text((i*400+10,6),f'Legacy {metadata["reference_video"]} frame {frame["index"]}',fill='white')
        for i,view in enumerate(['front-quarter','rear-quarter','top','rear']):
            sheet.paste(tile(root/(view+'.png'),(400,280)),(i*400,350))
            draw.text((i*400+10,328),f'Authored revision {metadata["revision"]} / {view}',fill='white')
        sheet.save(REPO/'artifacts/ship-reference-study'/f'{name}-comparison.png')
        report=dict(issue=954,blend_sha256=metadata['blend_sha256'],image_count=38,
                    transparent=True,minimum_margin=20,
                    hashes={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
        (root/'render-review.json').write_text(json.dumps(report,indent=2)+'\n')
        print('LIGHT_SHIP_RENDER_REVIEW_OK',name,len(paths),flush=True)


if __name__=='__main__':
    main()
