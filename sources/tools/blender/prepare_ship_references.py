"""Prepare reference-only, correctly paletted ship sheets without distributing legacy pixels."""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image,ImageDraw


REPO=Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_on_tile(file,frame=None):
    with Image.open(file) as source:
        image=source.convert('RGBA')
    if frame:
        image=image.crop((frame['x'],frame['y'],frame['x']+frame['width'],frame['y']+frame['height']))
    pixels=image.load()
    for y in range(image.height):
        for x in range(image.width):
            if pixels[x,y][:3]==(255,0,255):
                pixels[x,y]=(0,0,0,0)
    factor=min(284/max(1,image.width),200/max(1,image.height))
    image=image.resize((max(1,round(image.width*factor)),max(1,round(image.height*factor))),Image.Resampling.NEAREST)
    tile=Image.new('RGBA',(320,224),(14,20,28,255))
    tile.alpha_composite(image,((320-image.width)//2,(224-image.height)//2))
    return tile.convert('RGB')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root',type=Path,default=REPO.parent/'legacy')
    parser.add_argument('--decode-videos',action='store_true',help='Requires legacy Python/Pillow/Unicorn runtime')
    parser.add_argument('--output',type=Path,default=REPO/'artifacts/ship-reference-study/references')
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    inventory=read(REPO/'docs/reconstruction/models/inventory.json')
    gameplay=read(REPO/'content/standard/catalogues/legacy-gameplay.json')
    rules=gameplay['presentation']['shipAnimation']
    records=[]
    for ship in inventory['records']:
        if ship['category']!='ships':
            continue
        variant=ship['runtime_variants']['surface']
        source=next(candidate for candidate in variant['ordered_candidates'] if candidate['entry']==variant['selected_first_available'])
        root=args.legacy_root/'_S/png'
        metadata_path=root/(Path(source['entry']).stem+'.json')
        metadata=read(metadata_path)
        assert metadata['palette']['embedded'],ship['id']
        count=len(metadata['frames'])
        # 32-entry sheets follow runtime heading selection; 1/2-frame sheets are fixed states.
        selected=[0,8,16,24] if count==32 else list(range(count))
        mode='directional-heading-samples' if count==32 else 'fixed-state-samples; not four spatial views'
        frames=[]
        for index in selected:
            frame=metadata['frames'][index]
            file=root/frame['png']
            assert file.is_file()
            frames.append(dict(index=index,png=frame['png'],png_sha256=sha(file),
                pixel_width=frame['width'],pixel_height=frame['height']))
        record=dict(id=ship['id'],global_type=ship['legacy_identity']['globalTypeIndex'],name=ship['name'],
            culture=ship['culture'],source_entry=source['entry'],source_sha256=source['sha256'],
            decoded_metadata_sha256=sha(metadata_path),frame_count=count,palette='embedded original VGA palette',
            selection_mode=mode,frames=frames,
            runtime_even_heading_only=ship['id'] in rules['evenSurfaceFrameShipIds'],
            runtime_fixed_scale=ship['id'] in rules['fixedScaleShipIds'],
            videos=[],inferences_not_resolved=['Hidden hull surfaces and exact dimensions',
                'Three-dimensional hardpoint/socket transforms','Materials and mechanical detail below source pixel resolution'])
        videos=[reference for reference in ship['references'] if reference.get('kind')=='rotation-video']
        for reference in videos:
            file=args.legacy_root/reference['directory']/reference['entry']
            assert file.is_file() and sha(file)==reference['sha256']
            output=args.output/'videos'/Path(reference['entry']).stem/reference['sha256'][:12]
            if args.decode_videos and not (output/'metadata.json').exists():
                sys.path.insert(0,str(args.legacy_root/'tools'))
                import fragile_vid
                fragile_vid.export_png(file,output,args.legacy_root/'FRAGILE.EXE')
            video=dict(source_directory=reference['directory'],source_entry=reference['entry'],source_sha256=reference['sha256'],
                decoded=(output/'metadata.json').is_file())
            if video['decoded']:
                decoded=read(output/'metadata.json')
                total=decoded['head']['frame_count']
                indices=sorted({0,total//4,total//2,total*3//4,total-1})
                video.update(frame_count=total,frames=[dict(index=i,png=str((output/'frames'/f'{i:03}.png').relative_to(REPO)).replace('\\','/'),
                    png_sha256=sha(output/'frames'/f'{i:03}.png')) for i in indices])
            record['videos'].append(video)
        records.append(record)
    assert len(records)==41 and {record['global_type'] for record in records}==set(range(41))
    for culture in dict.fromkeys(record['culture'] for record in records):
        subset=[record for record in records if record['culture']==culture]
        for start in range(0,len(subset),6):
            group=subset[start:start+6]
            sheet=Image.new('RGB',(1280,len(group)*256),(14,20,28))
            draw=ImageDraw.Draw(sheet)
            for row,record in enumerate(group):
                root=args.legacy_root/'_S/png'
                metadata=read(root/(Path(record['source_entry']).stem+'.json'))
                for column,frame in enumerate(record['frames']):
                    sheet.paste(image_on_tile(root/frame['png'],metadata['frames'][frame['index']]),(column*320,row*256+24))
                    draw.text((column*320+6,row*256+238),f'frame {frame["index"]} | {frame["pixel_width"]}x{frame["pixel_height"]} pixels',fill=(170,190,205))
                draw.text((8,row*256+4),f'{record["global_type"]:02} {record["name"]} | {record["source_entry"]} | {record["selection_mode"]}',fill=(230,235,240))
            sheet.save(args.output/f'{culture}-{start:02}.png')
    # Large rotation frames have their own sheets, separate from tiny surface sprites.
    for record in records:
        for video in record['videos']:
            if not video['decoded']:
                continue
            sheet=Image.new('RGB',(1600,256),(14,20,28))
            draw=ImageDraw.Draw(sheet)
            for column,frame in enumerate(video['frames']):
                sheet.paste(image_on_tile(REPO/frame['png']),(column*320,24))
                draw.text((column*320+6,4),f'{record["name"]} | VID frame {frame["index"]}',fill=(230,235,240))
            sheet.save(args.output/f'rotation-{record["global_type"]:02}.png')
    index=dict(schema_version=1,issue=952,definition_count=41,
        cultures=dict(collections.Counter(record['culture'] for record in records)),
        reference_images='Original pixels remain only in ignored artifacts and the legacy installation.',
        ship_animation_rules=rules,ships=records)
    (REPO/'docs/reconstruction/models/ship-reference-index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    print('SHIP_REFERENCE_PREPARATION_OK',len(records),'ships',sum(len(record['frames']) for record in records),'surface samples',
        sum(video['decoded'] for record in records for video in record['videos']),'decoded rotations',flush=True)


if __name__=='__main__':
    main()
