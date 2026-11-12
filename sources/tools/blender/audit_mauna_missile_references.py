"""Audit Mauna missile references without embedding original pixels in deliverables."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw
REPO=Path(__file__).resolve().parents[2]
TARGET=REPO/'docs/reconstruction/models/mauna-missile-reference-audit.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
    index=REPO/'docs/reconstruction/models/missile-reference-index.json'
    catalogue=REPO/'content/standard/catalogues/legacy-gameplay.json'
    definitions={x['id']:x for x in json.loads(catalogue.read_text())['missiles']}
    cultures=REPO/'docs/reconstruction/models/cultural-architecture-index.json'
    guidance=next(x for x in json.loads(cultures.read_text())['cultures'] if x['culture']=='mauna')
    rows=[]
    for item in json.loads(index.read_text())['missiles']:
        if item['culture']!='mauna':continue
        surface=item['surface'];frames=[]
        assert surface['frame_count']==14 and item['management_preview'] is None
        for f in surface['frames']:
            p=REPO/f['png'];assert sha(p)==f['png_sha256']
            with Image.open(p) as im:
                assert im.mode=='P' and im.info['transparency']==0
                assert hashlib.sha256(bytes(im.getpalette())).hexdigest()==surface['palette_rgb_sha256']
                assert hashlib.sha256(im.tobytes()).hexdigest()==f['indexed_canvas_sha256']
                x,y,w,h=f['crop'];crop=im.crop((x,y,x+w,y+h));mask=bytes(int(v!=0) for v in crop.tobytes())
                occupancy=[sum(mask[r*w:(r+1)*w]) for r in range(h)]
                frames.append(dict(index=f['index'],crop=f['crop'],opaque_row_counts=occupancy,mask_sha256=hashlib.sha256(mask).hexdigest(),used_indices=sorted(set(crop.tobytes()))))
        entry=definitions[item['id']]
        rows.append(dict(id=item['id'],name=item['name'],source_entry=surface['source_entry'],source_sha256=surface['source_sha256'],palette_rgb_sha256=surface['palette_rgb_sha256'],effect_behavior=entry['effectBehaviorId'],legacy=entry['legacy'],flight_frame=3,frames=frames,management_preview=None,states='Flight/launch states, not a recovered turntable',acceptance='Reference audit only; no authored model acceptance'))
    assert len(rows)==10
    return dict(issue=1081,reference_index_sha256=sha(index),catalogue_sha256=sha(catalogue),cultural_index_sha256=sha(cultures),cultural_guidance=guidance,definitions=rows)
def comparison(report):
    # Original pixels remain in ignored analysis artifacts only.
    import sys
    sys.path.insert(0,str(Path(__file__).parent))
    from review_assault_fighter import tile
    index=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())
    sheet=Image.new('RGB',(1600,900),(20,24,30));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(report['definitions']):
        item=next(x for x in index['missiles'] if x['id']==row['id']);frame=item['surface']['frames'][3]
        sheet.paste(tile(REPO/frame['png'],(310,390)),((i%5)*320,(i//5)*450+30))
        draw.text(((i%5)*320+8,(i//5)*450+8),row['name'],fill='white')
    folder=REPO/'artifacts/issue-1081-mauna-reference';folder.mkdir(parents=True,exist_ok=True);sheet.save(folder/'flight-comparison.png')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();result=audit()
    if args.check:assert json.loads(TARGET.read_text())==result,'Stale Mauna audit'
    else:TARGET.write_text(json.dumps(result,indent=2)+'\n');comparison(result)
    print('MAUNA_MISSILE_REFERENCE_AUDIT_OK',len(result['definitions']),'definitions',sum(len(x['frames']) for x in result['definitions']),'frames')
if __name__=='__main__':main()
