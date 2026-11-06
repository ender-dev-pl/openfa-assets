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
    assert len(catalog['items'])==292 and len(report['files'])==590
    for name,digest in report['source_hashes'].items():assert sha(source/name)==digest,'Source changed: '+name
    assert sha(source/'package_menu.py')==report['packager_sha256'],'Packager changed'
    for name,digest in report['artifacts'].items():assert sha(source/name)==digest,'Scene changed: '+name
    assert set(report['files'])=={p.relative_to(media).as_posix() for p in media.rglob('*.png')}
    for name,digest in report['files'].items():assert sha(media/name)==digest,'Payload changed: '+name
    assert len(report['proof'])==10
    assert report['panel_registration']=={'max_channel_error':0,'overlap_channel_error':0,'interior_gap_pixels':0}
    assert report['emblem']=={'connected_components':1,'nonmanifold_edges':0,'context_color_invariant':True}
    assert report['sphere_context_invariance'] is True
    assert catalog['registration']['base_anchor']==[320,0] and catalog['registration']['sphere_anchor']==[152,136]
    whole=Image.open(media/'native/layer-shared-console.png').convert('RGBA')
    left=Image.open(media/'native/layer-panel.png').convert('RGBA');right=Image.open(media/'native/layer-menu-base.png').convert('RGBA')
    overlap=ImageChops.difference(left.crop((320,0,415,480)),right.crop((0,0,95,480)))
    assert max(hi for lo,hi in overlap.getextrema())==0,'Panel overlap differs'
    joined=Image.new('RGBA',(640,480));joined.alpha_composite(left);joined.alpha_composite(right,(320,0))
    diff=ImageChops.difference(joined.crop((4,4,636,476)),whole.crop((4,4,636,476)))
    assert max(hi for lo,hi in diff.getextrema())==0,'Registered panel seam differs from common source'
    assert joined.getchannel('A').crop((4,4,636,476)).getextrema()==(255,255),'Panel gap'
    assert catalog['screen_neon_bindings']['main-menu']=='amber' and catalog['screen_neon_bindings']['preset-games']=='green'
    for state in catalog['states']:
        raw=Image.open(media/'native'/f'sphere-ruby-{state}.png').tobytes()
        for theme in catalog['themes']:assert Image.open(media/'native'/f'sphere-{theme}-{state}.png').tobytes()==raw,'Dome must remain invariant across contexts'
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
            if item['role'] in ['registered-console','registered-left-half']:
                assert im.getchannel('A').crop((4,4,im.width-4,im.height-4)).getextrema()==(255,255),path
            elif item['role']!='independent-layer':assert im.getchannel('A').getextrema()[0]==0,path
    if a.reload:
        reload=json.loads((a.reload/'reload.json').read_text())
        assert reload['source_sha256']==report['artifacts']['main-menu.blend']
        assert reload['render_sha256']==sha(a.reload/'reload.png')
        assert reload['visible_objects']==19
        assert reload['emblem_meshes']==1 and reload['emblem_nonmanifold_edges']==0
    print('MAIN_MENU_VERIFIED',len(catalog['items']),'records',len(report['files']),'PNGs','10 GLB groups')


if __name__=='__main__':main()
