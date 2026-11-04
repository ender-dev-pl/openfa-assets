"""Validate source binding, layer contracts, state coverage and optional scene reload."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image,ImageChops


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True,type=Path);p.add_argument('--media',required=True,type=Path);p.add_argument('--reload',type=Path)
    a=p.parse_args();media=a.media;source=a.source
    report=json.loads((media/'verification.json').read_text());catalog=json.loads((media/'catalog.json').read_text())
    assert len(catalog['items'])==290 and len(report['files'])==585
    for name,digest in report['source_hashes'].items():assert sha(source/name)==digest,'Source changed: '+name
    assert sha(source/'package_menu.py')==report['packager_sha256'],'Packager changed'
    for name,digest in report['artifacts'].items():assert sha(source/name)==digest,'Scene changed: '+name
    assert set(report['files'])=={p.relative_to(media).as_posix() for p in media.rglob('*.png')}
    for name,digest in report['files'].items():assert sha(media/name)==digest,'Payload changed: '+name
    assert len(report['proof'])==10
    for name,proof in report['proof'].items():assert proof['silhouette_iou']>=.995,name
    for theme in catalog['themes']:
        seen=[]
        for state in catalog['states']:
            seen.append(Image.open(media/'native'/f'sphere-{theme}-{state}.png').tobytes())
            for prefix in ['sphere','emission','glow','dome-canvas','rail','rail-glow','row','row-glow']:
                assert (media/'native'/f'{prefix}-{theme}-{state}.png').is_file()
        assert len(set(seen))==6,'Indistinguishable illumination states: '+theme
        for i in range(8):assert (media/'native'/f'pulse-{theme}-{i:02}.png').is_file()
        assert Image.open(media/'native'/f'glow-{theme}-off.png').getchannel('A').getextrema()==(0,0)
    for item in catalog['items']:
        for resolution,path in item['files'].items():
            im=Image.open(media/path);size=item['native_size' if resolution=='native' else 'hires_size']
            assert im.mode=='RGBA' and list(im.size)==size,path
            if item['role'] not in ['independent-layer']:assert im.getchannel('A').getextrema()[0]==0,path
    if a.reload:
        reload=json.loads((a.reload/'reload.json').read_text())
        assert reload['source_sha256']==report['artifacts']['main-menu.blend']
        assert reload['render_sha256']==sha(a.reload/'reload.png')
        assert reload['visible_objects']==26
    print('MAIN_MENU_VERIFIED',len(catalog['items']),'records',len(report['files']),'PNGs','10 GLB groups')


if __name__=='__main__':main()
