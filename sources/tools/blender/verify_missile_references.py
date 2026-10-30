"""Independently check archive mappings, raw sprite tables and palette-only rebindings."""
import collections
import hashlib
import json
import struct
from pathlib import Path

from PIL import Image

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    index=read(REPO/'docs/reconstruction/models/missile-reference-index.json')
    inventory=read(REPO/'docs/reconstruction/models/inventory.json')['records']
    expected={r['id']:r for r in inventory if r['category']=='missiles'}
    assert index['definitions']==len(index['missiles'])==len(expected)==69
    assert {r['id'] for r in index['missiles']}==set(expected)
    assert {r['global_type'] for r in index['missiles']}==set(range(69))
    for file,digest in index['source_sha256'].items():
        assert sha((REPO/file).read_bytes())==digest,file
    gameplay=read(REPO/'content/standard/catalogues/legacy-gameplay.json')
    rules=gameplay['presentation']['surfaceScene']['backdrop']['surfacePalette']
    mutable=set(range(rules['firstPaletteIndex'],rules['firstPaletteIndex']+rules['shadeCount']))
    binding=index['palette_binding']
    assert binding['mutable_indices']==sorted(mutable) and binding['mutable_indices_used']==[]
    source=(LEGACY/binding['file']).read_bytes()
    assert sha(source)==binding['source_sha256']
    offset=source.rfind(b'PALETTE ')+32
    assert offset>=32 and len(source)-offset==768
    palette=source[offset:]
    rgb=bytes(((value&63)*255+31)//63 for value in palette)
    assert sha(palette)==binding['raw_vga_sha256'] and sha(rgb)==binding['rgb_sha256']
    archive_cache={}

    def check_sheet(sheet,expected_reference,external):
        directory=sheet['source_directory']
        assert directory==expected_reference['directory']
        assert sheet['source_entry']==expected_reference['entry']
        if directory not in archive_cache:
            archive=(LEGACY/directory/directory).read_bytes()
            table_end=struct.unpack_from('<I',archive,20)[0]
            entries={}
            for i in range(24,table_end,24):
                name=archive[i:i+16].split(b'\0',1)[0].decode('ascii')
                start,length=struct.unpack_from('<II',archive,i+16)
                entries[name]=archive[start:start+length]
            archive_cache[directory]=entries
        raw=archive_cache[directory][sheet['source_entry']]
        assert sha(raw)==sheet['source_sha256']==expected_reference['sha256']
        assert raw[:8]==b'GRAPHICS' and raw[32:40]==b'SPRITES '
        count=struct.unpack_from('<H',raw,40)[0]
        assert count==sheet['frame_count']==len(sheet['frames'])
        if external:
            assert count==14 and raw.rfind(b'PALETTE ')==-1
            colours=rgb
        else:
            start=raw.rfind(b'PALETTE ')+32
            assert start>=32 and len(raw)-start==768
            colours=bytes(((value&63)*255+31)//63 for value in raw[start:])
        assert sha(colours)==sheet['palette_rgb_sha256']
        used=set()
        signature=hashlib.sha256()
        for i,frame in enumerate(sheet['frames']):
            cw,ch,x,y,w,h,_=struct.unpack_from('<6HI',raw,48+i*16)
            assert frame['index']==i and frame['canvas']==[cw,ch] and frame['crop']==[x,y,w,h]
            file=REPO/frame['png']
            assert sha(file.read_bytes())==frame['png_sha256']
            with Image.open(file) as image:
                assert image.mode=='P' and image.size==(cw,ch)
                assert bytes(image.getpalette())==colours and image.info['transparency']==0
                pixels=image.tobytes()
                assert sha(pixels)==frame['indexed_canvas_sha256']
                cropped=image.crop((x,y,x+w,y+h)).tobytes()
            # Independent existing legacy export retains original indices even
            # when its palette is grayscale. Colour rebinding must not alter them.
            old=LEGACY/directory/'png'/Path(sheet['source_entry']).stem/f'{i:03}.png'
            with Image.open(old) as image:
                assert image.mode=='P' and image.tobytes()==pixels
            used.update(cropped)
            signature.update(struct.pack('<6H',cw,ch,x,y,w,h))
            signature.update(cropped)
        assert sorted(used)==sheet['used_indices']
        if external:
            assert not used.intersection(mutable)
        assert signature.hexdigest()==sheet['decoded_shape_sha256']
        return count

    frames=previews=0
    groups=collections.defaultdict(list)
    for missile in index['missiles']:
        record=expected[missile['id']]
        assert missile['culture']==record['culture']
        assert missile['global_type']==record['legacy_identity']['globalTypeIndex']
        reference=next(r for r in record['references'] if r['role']=='runtime.surface-flight')
        frames+=check_sheet(missile['surface'],reference,True)
        assert missile['selected_frames']==[0,3,6,7,9,12]
        preview=missile['management_preview']
        if preview:
            reference=next(r for r in record['references'] if r['directory']==preview['source_directory'] and r['entry']==preview['source_entry'])
            check_sheet(preview,reference,False)
            previews+=1
        groups[missile['surface']['decoded_shape_sha256']].append(missile['id'])
    assert frames==966 and previews==11
    assert index['unique_decoded_sequences']==len(groups)
    assert index['identical_decoded_sequences']==[ids for ids in groups.values() if len(ids)>1]
    print('MISSILE_REFERENCES_VERIFIED 69 definitions 966 frames 11 previews; no mutable palette pixels',flush=True)


if __name__=='__main__':
    main()
