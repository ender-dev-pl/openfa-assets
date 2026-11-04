"""Decode all explicitly mapped hardpoint videos into reference-only review sheets."""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from inventory_reconstruction import publish_text
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'
OUT=REPO/'artifacts/hardpoint-reference-study'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0,str(LEGACY/'tools'))
    import fragile_vid
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    for source in read(REPO/'docs/reconstruction/models/inventory.json')['records']:
        if source['category']!='hardpoints':
            continue
        videos=[item for item in source['references'] if item['kind']=='rotation-video']
        assert len(videos)==1,source['id']
        video=videos[0]
        file=LEGACY/video['directory']/video['entry']
        assert sha(file)==video['sha256']
        output=OUT/'videos'/file.stem/video['sha256'][:12]
        if not (output/'metadata.json').is_file():
            fragile_vid.export_png(file,output,LEGACY/'FRAGILE.EXE')
        metadata=read(output/'metadata.json')
        count=metadata['head']['frame_count']
        indices=sorted({int(i*(count-1)/8) for i in range(9)})
        frames=[]
        for i in indices:
            png=output/'frames'/f'{i:03}.png'
            with Image.open(png) as image:
                assert image.mode=='P' and image.palette
                palette_hash=hashlib.sha256(bytes(image.getpalette())).hexdigest()
                size=list(image.size)
            frames.append(dict(index=i,png=str(png.relative_to(REPO)).replace('\\','/'),
                               png_sha256=sha(png),palette_sha256=palette_hash,pixel_size=size))
        record=dict(id=source['id'],name=source['name'],type_index=source['legacy_identity']['typeIndex'],
                    source_directory=video['directory'],source_entry=video['entry'],source_sha256=video['sha256'],
                    decoded_metadata_sha256=sha(output/'metadata.json'),frame_count=count,frames=frames,
                    palette='Per-frame codec palette, original 6-bit VGA values expanded to 8-bit RGB',
                    scope='Shared equipment definition; cultural variants unresolved',
                    mechanics='Inventory presentation does not establish weapon aiming or mounting transforms')
        records.append(record)
        sheet=Image.new('RGB',(1440,3*320),(20,25,34))
        draw=ImageDraw.Draw(sheet)
        for j,frame in enumerate(frames):
            x,y=j%3*480,j//3*320
            sheet.paste(tile(REPO/frame['png'],(480,290)),(x,y+24))
            draw.text((x+8,y+5),f'{record["type_index"]:02} {record["name"]} / frame {frame["index"]}',fill='white')
        sheet.save(OUT/f'{record["type_index"]:02}.png')
    assert len(records)==16 and {r['type_index'] for r in records}==set(range(16))
    manifest=dict(schema_version=1,issue=955,definitions=16,decoder_sha256=sha(LEGACY/'tools/fragile_vid.py'),
                  codec_executable_sha256=sha(LEGACY/'FRAGILE.EXE'),
                  original_pixels='Reference-only, retained in ignored artifacts; not distributed assets',hardpoints=records)
    publish_text(REPO/'docs/reconstruction/models/hardpoint-reference-index.json',json.dumps(manifest,indent=2)+'\n')
    print('HARDPOINT_REFERENCES_PREPARED',len(records),sum(len(r['frames']) for r in records),'samples',flush=True)


if __name__=='__main__':
    main()
