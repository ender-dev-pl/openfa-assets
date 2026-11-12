"""Bind revalidation outputs and display working-copy native/imported overview pixels."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/evidence/rigellian-runtime-revalidation'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=ROOT/'summary.json';summary=json.loads(path.read_text())
    assert summary['models']==summary['passed']==len(summary['records'])==23
    assert summary['runner_sha256']==sha(Path(__file__).with_name('revalidate_rigellian_buildings.py'))
    assert summary['inventory_sha256']==sha(REPO/'docs/reconstruction/models/inventory.json')
    rows=[];sheets=[]
    for start in [0,12]:
        sheet=Image.new('RGB',(1280,6*345),(20,25,34));draw=ImageDraw.Draw(sheet)
        for index,record in enumerate(summary['records'][start:start+12]):
            source=(REPO/record['blend']).parent;working=REPO/record['working_copy'];folder=ROOT/source.name
            assert record['passed'] and record['source_assets_unchanged']
            assert record['verifier_sha256']==sha(REPO/'tools/blender'/record['verifier'])
            assert record['new_technical_report_sha256']==sha(folder/'technical-review.json')
            for name,digest in record['source_files'].items(): assert sha(source/name)==digest
            views={}
            for column,name in enumerate(['front-quarter','imported-glb-front-quarter']):
                image_path=working/(name+'.png');im=Image.open(image_path).convert('RGBA')
                assert im.getchannel('A').getbbox(),'Empty actual render'
                im.thumbnail((320,310));x=(index%2)*640+column*320;y=(index//2)*345
                sheet.paste(im,(x+(320-im.width)//2,y+28+(310-im.height)//2),im)
                draw.text((x+6,y+5),source.name+' '+('native' if column==0 else 'imported'),fill='white')
                views[name]=dict(path=str(image_path.relative_to(REPO)).replace('\\','/'),sha256=sha(image_path))
            rows.append(dict(id=record['id'],views=views))
        target=ROOT/f'overview-{start//12+1}.png';sheet.save(target);sheets.append(dict(path=str(target.relative_to(REPO)).replace('\\','/'),sha256=sha(target)))
    report=dict(issue=1106,reviewer_sha256=sha(Path(__file__)),summary_sha256=sha(path),
        records=rows,sheets=sheets,final_visual_acceptance=False,
        scope='Checks exact original/source-specific report hashes and nonempty working-copy overview renders. No quantitative pixel parity, exhaustive visual/state or final quality acceptance.')
    (ROOT/'overview-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RIGELLIAN_REVALIDATION_OVERVIEW_OK',len(rows),flush=True)


if __name__=='__main__': main()
