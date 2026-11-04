"""Check hardpoint IDs, source hashes, decoded coverage and embedded frame palettes."""
import hashlib
import json
from pathlib import Path

from PIL import Image

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    index=read(REPO/'docs/reconstruction/models/hardpoint-reference-index.json')
    inventory=read(REPO/'docs/reconstruction/models/inventory.json')['records']
    expected={row['id']:row for row in inventory if row['category']=='hardpoints'}
    actual=index['hardpoints']
    assert len(actual)==index['definitions']==len(expected)==16
    assert {row['id'] for row in actual}==set(expected)
    assert {row['type_index'] for row in actual}==set(range(16))
    assert index['decoder_sha256']==sha(LEGACY/'tools/fragile_vid.py')
    assert index['codec_executable_sha256']==sha(LEGACY/'FRAGILE.EXE')
    samples=0
    for row in actual:
        source=expected[row['id']]
        assert row['type_index']==source['legacy_identity']['typeIndex']
        assert row['name']==source['name']
        videos=[ref for ref in source['references'] if ref['kind']=='rotation-video']
        assert len(videos)==1
        video=videos[0]
        assert row['source_entry']==video['entry']
        assert row['source_directory']==video['directory']
        assert row['source_sha256']==video['sha256']==sha(LEGACY/video['directory']/video['entry'])
        first=REPO/row['frames'][0]['png']
        root=first.parent.parent
        assert row['decoded_metadata_sha256']==sha(root/'metadata.json')
        count=read(root/'metadata.json')['head']['frame_count']
        assert count==row['frame_count']
        assert [frame['index'] for frame in row['frames']]==sorted({int(i*(count-1)/8) for i in range(9)})
        # Check the complete decoded sequence exists, not only selected frames.
        assert {path.name for path in first.parent.glob('*.png')}=={f'{i:03}.png' for i in range(count)}
        for frame in row['frames']:
            file=REPO/frame['png']
            assert sha(file)==frame['png_sha256']
            with Image.open(file) as image:
                assert image.mode=='P' and image.palette
                assert list(image.size)==frame['pixel_size']
                assert hashlib.sha256(bytes(image.getpalette())).hexdigest()==frame['palette_sha256']
            samples+=1
        sheet=REPO/'artifacts/hardpoint-reference-study'/f'{row["type_index"]:02}.png'
        with Image.open(sheet) as image:
            assert image.size==(1440,960)
    assert samples==144
    print('HARDPOINT_REFERENCES_VERIFIED 16 definitions 144 samples',flush=True)


if __name__=='__main__':
    main()
