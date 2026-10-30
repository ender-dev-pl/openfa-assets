"""Bind original missile indices to the renderer's base palette and prepare all cultures."""
import collections
import hashlib
import json
import struct
import sys
from pathlib import Path

from PIL import Image,ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parent))
from inventory_reconstruction import publish_text
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'
OUT=REPO/'artifacts/missile-reference-study'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sys.path.insert(0,str(LEGACY/'tools'))
    import fragile256 as codec
    OUT.mkdir(parents=True,exist_ok=True)
    gameplay=read(REPO/'content/standard/catalogues/legacy-gameplay.json')
    inventory=read(REPO/'docs/reconstruction/models/inventory.json')
    buttons=next(item for item in gameplay['presentation']['legacyDemoSprites'] if item['id']=='buttons')
    assert buttons['directoryName']=='_MS' and buttons['entryName']=='BUTTONS.256' and buttons['archiveName'] is None
    palette_file=LEGACY/buttons['directoryName']/buttons['entryName']
    _,_,palette,palette_source=codec.read_sprites(palette_file)
    assert palette_source==palette_file.name
    png_palette=codec.palette_to_png(palette)
    palette_rules=gameplay['presentation']['surfaceScene']['backdrop']['surfacePalette']
    mutable=set(range(palette_rules['firstPaletteIndex'],palette_rules['firstPaletteIndex']+palette_rules['shadeCount']))
    archive_cache={}

    def decode(reference,external=False):
        directory=reference['directory']
        if directory not in archive_cache:
            _,archive,entries=codec.read_archive(LEGACY/directory/directory)
            archive_cache[directory]={entry.name:archive[entry.offset:entry.offset+entry.length] for entry in entries}
        payload=archive_cache[directory][reference['entry']]
        assert sha(payload)==reference['sha256']
        staging=OUT/'source'/directory
        staging.mkdir(parents=True,exist_ok=True)
        source=staging/reference['entry']
        if not source.exists() or source.read_bytes()!=payload:
            source.write_bytes(payload)
        data,frames,own_palette,origin=codec.read_sprites(source)
        embedded=codec.find_palette(data,48+len(frames)*16)[1]
        if external:
            assert embedded is None
            colours=png_palette
        else:
            assert embedded is not None and origin==source.name
            colours=codec.palette_to_png(own_palette)
        output=OUT/'decoded'/directory/source.stem/reference['sha256'][:12]
        output.mkdir(parents=True,exist_ok=True)
        result=[]
        all_indices=set()
        signature=hashlib.sha256()
        for frame in frames:
            start=codec.GLOBAL_HEADER_SIZE+frame.stream_offset
            cropped=codec.decode_sprite(data[start:start+frame.stream_length],frame.width,frame.height) if frame.width and frame.height else b''
            all_indices.update(cropped)
            signature.update(struct.pack('<6H',frame.canvas_width,frame.canvas_height,frame.x,frame.y,frame.width,frame.height))
            signature.update(cropped)
            canvas=bytearray(frame.canvas_width*frame.canvas_height)
            for row in range(frame.height):
                offset=(frame.y+row)*frame.canvas_width+frame.x
                canvas[offset:offset+frame.width]=cropped[row*frame.width:(row+1)*frame.width]
            image=Image.frombytes('P',(frame.canvas_width,frame.canvas_height),bytes(canvas))
            image.putpalette(colours,rawmode='RGB')
            file=output/f'{frame.index:03}.png'
            image.save(file,bits=8,transparency=0)
            result.append(dict(index=frame.index,png=str(file.relative_to(REPO)).replace('\\','/'),
                               png_sha256=sha(file.read_bytes()),indexed_canvas_sha256=sha(bytes(canvas)),
                               crop=[frame.x,frame.y,frame.width,frame.height],canvas=[frame.canvas_width,frame.canvas_height]))
        return dict(source_directory=directory,source_entry=reference['entry'],source_sha256=reference['sha256'],
                    palette_source='BUTTONS.256 base surface palette' if external else 'embedded',
                    palette_rgb_sha256=sha(colours),frame_count=len(frames),frames=result,
                    used_indices=sorted(all_indices),decoded_shape_sha256=signature.hexdigest())

    records=[]
    for record in inventory['records']:
        if record['category']!='missiles':
            continue
        surface_ref=next(ref for ref in record['references'] if ref['role']=='runtime.surface-flight')
        surface=decode(surface_ref,True)
        assert surface['frame_count']==14
        assert not mutable.intersection(surface['used_indices']),record['id']
        previews={ref['entry']:ref for ref in record['references'] if ref['directory']=='_MA' and ref['kind']=='sprite-sheet' and ref.get('present')}
        preview=decode(next(iter(previews.values()))) if previews else None
        records.append(dict(id=record['id'],name=record['name'],culture=record['culture'],
            global_type=record['legacy_identity']['globalTypeIndex'],surface=surface,management_preview=preview,
            selected_frames=[0,3,6,7,9,12],frame_semantics='Indexed flight/launch states; not turntable views',
            unresolved=['Hidden geometry and dimensions','Body versus exhaust/effect separation','Launch orientation and mount registration']))
    assert len(records)==69 and {r['global_type'] for r in records}==set(range(69))
    for culture in dict.fromkeys(r['culture'] for r in records):
        subset=[r for r in records if r['culture']==culture]
        for start in range(0,len(subset),5):
            group=subset[start:start+5]
            sheet=Image.new('RGB',(1792,len(group)*256),(20,25,34))
            draw=ImageDraw.Draw(sheet)
            for row,r in enumerate(group):
                draw.text((8,row*256+5),f'{r["global_type"]:02} {r["name"]} / {r["surface"]["source_entry"]}',fill='white')
                if r['management_preview']:
                    sheet.paste(tile(REPO/r['management_preview']['frames'][0]['png'],(256,220)),(0,row*256+25))
                else:
                    draw.text((8,row*256+110),'No bound management preview',fill=(180,190,200))
                for column,index in enumerate(r['selected_frames'],1):
                    frame=r['surface']['frames'][index]
                    sheet.paste(tile(REPO/frame['png'],(256,220)),(column*256,row*256+25))
                    draw.text((column*256+6,row*256+240),f'frame {index} / {frame["crop"][2]}x{frame["crop"][3]} pixels',fill=(180,190,200))
            sheet.save(OUT/f'{culture}-{start:02}.png')
    evidence_files=['src/OpenFA.Assets/FrontEnd/GameplayAssets.cs',
        'src/OpenFA.Assets/FrontEnd/LegacySurfaceObjectRenderer.cs',
        'src/OpenFA.Assets/FrontEnd/LegacySurfaceObjectRenderer.Part1.cs',
        'src/OpenFA.Assets/FrontEnd/LegacyAsteroidBackdropRenderer.Part1.cs',
        'content/standard/catalogues/legacy-gameplay.json','docs/legacy/missile-mechanics.md']
    groups=collections.defaultdict(list)
    for r in records:
        groups[r['surface']['decoded_shape_sha256']].append(r['id'])
    manifest=dict(schema_version=1,issue=958,definitions=69,cultures=dict(collections.Counter(r['culture'] for r in records)),
        palette_binding=dict(file='_MS/BUTTONS.256',source_sha256=sha(palette_file.read_bytes()),
            raw_vga_sha256=sha(palette),rgb_sha256=sha(png_palette),mutable_indices=sorted(mutable),
            mutable_indices_used=[],transparent_index=0,
            proof='All 966 decoded runtime frames avoid the asteroid-varying range; base colours therefore equal active surface colours for these pixels'),
        source_sha256={file:sha((REPO/file).read_bytes()) for file in evidence_files},
        identical_decoded_sequences=[ids for ids in groups.values() if len(ids)>1],
        unique_decoded_sequences=len(groups),unique_mesh_count='not established by 2D sequence equality',missiles=records)
    publish_text(REPO/'docs/reconstruction/models/missile-reference-index.json',json.dumps(manifest,indent=2)+'\n')
    print('MISSILE_REFERENCES_PREPARED',len(records),'definitions',sum(r['surface']['frame_count'] for r in records),
          'frames',sum(r['management_preview'] is not None for r in records),'management previews',len(groups),'distinct sequences',flush=True)


if __name__=='__main__':
    main()
