"""Build an authored-only culture missile sheet from the real inventory ledger."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--culture',default='terran');args=parser.parse_args()
    inventory_path=REPO/'docs/reconstruction/models/inventory.json';inventory=json.loads(inventory_path.read_text())
    records=[r for r in inventory['records'] if r['category']=='missiles' and r['culture']==args.culture]
    assert records,'Unknown culture'
    width,height,columns=320,440,5
    sheet=Image.new('RGB',(width*columns,50+height*math.ceil(len(records)/columns)),(20,25,34));draw=ImageDraw.Draw(sheet)
    draw.text((16,10),args.culture.upper()+' MISSILE STUDIES - source coverage; final artistic/integration acceptance open',fill='white')
    entries=[]
    for i,record in enumerate(records):
        x=i%columns*width;y=50+i//columns*height
        studies=[s for s in record['available_studies'] if s['present']]
        draw.text((x+12,y+6),record['name'],fill='white')
        if not studies:
            draw.text((x+12,y+40),'No authored source registered',fill=(255,160,100))
            entries.append(dict(id=record['id'],present=False));continue
        study=studies[-1];root=(REPO/study['blend']).parent;image=root/'front-quarter.png'
        meta=json.loads((root/'model.json').read_text())
        assert sha(REPO/study['blend'])==study['sha256']==meta['blend_sha256']
        sheet.paste(tile(image,(width,height-55)),(x,y+26))
        interpretation='interpretation' in study['stage']
        label='Low-resolution interpretation' if interpretation else 'Management-reference study'
        draw.text((x+12,y+height-20),label,fill=(255,180,110) if interpretation else (175,195,210))
        entries.append(dict(id=record['id'],present=True,stage=study['stage'],blend=study['blend'],
            blend_sha256=study['sha256'],image=str(image.relative_to(REPO)).replace('\\','/'),image_sha256=sha(image),final_visual_acceptance=False))
    output=REPO/'docs/assets/reconstruction/missiles'/args.culture;output.mkdir(parents=True,exist_ok=True)
    sheet.save(output/'catalogue-studies.png')
    report=dict(issue=968,culture=args.culture,definitions=len(records),authored_sources=sum(e['present'] for e in entries),
        inventory_sha256=sha(inventory_path),sheet_sha256=sha(output/'catalogue-studies.png'),entries=entries,
        note='Independent source coverage only; neither per-model artistic acceptance nor integration is implied')
    (output/'catalogue-studies.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MISSILE_CULTURE_SHEET_OK',args.culture,report['authored_sources'],'of',len(records))


if __name__=='__main__': main()
