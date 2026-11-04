"""Validate published UI payload against source-bound render/coverage evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--media',required=True,type=Path)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--renders',type=Path,help='Optional independent raw-render directory')
    a=p.parse_args();media=a.media.resolve();source=a.source.resolve()
    report=json.loads((media/'verification.json').read_text())
    catalog=json.loads((media/'catalog.json').read_text())
    mapping=json.loads((media/'frame-map.json').read_text())['frames']
    assert report['icons']==111 and report['icon_pngs']==1110 and report['button_pngs']==1110
    assert len(catalog['items'])==111 and len(mapping)==147
    assert len({(r['source'],r['frame']) for r in mapping})==147
    assert {i['frame'] for i in catalog['items'] if i['family']=='gameplay'}==set(range(75))
    assert {i['frame'] for i in catalog['items'] if i['family']=='controls'}==set(range(4))
    assert {i['frame'] for i in catalog['items'] if i['family']=='scroll'}==set(range(14))
    assert {i['frame'] for i in catalog['items'] if i['family']=='frontend'}==set(range(17))
    for name,digest in report['source_hashes'].items():assert sha(source/name)==digest, 'Source changed: '+name
    assert sha(source/'assemble_icon_set.py')==report['packager_sha256'],'Packager changed'
    for name,digest in report['source_artifacts'].items():assert sha(source/name)==digest,'Source artifact changed: '+name
    assert len(report['proofs'])==121
    reload=report['saved_scene_reload']
    assert reload['source_sha256']==report['source_artifacts']['legacy-ui-full.blend']
    assert reload['silhouette_iou']>=.995 and len(reload['visible_objects'])==6
    for name,proof in report['proofs'].items():
        assert proof['source_objects']==proof['imported_objects']>0,name
        assert proof['silhouette_iou']>=.995,name
    assert {p.relative_to(media).as_posix() for p in media.rglob('*.png')}==set(report['files']), 'Unexpected or missing PNGs'
    for name,digest in report['files'].items():assert sha(media/name)==digest,'Payload changed: '+name
    if a.renders:
        assert len(report['render_hashes'])==242
        for name,digest in report['render_hashes'].items():assert sha(a.renders/name)==digest,'Raw render changed: '+name
    for item in catalog['items']:
        for kind in ['icons','buttons']:
            for key,path in item['files'][kind].items():
                im=Image.open(media/path)
                size=item['icon_size' if kind=='icons' else 'button_size']
                if key.startswith('hires'):size=[n*8 for n in size]
                assert im.mode=='RGBA' and list(im.size)==size,(item['id'],path)
                lo,hi=im.getchannel('A').getextrema()
                assert lo==0 and hi>0,(item['id'],'Missing transparency or visible content')
        normal=Image.open(media/item['files']['buttons']['native/normal'])
        pressed=Image.open(media/item['files']['buttons']['native/pressed'])
        disabled=Image.open(media/item['files']['buttons']['native/disabled'])
        assert normal.tobytes()!=pressed.tobytes()!=disabled.tobytes(),item['id']
    print('PUBLISHED_ICON_SET_VERIFIED',len(catalog['items']),'icons',len(report['files']),'PNGs',len(mapping),'frame mappings')


if __name__=='__main__':main()
