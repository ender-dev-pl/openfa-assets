"""Prepare/verify RI01 embedded-palette surface and hologram phases, reference-only."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'
OUT=REPO/'artifacts/rigellian-cpu-reference-study'
TARGET=REPO/'docs/reconstruction/models/rigellian-cpu-reference.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    sys.path.insert(0,str(LEGACY/'tools'))
    import fragile256 as codec
    import fragile_vid as video
    buildings=json.loads((REPO/'content/standard/catalogues/legacy-buildings.json').read_text())['buildings']
    building=next(r for r in buildings if r['id']=='openfa:building/legacy/040')
    assert building['legacy']['globalType']==40 and [building['footprintWidth'],building['footprintHeight']]==[3,3]
    OUT.mkdir(parents=True,exist_ok=True)
    _,payload,entries=codec.read_archive(LEGACY/'_B/_B')
    entry=next(e for e in entries if e.name=='RI01.256');raw=payload[entry.offset:entry.offset+entry.length]
    staged=OUT/'RI01.256'
    if not staged.exists() or staged.read_bytes()!=raw: staged.write_bytes(raw)
    data,frames,palette,origin=codec.read_sprites(staged)
    assert origin=='RI01.256' and len(frames)==2
    rgb=codec.palette_to_png(palette);samples=[]
    for frame in frames:
        indices=codec.decode_sprite(data[codec.GLOBAL_HEADER_SIZE+frame.stream_offset:codec.GLOBAL_HEADER_SIZE+frame.stream_offset+frame.stream_length],frame.width,frame.height)
        indexed=Image.frombytes('P',(frame.width,frame.height),indices);indexed.putpalette(rgb)
        old=Image.open(LEGACY/'_B/png/RI01'/f'{frame.index:03}.png').crop((frame.x,frame.y,frame.x+frame.width,frame.y+frame.height)).convert('RGB')
        assert old.tobytes()==indexed.convert('RGB').tobytes(),'Existing export differs from raw embedded-palette decode'
        rgba=indexed.convert('RGBA');rgba.putalpha(Image.frombytes('L',rgba.size,bytes(255 if i else 0 for i in indices)))
        target=OUT/f'surface-{frame.index:02}.png'
        if not args.check: rgba.save(target)
        assert target.is_file() and Image.open(target).convert('RGBA').tobytes()==rgba.tobytes()
        samples.append(dict(index=frame.index,role='ground/footprint layer' if frame.index==0 else 'complete surface body',
            size=[frame.width,frame.height],crop=[frame.x,frame.y,frame.width,frame.height],
            indexed_sha256=hashlib.sha256(indices).hexdigest(),png=str(target.relative_to(REPO)).replace('\\','/'),png_sha256=sha(target)))
    video_root=OUT/'hologram'
    if not (video_root/'metadata.json').exists():
        assert not args.check,'Hologram reference was not decoded'
        video.export_png(LEGACY/'_ZOOM/RI01.VID',video_root,LEGACY/'FRAGILE.EXE')
    meta=json.loads((video_root/'metadata.json').read_text());assert meta['head']['frame_count']==41
    selected=[]
    for index in [0,10,20,30,40]:
        path=video_root/'frames'/f'{index:03}.png';assert path.is_file()
        selected.append(dict(index=index,png=str(path.relative_to(REPO)).replace('\\','/'),png_sha256=sha(path)))
    result=dict(issue=969,id=building['id'],name=building['legacy']['name'],culture='rigellian',global_type=40,footprint=[3,3],
        surface_source=dict(archive='../legacy/_B/_B',archive_sha256=sha(LEGACY/'_B/_B'),entry='RI01.256',source_sha256=sha(staged),
            palette='embedded VGA, flags masked and 6-bit channels expanded',palette_rgb_sha256=hashlib.sha256(rgb).hexdigest(),transparent_index=0,frames=samples),
        catalogue_source=dict(path='../legacy/_ZOOM/RI01.VID',source_sha256=sha(LEGACY/'_ZOOM/RI01.VID'),frames=41,selected=selected,
            interpretation='Hologram/presentation phases; not established as independent spatial rotations'),
        source_sha256={name:sha(REPO/name) for name in ['content/standard/catalogues/legacy-buildings.json','content/standard/presentation/legacy-domain.json']},
        decoder_sha256={name:sha(LEGACY/name) for name in ['tools/fragile256.py','tools/fragile_vid.py','FRAGILE.EXE']},
        unresolved=['Hidden sides and underside','Exact 3D dimensions/projection','Construction and damage states','Final visual acceptance'])
    if args.check: assert json.loads(TARGET.read_text())==result,'Stale RI01 reference provenance'
    else:
        TARGET.write_text(json.dumps(result,indent=2)+'\n')
        sheet=Image.new('RGB',(1500,400),(20,25,34));draw=ImageDraw.Draw(sheet)
        images=[(OUT/'surface-01.png','Embedded-palette surface body')]+[(REPO/f['png'],f'Hologram phase {f["index"]}') for f in selected]
        for i,(path,label) in enumerate(images):
            im=Image.open(path).convert('RGBA')
            if i: im=im.crop((38,25,104,134))
            else: im=im.crop(im.getbbox())
            scale=min(230/im.width,350/im.height)
            im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
            sheet.paste(im,(i*250+(250-im.width)//2,35),im);draw.text((i*250+10,10),label,fill='white')
        sheet.save(OUT/'reference-sheet.png')
    print('RIGELLIAN_CPU_REFERENCES_OK 2 raw surface layers, 41 decoded presentation frames; footprint 3x3')


if __name__=='__main__': main()
