"""Revalidate original Sci-Tek bindings/timelines and prior private decoded frames."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def container(path):
    data=path.read_bytes()
    assert data[:4]==b'Vide' and struct.unpack_from('<I',data,4)[0]==len(data)
    assert data[8:12]==b'Head' and struct.unpack_from('<I',data,12)[0]==20
    depth,width,height,declared,_,_=struct.unpack_from('<6H',data,16)
    assert depth==8
    chunks=[];offset=28;updates=0;timeline=0
    while offset<len(data):
        tag=data[offset:offset+4].decode('ascii');size=struct.unpack_from('<I',data,offset+4)[0]
        assert size>=8 and offset+size<=len(data)
        chunk=dict(tag=tag,offset=offset,size=size)
        if tag=='Fram':chunk['index']=updates;updates+=1;timeline+=1
        elif tag=='Same':assert updates and size==8;timeline+=1
        elif tag=='Stop':assert size==8 and offset+size==len(data)
        else:assert tag=='Inte'
        chunks.append(chunk);offset+=size
    assert timeline==declared and chunks and chunks[-1]['tag']=='Stop'
    return dict(head=dict(width=width,height=height,image_updates=updates,timeline_frames=timeline),chunks=chunks)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy-root',type=Path,required=True)
    parser.add_argument('--reference-cache',type=Path,required=True)
    args=parser.parse_args();legacy=args.legacy_root;cache=args.reference_cache
    path=ROOT/'sources/content/standard/presentation/legacy-domain.json';data=json.loads(path.read_text())
    assets={r['id']:r for r in data['assets']};animations={r['id']:r for r in data['animations']}
    private=ROOT/'artifacts/issue-190/scitek-review';private.mkdir(parents=True,exist_ok=True)
    records=[];sheets=[]
    for row in data['research']:
        index=int(row['id'].split('/')[-1]);folder=cache/f'ST{index:02}'
        video=assets[animations[row['informationAnimationId']]['assetId']]['source']
        preview=assets[row['catalogue']['normal']['assetId']]['source']
        original=legacy/video['directoryName']/video['fileName']
        inputs=dict(source_sha256=sha(original),executable_sha256=sha(legacy/'FRAGILE.EXE'),
          decoder_sha256=sha(legacy/'tools/fragile_vid.py'),timeline_decoder_sha256=sha(ROOT/'tools/prepare_rigellian_scitek_review.py'))
        assert json.loads((folder/'inputs.json').read_text())==inputs,'Prior decode no longer binds current original inputs'
        parsed=container(original);metadata=json.loads((folder/'metadata.json').read_text())
        assert parsed['head']==metadata['head'] and parsed['chunks']==metadata['chunks']
        frames=sorted((folder/'frames').glob('*.png'))
        assert [f.name for f in frames]==[f'{i:03}.png' for i in range(parsed['head']['image_updates'])]
        hashes=[]
        for frame in frames:
            with Image.open(frame) as im:assert list(im.size)==[parsed['head']['width'],parsed['head']['height']]
            hashes.append([frame.name,sha(frame)])
        prior=json.loads((folder/'review-inputs.json').read_text())
        assert prior['subject']==row['researchId'] and prior['preview_source']==preview and prior['information_source']==video
        assert prior['motion_contact_sha256']==sha(folder/'motion-contact.png')
        selected=prior['sampled_updates'];assert selected[0]==0 and selected[-1]==len(frames)-1
        records.append(dict(index=index,subject=row['researchId'],preview_source=preview,information_source=video,
          **inputs,**parsed['head'],same_frames=parsed['head']['timeline_frames']-len(frames),
          decoded_frames_sha256=hashlib.sha256(json.dumps(hashes,separators=(',',':')).encode()).hexdigest(),
          metadata_sha256=sha(folder/'metadata.json'),sampled_updates=selected,
          motion_contact_sha256=sha(folder/'motion-contact.png'),direct_braccatian_preview=preview.get('entryName','').startswith('BR')))
        sheets.append(folder/'motion-contact.png')
    assert len(records)==36 and not any(r['direct_braccatian_preview'] for r in records)
    # Retain only private viewing sheets; no original pixels enter tracked sources.
    for start in range(0,len(sheets),6):
        sheet=Image.new('RGB',(1800,1520),(16,20,24))
        for j,path in enumerate(sheets[start:start+6]):
            im=Image.open(path).convert('RGB').resize((600,760),Image.Resampling.NEAREST)
            sheet.paste(im,((j%3)*600,(j//3)*760))
        sheet.save(private/f'overview-{start:02}.png')
    ledger=dict(issue=190,culture='braccatian',catalogue_sha256=sha(ROOT/'sources/content/standard/presentation/legacy-domain.json'),
      audit_tool_sha256=sha(Path(__file__)),decode_provenance='Prior private original-codec decode cache from issue 185; current source/executable/decoder, container chunks, timeline, metadata and decoded frame files revalidated. Not a new decode.',
      no_direct_braccatian_previews=True,records=records,
      review_policy='Bindings and timeline integrity alone do not establish geometric relevance; visual review and functional applicability are documented separately.')
    destination=ROOT/'sources/docs/reconstruction/models/braccatian-scitek-evidence.json'
    destination.write_text(json.dumps(ledger,indent=2)+'\n')
    print('BRACCATIAN_SCITEK_INPUTS_VERIFIED',len(records),sum(r['image_updates'] for r in records),sum(r['timeline_frames'] for r in records))


if __name__=='__main__':main()
