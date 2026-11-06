"""Check render alpha/framing and assemble reference-only comparison evidence."""
import hashlib
import json
from pathlib import Path

from PIL import Image,ImageDraw

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'
OUT=REPO/'artifacts/ship-reference-study'


def tile(path,size):
    image=Image.open(path).convert('RGBA')
    if image.getextrema()[3]==(255,255):
        box=Image.eval(image.convert('RGB').convert('L'),lambda value: 255 if value>8 else 0).getbbox()
    else:
        box=image.getbbox()
    image=image.crop(box)
    factor=min(size[0]/image.width,size[1]/image.height)
    image=image.resize((round(image.width*factor),round(image.height*factor)),
                       Image.Resampling.NEAREST if factor>1 else Image.Resampling.LANCZOS)
    result=Image.new('RGBA',size,(20,25,34,255))
    result.alpha_composite(image,((size[0]-image.width)//2,(size[1]-image.height)//2))
    return result.convert('RGB')


def main():
    manifest=json.loads((ROOT/'model.json').read_text())
    directions=json.loads((ROOT/'directions.json').read_text())
    assert directions['blend_sha256']==manifest['blend_sha256'],'Directional images belong to a different model revision'
    files=[ROOT/(view+'.png') for view in manifest['views']]
    files += [ROOT/'directions'/f'{i:02}.png' for i in range(32)]
    for path in files:
        with Image.open(path) as image:
            assert image.size==(768,768)
            assert image.mode=='RGBA' and image.getextrema()[3]==(0,255),path
            box=image.getbbox()
            assert box and min(box[0],box[1],768-box[2],768-box[3])>=20,path
    sheet=Image.new('RGB',(1600,960),(20,25,34))
    draw=ImageDraw.Draw(sheet)
    index=json.loads((REPO/'docs/reconstruction/models/ship-reference-index.json').read_text())
    ship=next(row for row in index['ships'] if row['id']=='openfa:assault-fighter')
    for i,frame in enumerate(ship['videos'][0]['frames'][:4]):
        sheet.paste(tile(REPO/frame['png'],(400,280)),(i*400,30))
        draw.text((i*400+10,8),f'Legacy PS00.VID frame {frame["index"]} - reference only',fill='white')
    for i,view in enumerate(['front-quarter','rear-quarter','top','rear']):
        sheet.paste(tile(ROOT/(view+'.png'),(400,280)),(i*400,350))
        draw.text((i*400+10,328),f'Authored revision {manifest["revision"]} / {view}',fill='white')
    for i,view in enumerate(['front-quarter','rear-quarter','top','rear']):
        sheet.paste(tile(OUT/'fighter-revision-1'/(view+'.png'),(400,280)),(i*400,675))
        draw.text((i*400+10,648),f'Initial iteration / {view}',fill='white')
    sheet.save(OUT/'fighter-comparison.png')
    # Authored-only gallery can be distributed with the model.
    gallery=Image.new('RGB',(1536,1024),(20,25,34))
    draw=ImageDraw.Draw(gallery)
    for i,view in enumerate(manifest['views']):
        x=(i%3)*512
        y=(i//3)*512
        gallery.paste(tile(ROOT/(view+'.png'),(512,480)),(x,y+24))
        draw.text((x+12,y+6),view,fill='white')
    gallery.save(ROOT/'gallery.png')
    report=dict(issue=953,blend_sha256=manifest['blend_sha256'],render_count=len(files),
                alpha='transparent with opaque geometry',framing='at least 20 pixel margin in every render',
                sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files})
    (OUT/'fighter-render-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ASSAULT_FIGHTER_RENDER_CHECK_OK',len(files),flush=True)


if __name__=='__main__':
    main()
