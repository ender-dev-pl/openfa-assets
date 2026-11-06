"""Index all culture/footprint construction references without importing pixels into models."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
REPO=Path(__file__).resolve().parents[2]
PREFIXES={'terran':'PB','rigellian':'RI','braccatian':'BR','mikotaj':'MK','artemian':'AR','mauna':'MN','achaean':'AC'}
TARGET=REPO/'docs/reconstruction/models/shared-construction-references.json'


def digest(path):
    data=path.read_text(encoding='utf-8-sig').encode() if path.suffix in ['.py','.cs','.json'] else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def build_index(root=REPO,legacy=None,check=False):
    legacy=legacy or root.parent/'legacy'
    sys.path.insert(0,str(legacy/'tools'))
    import fragile256 as codec
    from review_assault_fighter import tile
    catalogue=root/'content/standard/catalogues/legacy-buildings.json'
    definitions=json.loads(catalogue.read_text())['buildings'];assert len(definitions)==177
    out=root/'artifacts/shared-construction-reference-study';out.mkdir(parents=True,exist_ok=True)
    _,payload,entries=codec.read_archive(legacy/'_B/_B');archive={e.name:e for e in entries}
    mappings=[]
    for definition in definitions:
        culture=definition['factionId'].rsplit('/',1)[1]
        size=max(1,min(4,max(definition['footprintWidth'],definition['footprintHeight'])))
        mappings.append(dict(id=definition['id'],culture=culture,footprint=[definition['footprintWidth'],definition['footprintHeight']],
            family=f'{PREFIXES[culture]}S{size}',footprint_class=size))
    assert len({r['id'] for r in mappings})==177
    families=[];overview=Image.new('RGB',(1600,2100),(20,25,34));labels=ImageDraw.Draw(overview)
    for row,(culture,prefix) in enumerate(PREFIXES.items()):
        for size in range(1,5):
            key=f'{prefix}S{size}';entry=archive[key+'.256'];raw=payload[entry.offset:entry.offset+entry.length]
            folder=out/key;folder.mkdir(parents=True,exist_ok=True);source=folder/(key+'.256')
            if not check: source.write_bytes(raw)
            assert source.read_bytes()==raw
            data,frames,palette,origin=codec.read_sprites(source);assert origin==key+'.256'
            rgb=codec.palette_to_png(palette);records=[]
            sheet=Image.new('RGB',(1000,math.ceil(len(frames)/5)*180),(20,25,34));draw=ImageDraw.Draw(sheet)
            for frame in frames:
                record=dict(index=frame.index,size=[frame.width,frame.height],offset=[frame.x,frame.y])
                if frame.width and frame.height:
                    start=codec.GLOBAL_HEADER_SIZE+frame.stream_offset
                    pixels=codec.decode_sprite(data[start:start+frame.stream_length],frame.width,frame.height)
                    im=Image.frombytes('P',(frame.width,frame.height),pixels);im.putpalette(rgb);rgba=im.convert('RGBA')
                    rgba.putalpha(Image.frombytes('L',rgba.size,bytes(255 if v else 0 for v in pixels)))
                    png=folder/f'descriptor-{frame.index:02}.png'
                    if not check: rgba.save(png)
                    with Image.open(png) as actual: assert actual.convert('RGBA').tobytes()==rgba.tobytes()
                    record.update(indexed_sha256=hashlib.sha256(pixels).hexdigest(),png=str(png.relative_to(root)).replace('\\','/'),png_sha256=digest(png))
                    sheet.paste(tile(png,(200,150)),(frame.index%5*200,frame.index//5*180+25))
                else: record['empty']=True
                draw.text((frame.index%5*200+8,frame.index//5*180+6),f'{key} descriptor {frame.index}',fill='white')
                records.append(record)
            contact=folder/'descriptors.png'
            if not check: sheet.save(contact)
            assert contact.is_file()
            overview.paste(tile(contact,(400,260)),((size-1)*400,row*300+28))
            labels.text(((size-1)*400+8,row*300+7),f'{key}: {len(frames)} descriptors; reference only',fill='white')
            used=[r['id'] for r in mappings if r['family']==key]
            families.append(dict(key=key,object_kind='construction-scaffolding',culture=culture,footprint_class=size,archive_entry=key+'.256',source_sha256=hashlib.sha256(raw).hexdigest(),
                palette_rgb_sha256=hashlib.sha256(rgb).hexdigest(),descriptor_count=len(frames),descriptors=records,
                contact_sheet=str(contact.relative_to(root)).replace('\\','/'),contact_sheet_sha256=digest(contact),building_ids=used,
                interpretation='Descriptor zero is excluded from construction body progress by current runtime; exact original timing and geometry require separate review',
                descriptor_zero_visual_review=('Body-like green domed structure rather than the purple perimeter mask visible in the other reviewed families; current runtime excludes zero; original selector/composition requires investigation' if key=='ARS2' else 'Purple perimeter/ground-mask appearance in the reviewed reference contact sheet; exact legacy composition not established'),
                authored_model=None,final_visual_acceptance=False))
    if not check: overview.save(out/'overview.png')
    paths=['content/standard/catalogues/legacy-buildings.json','src/OpenFA.Assets/FrontEnd/GameplayAssets.cs',
           'src/OpenFA.Core/Presentation/LegacyConstructionSpriteFrameSelector.cs']
    return dict(issue=983,schema_version=1,text_hash_policy='UTF-8 with LF-normalized newlines; binary sources exact',
        archive_sha256=digest(legacy/'_B/_B'),generator_sha256=digest(Path(__file__)),source_sha256={p:digest(root/p) for p in paths},
        family_count=len(families),building_count=len(mappings),families=families,building_dependencies=mappings,
        scope='Current OpenFA culture/footprint loader mapping and decoded original references; not proof of original selection/timing, damage variants, authored 3D states or final acceptance')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=build_index(check=args.check)
    if args.check: assert json.loads(TARGET.read_text())==result,'Stale shared construction index'
    else: TARGET.write_text(json.dumps(result,indent=2)+'\n')
    print('SHARED_CONSTRUCTION_REFERENCES_OK',result['family_count'],'families',result['building_count'],'buildings',sum(r['descriptor_count'] for r in result['families']),'descriptors')


if __name__=='__main__': main()
